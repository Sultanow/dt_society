import os
from flask import Flask, request, jsonify

from . import graph, forecast
from .extensions import mongo, cache, cors, session
from .preprocessing.parse import parse_dataset
from .preprocessing.dataset import DigitalTwinTimeSeries


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

    @app.route("/data/demo", methods=["GET"])
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

        for key in demo_data:
            df = DigitalTwinTimeSeries(demo_data[key][1], sep="\t")

            collection = mongo.db["collection_1"]

            if collection.count_documents({"filename": demo_data[key][0]}) > 0:
                print(f"Dataset '{demo_data[key][0]}' is already in database.")

            else:
                collection.insert_one(
                    {
                        "filename": demo_data[key][0],
                        "data": df.data.to_dict("records"),
                    }
                )
                print(f"Added '{demo_data[key][0]}' to database.")

        return ("", 204)

    @app.route("/data/upload", methods=["POST"])
    def upload_dataset():

        uploaded_file = request.files["upload"]
        separator = request.form.get("separator")

        if uploaded_file.filename != "":

            try:
                df = DigitalTwinTimeSeries(uploaded_file.stream, sep=separator)

                if mongo.db is not None and df is not None:
                    collection = mongo.db["collection_1"]

                    if (
                        collection.count_documents({"filename": uploaded_file.filename})
                        > 0
                    ):
                        print(
                            f"Dataset '{uploaded_file.filename}' is already in database."
                        )

                    else:
                        collection.insert_one(
                            {
                                "filename": uploaded_file.filename,
                                "data": df.data.to_dict("records"),
                            }
                        )
                        print(f"Added '{uploaded_file.filename}' to database.")
            except Exception as e:

                return ("", 400)

        return ("", 204)

    @app.route("/data/", methods=["GET"])
    def get_datasets():

        if mongo.db is None:
            return ("Database not available.", 500)

        collection = mongo.db["collection_1"]

        avail_columns = []

        datasets = collection.find({})

        for i, dataset in enumerate(datasets):
            columns = parse_dataset(geo_column=None, dataset_id=i).columns.to_list()

            columns.insert(0, "N/A")

            avail_columns.append({"id": dataset["filename"], "columns": columns})

        print(avail_columns)

        return jsonify(avail_columns)

    @app.route("/data/reshape", methods=["POST"])
    def reshape_dataset():

        if mongo.db is None:
            return ("Database not available.", 500)

        data = request.get_json()

        if data is None:
            return ("Empty request.", 400)

        file_id = data["datasetId"]
        reshape_column = data["reshapeColumn"]
        geo_column = data["geoColumn"]

        df = parse_dataset(
            geo_column=geo_column,
            dataset_id=file_id,
            reshape_column=reshape_column,
        )

        time_columns = df.columns.to_list() if reshape_column is None else ["Time"]
        feature_columns = [
            feature
            for feature in df.columns.to_list()
            if feature not in ("Time", geo_column)
        ]

        countries = df[geo_column].unique().tolist()

        available_columns = {
            "timeOptions": time_columns,
            "featureOptions": feature_columns,
            "countryOptions": countries,
        }

        return jsonify(available_columns)

    @app.route("/data/remove", methods=["DELETE"])
    def remove_dataset():

        if mongo.db is None:
            return ("Database not available.", 500)

        collection = mongo.db["collection_1"]

        data = request.get_json()
        if data is None:
            return ("Empty request.", 400)
        filename = data["datasetId"]

        collection.delete_one({"filename": filename})

        print(f"Successfully removed dataset '{filename}'.")

        return ("", 204)

    return app
