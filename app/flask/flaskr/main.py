import io
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required
import gridfs
import time
import pycountry

from blueprints import graph, forecast
from auth.session import get_session
from extensions import mongo, cache, cors, session, jwt
from preprocessing.parse import parse_dataset
from preprocessing.dataset import DigitalTwinTimeSeries
from preprocessing.filter import infer_feature_options
from preprocessing.states import germany_federal

# create and configure the app
app = Flask(__name__, instance_relative_config=True)

app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/dt_society_datasets"
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config.from_mapping(SECRET_KEY="dev")

app.register_blueprint(graph.bp)
app.register_blueprint(forecast.bp)

session.init_app(app)
cache.init_app(app)
mongo.init_app(app)
cors.init_app(app)
jwt.init_app(app)


@app.route("/data/demo", methods=["GET"])
@jwt_required()
def get_demo_datasets():

    demo_data = {
        "Demo 0": (
            "arbeitslosenquote_eu.tsv",
            "https://raw.githubusercontent.com/Sultanow/dt_society/dev/app/flask/flaskr/static/demodata/arbeitslosenquote_eu.tsv",
        ),
        "Demo 1": (
            "bip_europa.tsv",
            "https://raw.githubusercontent.com/Sultanow/dt_society/dev/app/flask/flaskr/static/demodata/bip_eu.tsv",
        ),
    }
    if mongo.db is None:
        return ("Database not available.", 500)

    session = get_jwt_identity()

    bucket = gridfs.GridFS(mongo.db, session)

    for key in demo_data:
        df = DigitalTwinTimeSeries(demo_data[key][1], filename=demo_data[key][0])

        if bucket.exists({"filename": demo_data[key][0]}):
            print(f"Dataset '{demo_data[key][0]}' is already in database.")

        else:
            file_id = hash(demo_data[key][0] + str(time.time()))

            buffer = io.BytesIO()
            df.data.to_json(buffer, orient="records")
            buffer.seek(0)

            bucket.put(
                buffer,
                filename=demo_data[key][0],
                id=str(file_id),
                state="original",
            )

            print(f"Added '{demo_data[key][0]}' to database.")

    return ("", 204)


@app.route("/data/upload", methods=["POST"])
@jwt_required()
def upload_dataset():

    uploaded_file = request.files["upload"]

    file_name = (
        request.form["updatedFileName"]
        if request.form["updatedFileName"] != ""
        else uploaded_file.filename
    )

    if uploaded_file.filename != "":

        try:

            session = get_jwt_identity()

            df = DigitalTwinTimeSeries(
                uploaded_file.stream, filename=uploaded_file.filename
            )

            if mongo.db is not None and df is not None:
                bucket = gridfs.GridFS(mongo.db, session)

                file_id = hash(uploaded_file.filename + str(time.time()))

                buffer = io.BytesIO()
                df.data.to_json(buffer, orient="records")
                buffer.seek(0)

                bucket.put(
                    buffer,
                    filename=file_name,
                    id=str(file_id),
                    state="original",
                )
                print(f"Added '{uploaded_file.filename}' to database.")

        except Exception as e:
            print(e)
            return ("", 400)

    return ("", 204)


@app.route("/data/", methods=["GET"])
def get_data():
    if mongo.db is None:
        return ("Database not available.", 500)

    session, access_token = get_session()

    collection = mongo.db[session + ".files"]

    selection_options = []

    datasets = collection.find({})

    for dataset in datasets:
        df, _ = parse_dataset(
            geo_column=None,
            dataset_id=dataset["id"],
            session_id=session,
            use_preprocessed=False,
        )

        df = df.fillna(0)

        possible_features, geo_col, initialColumns = infer_feature_options(df)

        if geo_col is None:
            geo_col = "None"

        selection_options.append(
            {
                "id": dataset["id"],
                "possibleFeatures": possible_features,
                "geoSelected": geo_col,
                "name": dataset["filename"],
                "initialColumns": initialColumns,
            }
        )

    if access_token is not None:
        selection_options.append({"token": access_token})

    response_data = make_response(jsonify(selection_options))

    return response_data


