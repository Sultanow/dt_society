import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session

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
    cache.init_app(app)
    mongo.init_app(app)

    @app.route("/")
    def index():
        return render_template("data.html")

    @app.route("/", methods=["POST"])
    def uploadFiles():

        uploaded_file = request.files["file"]
        if uploaded_file.filename != "":
            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"], uploaded_file.filename
            )

            uploaded_file.save(file_path)

            if "files" not in session.keys():
                session["files"] = [file_path]

            elif file_path not in session["files"]:
                session["files"].append(file_path)

            data_collection = mongo.db.datasets

        return redirect(url_for("index"))

    return app
