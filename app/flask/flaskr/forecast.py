import pandas as pd
import pycountry

from flask import (
    Blueprint,
    request,
)
from flask_jwt_extended import get_jwt_identity, jwt_required
from .forecasting.models import (
    var_fit_and_predict_multi,
    hw_es_fit_and_predict_multi,
    prophet_fit_and_predict_n,
)
from .preprocessing.parse import parse_dataset


bp = Blueprint("forecast", __name__, url_prefix="/forecast")


@bp.route("/multivariate/<model>", methods=["POST"])
@jwt_required()
def forecastVAR(model):
    if model not in ("var", "hwes"):
        return ("Unknown model.", 400)

    data = request.get_json()

    datasets = data["datasets"]
    selected_country = pycountry.countries.get(name=data["country"]).alpha_3

    if datasets is None:
        return ("Empty request", 400)

    time_columns = []
    feature_columns = []
    filtered_dfs = []
    frequencies = []

    session = get_jwt_identity()

    response_data = {}
    for dataset in datasets:

        reshape_selected = (
            dataset["reshapeSelected"] if dataset["reshapeSelected"] != "N/A" else None
        )
        geo_selected = dataset["geoSelected"]
        dataset_id = dataset["id"] if dataset["geoSelected"] != "None" else None
        time_selected = dataset["timeSelected"]
        feature_selected = dataset["featureSelected"]

        df = parse_dataset(
            geo_column=geo_selected,
            dataset_id=dataset_id,
            reshape_column=reshape_selected,
            session_id=session,
            processed_state=True,
        )
        if geo_selected is None:
            filtered_df = df
            filtered_df[time_selected] = pd.to_datetime(
                filtered_df[time_selected].astype("str")
            )

            freq = pd.infer_freq(filtered_df[time_selected])

            filtered_dfs.append(filtered_df)
            frequencies.append(freq)
            time_columns.append(time_selected)
            feature_columns.append(feature_selected)

        elif geo_selected is not None and selected_country in df[geo_selected].unique():
            filtered_df = df[df[geo_selected] == selected_country][
                [time_selected, feature_selected]
            ]

            filtered_df[time_selected] = pd.to_datetime(
                filtered_df[time_selected].astype("str")
            )

            freq = pd.infer_freq(filtered_df[time_selected])

            filtered_dfs.append(filtered_df)
            frequencies.append(freq)
            time_columns.append(time_selected)
            feature_columns.append(feature_selected)

    if len(set(frequencies)) != 1:
        print("Frequencies of datasets do not match.")
        return ("Frequencies do not match.", 400)

    if model == "var":
        forecast = var_fit_and_predict_multi(
            filtered_dfs,
            time_columns,
            feature_columns,
            max_lags=data["maxLags"],
            periods=data["periods"],
            frequency=freq,
        )
    elif model == "hwes":
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
@jwt_required()
def forecastProphet():
    data = request.get_json()

    datasets = data["datasets"]
    selected_country = pycountry.countries.get(name=data["country"]).alpha_3
    dependent_df = data["dependentDataset"]
    scenarios = data["scenarios"]

    if datasets is None:
        return ("Empty request", 400)

    time_columns = []
    feature_columns = []
    filtered_dfs = []
    frequencies = []

    y_feature_index = None

    session = get_jwt_identity()

    for i, dataset in enumerate(datasets):
        if dataset["id"] in scenarios.keys():
            reshape_selected = (
                dataset["reshapeSelected"]
                if dataset["reshapeSelected"] != "N/A"
                else None
            )
            geo_selected = (
                dataset["geoSelected"] if dataset["geoSelected"] != "None" else None
            )
            dataset_id = dataset["id"]
            time_selected = dataset["timeSelected"]
            feature_selected = dataset["featureSelected"]

            df = parse_dataset(
                geo_column=geo_selected,
                dataset_id=dataset_id,
                reshape_column=reshape_selected,
                session_id=session,
                processed_state=True,
            )
            if geo_selected is not None:
                filtered_df = df[df[geo_selected] == selected_country][
                    [time_selected, feature_selected]
                ]
            else:
                filtered_df = df[[time_selected, feature_selected]]

            filtered_df[time_selected] = pd.to_datetime(
                filtered_df[time_selected].astype("str")
            )

            freq = pd.infer_freq(filtered_df[time_selected])

            filtered_dfs.append(filtered_df)
            frequencies.append(freq)
            time_columns.append(time_selected)
            feature_columns.append(feature_selected)

            if dataset_id == dependent_df:
                y_feature_index = i

    scenarios_data = [
        [float(x) for x in scenarios[dataset] if x is not None and len(x) != 0]
        for dataset in data["scenarios"]
        if dataset != dependent_df
    ]

    if len(set(frequencies)) != 1:
        print("Frequencies of datasets do not match.")
        return ("Frequencies do not match.", 400)

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
