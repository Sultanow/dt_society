import os
import pycountry
import uuid
import datetime
import time
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import create_access_token
from flask_jwt_extended import (
    get_jwt_identity,
    get_current_user,
    decode_token,
    verify_jwt_in_request,
)
from flask_jwt_extended import jwt_required
from dateutil import parser
from jwt import ExpiredSignatureError
from . import graph, forecast
from .extensions import mongo, cache, cors, session, jwt
from .preprocessing.parse import parse_dataset
from .preprocessing.dataset import DigitalTwinTimeSeries
from .preprocessing.states import germany_federal
from .preprocessing.filter import find_geo_column, is_datetime, infer_feature_options


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

        token = request.headers.get("Authorization").split(sep=" ")[1]

        decoded_token = decode_token(token, allow_expired=True)

        session = decoded_token["sub"]

        collection = mongo.db[session]

        for key in demo_data:
            df = DigitalTwinTimeSeries(demo_data[key][1], filename=demo_data[key][0])

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

        if uploaded_file.filename != "":

            try:
                token = request.headers.get("Authorization").split(sep=" ")[1]

                decoded_token = decode_token(token, allow_expired=True)

                session = decoded_token["sub"]

                df = DigitalTwinTimeSeries(
                    uploaded_file.stream, filename=uploaded_file.filename
                )

                if mongo.db is not None and df is not None:
                    collection = mongo.db[session]

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
                print(e)
                return ("", 400)

        return ("", 204)

    @app.route("/data/find_geo", methods=["GET"])
    def get_geo():
        if mongo.db is None:
            return ("Database not available.", 500)

        access_token = None

        session = None

        # mongo.db.drop_collection("collection_1")

        try:

            token = request.headers.get("Authorization").split(sep=" ")[1]

            decoded_token = decode_token(token, allow_expired=True)

            session = decoded_token["sub"]

            if decoded_token["exp"] < time.time():
                raise ExpiredSignatureError

            collection = mongo.db[session]

        except:
            print("No valid token found. \n")

            if session is not None:
                mongo.db.drop_collection(session)

            expiration = datetime.timedelta(minutes=5)
            new_session = str(uuid.uuid1())
            access_token = create_access_token(
                identity=new_session, expires_delta=expiration
            )
            print("New Token created for session.\n")

            collection = mongo.db[new_session]

        selection_options = []

        datasets = collection.find({})

        for i, dataset in enumerate(datasets):
            df, _ = parse_dataset(geo_column=None, dataset_id=i)

            df = df.fillna(0)

            possible_features, geo_col = infer_feature_options(df)

            selection_options.append(
                {
                    "id": dataset["filename"],
                    "possibleFeatures": possible_features,
                    "geoSelected": geo_col,
                }
            )

        if access_token is not None:
            selection_options.append({"token": access_token})

        response_data = make_response(jsonify(selection_options))

        return response_data

    @app.route("/data/reshape", methods=["POST"])
    def reshape_dataset():

        if mongo.db is None:
            return ("Database not available.", 500)

        data = request.get_json()

        if data is None:
            return ("Empty request.", 400)

        file_id = data["datasetId"]
        # reshape_column = data["reshapeColumn"]
        geo_column = data["geoColumn"]
        feature_selected = data["featureSelected"]

        df, reshape_column = parse_dataset(
            geo_column=geo_column,
            dataset_id=file_id,
            selected_feature=feature_selected
            # reshape_column=reshape_column,
        )

        feature_columns = [
            feature
            for feature in df.columns.to_list()
            if feature not in ("Time", geo_column)
        ]

        countries = df[geo_column].unique().tolist()

        response_data = {}

        response_data["features"] = feature_columns
        response_data["countries"] = countries
        response_data["reshape_column"] = reshape_column

        return response_data

    @app.route("/data/remove", methods=["DELETE"])
    def remove_dataset():

        if mongo.db is None:
            return ("Database not available.", 500)

        token = request.headers.get("Authorization").split(sep=" ")[1]

        decoded_token = decode_token(token, allow_expired=True)

        session = decoded_token["sub"]

        collection = mongo.db[session]

        data = request.get_json()
        if data is None:
            return ("Empty request.", 400)
        filename = data["datasetId"]

        collection.delete_one({"filename": filename})

        print(f"Successfully removed dataset '{filename}'.")

        return ("", 204)

    @app.route("/data/reshapecheck", methods=["POST"])
    def check_for_reshape():
        if mongo.db is None:
            return ("Database not available.", 500)

        data = request.get_json()

        if data is None:
            return ("Empty request.", 400)

        file_id = data["datasetId"]
        geo_column = data["geoColumn"]
        feature_selected = data["featureSelected"]

        dataframe = parse_dataset(geo_column=geo_column, dataset_id=file_id)

        features_in_columns = dataframe.columns.to_list()

        response_data = None

        for feature in features_in_columns:
            if feature_selected in dataframe[feature].unique().tolist():
                response_data = feature

        return jsonify(response_data)

    return app
