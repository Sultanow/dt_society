import json
import plotly
import pandas as pd

from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
)
from .forecasting.models import (
    var_fit_and_predict_multi,
    hw_es_fit_and_predict_multi,
    prophet_fit_and_predict_n,
)
from .plots.plots import (
    create_var_forecast_plot_multi,
    create_multivariate_forecast_prophet,
)
from .preprocessing.parse import parse_dataset, merge_dataframes_multi
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import mongo

bp = Blueprint("forecast", __name__, url_prefix="/forecast")


@bp.route("/var", methods=["POST"])
def forecastVAR():
    data = request.get_json()

    print(data)

    datasets = data["datasets"]

    if datasets is None:
        return ("Empty request", 400)

    time_columns = []
    feature_columns = []
    filtered_dfs = []

    collection = mongo.db["collection_1"]

    d = {}
    for dataset in datasets:

        df = parse_dataset(
            geo_column=dataset["geoSelected"],
            dataset_id=dataset["id"],
            reshape_column=dataset["reshapeSelected"]
            if dataset["reshapeSelected"] != "N/A"
            else None,
        )
        filtered_df = df[df[dataset["geoSelected"]] == data["country"]][
            [dataset["timeSelected"], dataset["featureSelected"]]
        ]

        filtered_df[dataset["timeSelected"]] = pd.to_datetime(
            filtered_df[dataset["timeSelected"]].astype("str")
        )

        filtered_dfs.append(filtered_df)

        time_columns.append(dataset["timeSelected"])
        feature_columns.append(dataset["featureSelected"])

    forecast = var_fit_and_predict_multi(
        filtered_dfs,
        time_columns,
        feature_columns,
        max_lags=data["maxLags"],
        periods=data["periods"],
        frequency=data["frequency"],
    )

    # fig = create_var_forecast_plot_multi(forecast, feature_col, time_col[-1], 5)

    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # return render_template("figure.html", graphJSON=graphJSON)
    # return jsonify(graphJSON)

    d["x"] = forecast[time_columns[-1]].dt.strftime("%Y-%m-%d").tolist()
    for feature in feature_columns:
        d[feature] = forecast[feature].tolist()

    print(d)
    return d


@bp.route("hwes", methods=["GET"])
def forecastHWES():
    geo_col = request.args.getlist("geo")
    time_col = request.args.getlist("x")
    feature_col = request.args.getlist("y")
    reshape_col = request.args.getlist("rshp")

    filtered_dfs = []
    collection = mongo.db["collection_1"]
    for i in range(collection.count_documents({})):
        df = parse_dataset(
            geo_column=geo_col[i],
            dataset_id=i,
            reshape_column=reshape_col[i],
        )
        filtered_df = df[df[geo_col[i]] == "AUT"][[time_col[i], feature_col[i]]]

        filtered_dfs.append(filtered_df)

    forecast = hw_es_fit_and_predict_multi(
        filtered_dfs,
        time_col,
        feature_col,
        alpha=0.4,
        periods=5,
        frequency="Yearly",
    )

    fig = create_var_forecast_plot_multi(forecast, feature_col, time_col[-1], 5)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("figure.html", graphJSON=graphJSON)


@bp.route("prophet", methods=["GET", "POST"])
def forecastProphet():
    geo_col = request.args.getlist("geo")
    time_col = request.args.getlist("x")
    feature_col = request.args.getlist("y")
    reshape_col = request.args.getlist("rshp")

    filtered_dfs = []
    collection = mongo.db["collection_1"]
    for i in range(collection.count_documents({})):
        df = parse_dataset(
            geo_column=geo_col[i],
            dataset_id=i,
            reshape_column=reshape_col[i],
        )
        filtered_df = df[df[geo_col[i]] == "AUT"][[time_col[i], feature_col[i]]]

        filtered_dfs.append(filtered_df)

    scenarios_data = [[45000, 46000, 47000]]

    forecast, merged_df, future_df, y_feature = prophet_fit_and_predict_n(
        filtered_dfs,
        time_col,
        feature_col,
        scenarios=scenarios_data,
        frequency="Yearly",
        y_feature_index=0,
    )

    fig = create_multivariate_forecast_prophet(
        forecast, merged_df, future_df, y_feature, feature_col
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("figure.html", graphJSON=graphJSON)
