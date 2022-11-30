import os
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required
import time

from . import graph, forecast
from .auth.session import get_session
from .extensions import mongo, cache, cors, session, jwt
from .preprocessing.parse import parse_dataset
from .preprocessing.dataset import DigitalTwinTimeSeries
from .preprocessing.filter import infer_feature_options


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Upload folder
    UPLOAD_FOLDER = "flaskr/static/files"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["PROPAGATE_EXCEPTIONS"] = True

    app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/dt_society_datasets"

    app.config["JWT_SECRET_KEY"] = "super-secret"

    app.register_blueprint(graph.bp)
    app.register_blueprint(forecast.bp)

    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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
                "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tipsun20.tsv.gz",
            ),
            "Demo 1": (
                "bip_europa.tsv",
                "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tec00001.tsv.gz",
            ),
        }
        if mongo.db is None:
            return ("Database not available.", 500)

        session = get_jwt_identity()

        collection = mongo.db[session]

        for key in demo_data:
            df = DigitalTwinTimeSeries(demo_data[key][1], filename=demo_data[key][0])

            if collection.count_documents({"name": demo_data[key][0]}) > 0:
                print(f"Dataset '{demo_data[key][0]}' is already in database.")

            else:
                file_id = hash(demo_data[key][0] + str(time.time()))
                collection.insert_one(
                    {
                        "name": demo_data[key][0],
                        "data": df.data.to_dict("records"),
                        "id": str(file_id),
                    }
                )
                print(f"Added '{demo_data[key][0]}' to database.")

        return ("", 204)

    @app.route("/data/upload", methods=["POST"])
    @jwt_required()
    def upload_dataset():

        uploaded_file = request.files["upload"]

        if uploaded_file.filename != "":

            try:

                session = get_jwt_identity()

                df = DigitalTwinTimeSeries(
                    uploaded_file.stream, filename=uploaded_file.filename
                )

                if mongo.db is not None and df is not None:
                    collection = mongo.db[session]

                    if collection.count_documents({"name": uploaded_file.filename}) > 0:
                        print(
                            f"Dataset '{uploaded_file.filename}' is already in database."
                        )

                    else:
                        file_id = hash(uploaded_file.filename + str(time.time()))
                        collection.insert_one(
                            {
                                "name": uploaded_file.filename,
                                "data": df.data.to_dict("records"),
                                "id": str(file_id),
                            }
                        )
                        print(f"Added '{uploaded_file.filename}' to database.")
            except Exception as e:
                print(e)
                return ("", 400)

        return ("", 204)

    @app.route("/data/find_geo", methods=["GET"])
    def get_geo():
        if mongo.db is None:
            return ("Database not available.", 500)

        session, access_token = get_session()

        collection = mongo.db[session]

        selection_options = []

        datasets = collection.find({})

        for i, dataset in enumerate(datasets):
            df, _ = parse_dataset(
                geo_column=None, dataset_id=dataset["id"], session_id=session
            )

            df = df.fillna(0)

            possible_features, geo_col = infer_feature_options(df)

            if geo_col is None:
                geo_col = "None"

            selection_options.append(
                {
                    "id": dataset["id"],
                    "possibleFeatures": possible_features,
                    "geoSelected": geo_col,
                    "name": dataset["name"],
                }
            )

        if access_token is not None:
            selection_options.append({"token": access_token})

        response_data = make_response(jsonify(selection_options))

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

        session = get_jwt_identity()

        df, reshape_column = parse_dataset(
            geo_column=geo_column,
            dataset_id=file_id,
            selected_feature=feature_selected,
            session_id=session,
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
            response_data["countries"] = countries
        response_data["reshape_column"] = reshape_column

        return response_data

    @app.route("/data/remove", methods=["DELETE"])
    @jwt_required()
    def remove_dataset():

        if mongo.db is None:
            return ("Database not available.", 500)

        session = get_jwt_identity()

        collection = mongo.db[session]

        data = request.get_json()
        if data is None:
            return ("Empty request.", 400)
        dataset_id = data["datasetId"]

        collection.delete_one({"id": dataset_id})

        print(f"Successfully removed dataset '{dataset_id}'.")

        return ("", 204)

    @app.route("/data/reshapecheck", methods=["POST"])
    @jwt_required()
    def check_for_reshape():

        session = get_jwt_identity()
        if mongo.db is None:
            return ("Database not available.", 500)

        data = request.get_json()

        if data is None:
            return ("Empty request.", 400)

        file_id = data["datasetId"]
        geo_column = data["geoColumn"] if data["geoColumn"] != "None" else None
        feature_selected = data["featureSelected"]

        dataframe = parse_dataset(
            geo_column=geo_column, dataset_id=file_id, session_id=session
        )

        features_in_columns = dataframe.columns.to_list()

        response_data = None

        for feature in features_in_columns:
            if feature_selected in dataframe[feature].unique().tolist():
                response_data = feature

        return jsonify(response_data)

    return app
