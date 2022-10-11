import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from flask_cors import CORS
import pandas as pd

from . import graph, forecast
from .extensions import mongo, cache


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Upload folder
    UPLOAD_FOLDER = "flaskr/static/files"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

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
    CORS(app)
    cache.init_app(app)
    mongo.init_app(app)

    @app.route("/")
    def index():
        collection = mongo.db["collection_1"]
        data = collection.find({})

        return render_template("db_data.html", files=data)

    @app.route("/", methods=["POST"])
    def uploadFiles():

        uploaded_file = request.files["file"]
        if uploaded_file.filename != "":

            df = pd.read_table(uploaded_file.stream)

            # create collections for each session
            collection = mongo.db["collection_1"]

            if collection.count_documents({"filename": uploaded_file.filename}) > 0:
                print("already in db")
            else:
                collection.insert_one(
                    {"filename": uploaded_file.filename, "data": df.to_dict("records")}
                )
                print("added to db")

        return redirect(url_for("index"))
        # return render_template("db_data.html", files=data)

    return app