@app.route("/data/update", methods=["POST"])
@app.route("/data/name", methods=["POST"])
@jwt_required()
def update_dataset():

    if mongo.db is None:
        return ("Database not available.", 500)

    session = get_jwt_identity()

    data = request.get_json()

    if data is None:
        return ("Empty request.", 400)

    file_id = data["datasetId"]

    collection = mongo.db[session + ".files"]

    dataset = collection.find_one({"id": file_id})

    if "name" in request.path:

        collection.update_one(
            {"id": file_id}, {"$set": {"filename": data["datasetName"]}}
        )

        return ("", 204)

    geo_column = data["geoColumn"]

    df, _ = parse_dataset(
        geo_column=geo_column,
        dataset_id=dataset["id"],
        session_id=session,
        use_preprocessed=False,
    )

    df = df.fillna(0)

    possible_features, _, initialColumns = infer_feature_options(df)

    response_data = {
        "id": dataset["id"],
        "possibleFeatures": possible_features,
        "geoSelected": geo_column,
        "name": data["datasetName"],
        "initialColumns": initialColumns,
    }

    return response_data


@app.route("/data/reshape", methods=["POST"])
@jwt_required()
def reshape_dataset():

    if mongo.db is None:
        return ("Database not available.", 500)

    data = request.get_json()

    if data is None:
        return ("Empty request.", 400)

    file_id = data["datasetId"]
    geo_column = data["geoColumn"] if data["geoColumn"] != "None" else None
    feature_selected = data["featureSelected"]

    reshape_column = data["reshapeSelected"] if "reshapeSelected" in data else None

    session = get_jwt_identity()

    bucket = gridfs.GridFS(mongo.db, session)

    df, reshape_column = parse_dataset(
        geo_column=geo_column,
        dataset_id=file_id,
        reshape_column=reshape_column,
        selected_feature=feature_selected,
        session_id=session,
        use_preprocessed=False,
    )

    processed = mongo.db[session + ".files"].find_one(
        {"id": file_id, "state": "processed"}
    )

    file_name = mongo.db[session + ".files"].find_one(
        {"id": file_id, "state": "original"}
    )["filename"]

    if processed is not None:
        print("Updating processed state of: \n", processed)
        bucket.delete(processed["_id"])
    else:
        print("File does not exist")

    buffer = io.BytesIO()
    df.to_json(buffer, orient="records")
    buffer.seek(0)

    bucket.put(
        buffer,
        filename=file_name,
        id=str(file_id),
        state="processed",
    )

    feature_columns = [
        feature
        for feature in df.columns.to_list()
        if feature not in ("Time", geo_column)
    ]

    response_data = {}

    response_data["features"] = feature_columns
    if geo_column is not None:
        countries = df[geo_column].unique().tolist()
        if set(countries).isdisjoint(germany_federal.values()):
            countries = map(
                lambda country: pycountry.countries.get(alpha_3=country).name, countries
            )
        else:
            countries = map(
                lambda country: pycountry.subdivisions.get(code=country).name,
                countries,
            )
        response_data["countries"] = list(countries)
    response_data["reshape_column"] = reshape_column

    return response_data


@app.route("/data/", methods=["DELETE"])
@jwt_required()
def remove_dataset():

    data = request.get_json()

    if mongo.db is None:
        return ("Database not available.", 500)

    if data is None:
        return ("Empty request.", 400)

    session = get_jwt_identity()
    bucket = gridfs.GridFS(mongo.db, session)

    dataset_id = data["datasetId"]

    file_to_delete_processed = mongo.db[session + ".files"].find_one(
        {"id": dataset_id, "state": "processed"}
    )

    file_to_delete_original = mongo.db[session + ".files"].find_one(
        {"id": dataset_id, "state": "original"}
    )

    if file_to_delete_processed is not None:
        bucket.delete(file_to_delete_processed["_id"])

    bucket.delete(file_to_delete_original["_id"])

    print(f"Successfully removed dataset '{dataset_id}'.")

    return ("", 204)


if __name__ == "__main__":
    app.run(debug=True)
