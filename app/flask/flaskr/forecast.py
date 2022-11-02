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

    d["x"] = forecast[time_columns[-1]].dt.strftime("%Y-%m-%d").tolist()
    for feature in feature_columns:
        d[feature] = forecast[feature].tolist()

    print(d)
    return d


@bp.route("hwes", methods=["POST"])
def forecastHWES():
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

    forecast = hw_es_fit_and_predict_multi(
        filtered_dfs,
        time_columns,
        feature_columns,
        alpha=data["maxLags"],
        periods=data["periods"],
        frequency=data["frequency"],
    )

    d["x"] = forecast[time_columns[-1]].dt.strftime("%Y-%m-%d").tolist()
    for feature in feature_columns:
        d[feature] = forecast[feature].tolist()

    print(d)
    return d


@bp.route("prophet", methods=["POST"])
def forecastProphet():
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

    scenarios_data = [[45000, 46000, 47000], [21.2, 30.3, 43.4]]

    forecast, merged_df, future_df, y_feature = prophet_fit_and_predict_n(
        filtered_dfs,
        time_columns,
        feature_columns,
        scenarios=scenarios_data,
        frequency="Yearly",
        y_feature_index=0,
    )

    # fig = create_multivariate_forecast_prophet(
    #     forecast, merged_df, future_df, y_feature, feature_col
    # )

    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    print(forecast)

    return ""
