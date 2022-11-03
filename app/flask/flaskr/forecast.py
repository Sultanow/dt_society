import pandas as pd

from flask import (
    Blueprint,
    request,
)
from .forecasting.models import (
    var_fit_and_predict_multi,
    hw_es_fit_and_predict_multi,
    prophet_fit_and_predict_n,
)
from .preprocessing.parse import parse_dataset

from .extensions import mongo

bp = Blueprint("forecast", __name__, url_prefix="/forecast")


@bp.route("/var", methods=["POST"])
def forecastVAR():
    data = request.get_json()

    datasets = data["datasets"]

    if datasets is None:
        return ("Empty request", 400)

    time_columns = []
    feature_columns = []
    filtered_dfs = []

    response_data = {}
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

    response_data["x"] = forecast[time_columns[-1]].dt.strftime("%Y-%m-%d").tolist()
    for feature in feature_columns:
        response_data[feature] = forecast[feature].tolist()

    return response_data


@bp.route("hwes", methods=["POST"])
def forecastHWES():
    data = request.get_json()

    datasets = data["datasets"]

    if datasets is None:
        return ("Empty request", 400)

    time_columns = []
    feature_columns = []
    filtered_dfs = []

    response_data = {}
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

    response_data["x"] = forecast[time_columns[-1]].dt.strftime("%Y-%m-%d").tolist()
    for feature in feature_columns:
        response_data[feature] = forecast[feature].tolist()

    return response_data


@bp.route("prophet", methods=["POST"])
def forecastProphet():
    data = request.get_json()

    datasets = data["datasets"]

    dependent_df = data["dependentDataset"]

    if datasets is None:
        return ("Empty request", 400)

    time_columns = []
    feature_columns = []
    filtered_dfs = []

    y_feature_index = None

    for i, dataset in enumerate(datasets):

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

        if dataset["id"] == dependent_df:
            y_feature_index = i

    scenarios_data = [
        [float(x) if x is not None else x for x in data["scenarios"][dataset]]
        for dataset in data["scenarios"]
        if dataset != dependent_df
    ]

    response_data = {}
    response_data["future"] = {}
    response_data["merge"] = {}
    response_data["forecast"] = {}
    forecast, merged_df, future_df, y_feature = prophet_fit_and_predict_n(
        filtered_dfs,
        time_columns,
        feature_columns,
        scenarios=scenarios_data,
        frequency=data["frequency"],
        y_feature_index=y_feature_index,
    )

    for df_key, df in zip(response_data, (future_df, merged_df, forecast)):
        for column in df.columns.tolist():
            if column == "ds":
                response_data[df_key]["x"] = (
                    df[column].dt.strftime("%Y-%m-%d").to_list()
                )
            elif column == "y":

                response_data[df_key][y_feature] = df[column].to_list()
            else:
                response_data[df_key][column] = df[column].to_list()

    return response_data
