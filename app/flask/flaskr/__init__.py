import os
from tkinter.ttk import Separator
from flask import Flask, request, jsonify, abort
from flask_session import Session
from flask_cors import CORS
import pandas as pd

from . import graph, forecast
from .extensions import mongo, cache
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

    Session(app)
    CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
    cache.init_app(app)
    mongo.init_app(app)

    @app.errorhandler(ValueError)
    def page_not_found(error):
        print("OOps")

        return "", 400

    @app.route("/data/upload", methods=["POST"])
    def upload_dataset():

        uploaded_file = request.files["upload"]
        separator = request.form.get("separator")
        print(separator)

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

        # collection.delete_one({"filename": "broadband_data_y.csv"})

        for i, dataset in enumerate(datasets):
            columns = parse_dataset(geo_column=None, dataset_id=i).columns.to_list()

            columns.append("N/A")

            avail_columns.append({"id": dataset["filename"], "columns": columns})

        return jsonify(avail_columns)

    @app.route("/data/reshape", methods=["POST"])
    def reshape_dataset():

        if mongo.db is None:
            return ("Database not available.", 500)

        payload = request.get_json()

        if payload is None:
            return ("Empty request.", 400)

        file_idx = payload["datasetIdx"]
        reshape_column = payload["reshapeColumn"]
        geo_column = payload["geoColumn"]

        columns = parse_dataset(
            geo_column=geo_column,
            dataset_id=file_idx,
            reshape_column=reshape_column,
        ).columns.to_list()

        time_columns = columns if reshape_column is None else ["Time"]
        feature_columns = [
            feature for feature in columns if feature not in ("Time", geo_column)
        ]

        available_columns = {
            "timeOptions": time_columns,
            "featureOptions": feature_columns,
        }

        return jsonify(available_columns)

    @app.route("/data/remove", methods=["DELETE"])
    def remove_dataset():

        if mongo.db is None:
            return ("Database not available.", 500)

        collection = mongo.db["collection_1"]

        payload = request.get_json()
        if payload is None:
            return ("Empty request.", 400)
        filename = payload["datasetId"]

        collection.delete_one({"filename": filename})

        print(f"Successfully removed dataset '{filename}'.")

        return ("", 204)

    return app
