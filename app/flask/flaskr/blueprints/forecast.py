from typing import List
import pandas as pd
import pycountry

from itertools import repeat
from multiprocessing import Pool

from flask import (
    Blueprint,
    request,
)
from flask_jwt_extended import get_jwt_identity, jwt_required
from forecasting.models import (
    var_fit_and_predict_multi,
    hw_es_fit_and_predict_multi,
    prophet_fit_and_predict_n,
    prophet_fit_and_predict,
)
from preprocessing.parse import parse_dataset, make_unique_features


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
        varFeatures_selected = (
            dataset["varFeaturesSelected"]
            if "varFeaturesSelected" in dataset
            else [dataset["featureSelected"]]
        )

        geo_selected = dataset["geoSelected"]
        dataset_id = dataset["id"] if dataset["geoSelected"] != "None" else None
        time_selected = dataset["timeSelected"]
        reshape_selected = (
            dataset["reshapeSelected"] if dataset["reshapeSelected"] != "N/A" else None
        )

        for feature in varFeatures_selected:

            feature_selected = feature

            df, _ = parse_dataset(
                geo_column=geo_selected,
                dataset_id=dataset_id,
                reshape_column=reshape_selected,
                session_id=session,
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

            elif (
                geo_selected is not None
                and selected_country in df[geo_selected].unique()
            ):
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

    filtered_dfs, feature_columns = make_unique_features(filtered_dfs, feature_columns)

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
            frequency=freq,
        )

    response_data["x"] = forecast[time_columns[-1]].dt.strftime("%Y-%m-%d").tolist()
    for feature in feature_columns:
        response_data[feature] = forecast[feature].tolist()

    future = pd.date_range(
        start=response_data["x"][-data["periods"] - 1],
        freq=freq,
        periods=40,
    )

    response_data["future"] = future.strftime("%Y-%m-%d").tolist()

    return response_data


@bp.route("prophet", methods=["POST"])
@jwt_required()
def forecastProphet():
    data = request.get_json()

    predictions = data["predictions"] if "predictions" in data else None
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

            df, _ = parse_dataset(
                geo_column=geo_selected,
                dataset_id=dataset_id,
                reshape_column=reshape_selected,
                session_id=session,
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

    if predictions is None:
        scenarios_data = [
            [
                float(x)
                for x in scenarios[dataset]["data"]
                if x is not None and len(x) != 0
            ]
            for dataset in data["scenarios"]
            if dataset != dependent_df
        ]
    else:

        scenarios_data = []
        for i, dataset in enumerate(datasets):
            if datasets[i]["id"] != dependent_df:
                forecast, _ = prophet_fit_and_predict(
                    filtered_dfs[i],
                    time_columns[i],
                    feature_columns[i],
                    predictions,
                    frequencies[i],
                )
                scenarios_data.append(forecast["yhat"])

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
        frequency=set(frequencies).pop(),
        y_feature_index=y_feature_index,
    )
    time_range = []

    for df_key, df in zip(response_data, (future_df, merged_df, forecast)):
        for column in df.columns.tolist():
            if column == "ds":
                response_data[df_key]["x"] = (
                    df[column].dt.strftime("%Y-%m-%d").to_list()
                )

                if len(df[column].dt.strftime("%Y-%m-%d").to_list()) > 2:
                    freq = pd.infer_freq(df[column].dt.strftime("%Y-%m-%d").to_list())

                    time_range = pd.date_range(
                        start=df[column].dt.strftime("%Y-%m-%d").to_list()[-1],
                        freq=freq,
                        periods=40,
                    ).strftime("%Y-%m-%d")
            elif column == "y":

                response_data[df_key][y_feature] = df[column].to_list()
            else:
                response_data[df_key][column] = df[column].to_list()

    response_data["slidervalues"] = time_range.to_list()
    return response_data


@bp.route("map/<model>", methods=["POST"])
@jwt_required()
def var_forecast_map(model):

    data = request.get_json()

    datasets = data["datasets"]

    if datasets is None:
        return ("Empty request", 400)

    time_columns = []
    feature_columns = []
    filtered_dfs = []
    frequencies = []
    countries = []

    session = get_jwt_identity()

    response_data = {}
    for dataset in datasets:

        varmapFeatures_selected = (
            dataset["varmapFeaturesSelected"]
            if "varmapFeaturesSelected" in dataset
            else [dataset["featureSelected"]]
        )

        geo_selected = dataset["geoSelected"]
        dataset_id = dataset["id"] if dataset["geoSelected"] != "None" else None
        time_selected = dataset["timeSelected"]

        reshape_selected = (
            dataset["reshapeSelected"] if dataset["reshapeSelected"] != "N/A" else None
        )

        df, _ = parse_dataset(
            geo_column=geo_selected,
            dataset_id=dataset_id,
            reshape_column=reshape_selected,
            session_id=session,
        )

        filtered_df = df.dropna()

        filtered_df[time_selected] = pd.to_datetime(
            filtered_df[time_selected].astype("str")
        )

        filtered_dfs.append(filtered_df)

        countries.append(set(filtered_df[geo_selected].unique()))

    filtered_dfs_by_country = []

    countries = list(set.intersection(*countries))

    for country in countries:
        dfs = []
        features = []
        time = []
        k = 0
        for i, df in enumerate(datasets):
            geo_col = df["geoSelected"]
            time_selected = df["timeSelected"]

            varmapFeatures_selected = (
                df["varmapFeaturesSelected"]
                if "varmapFeaturesSelected" in df
                else [df["featureSelected"]]
            )
            for feature in varmapFeatures_selected:
                feature_selected = feature

                if country not in filtered_dfs[i][geo_col].unique():
                    break

                dfs.append(
                    filtered_dfs[i][filtered_dfs[i][geo_col] == country][
                        [time_selected, feature_selected]
                    ]
                )

                freq = pd.infer_freq(dfs[k][time_selected])
                frequencies.append(freq)

                time.append(time_selected)
                features.append(feature_selected)
                k = k + 1
        if len(dfs) > 1:
            filtered_dfs_by_country.append(dfs)
            feature_columns.append(features)
            time_columns.append(time)

    n_countries = len(countries)

    frequencies = [
        frequency for frequency in list(set(frequencies)) if frequency is not None
    ]

    pool = Pool(4)
    if model == "var":
        result: List[pd.DataFrame] = pool.starmap(
            var_fit_and_predict_multi,
            zip(
                filtered_dfs_by_country,
                time_columns,
                feature_columns,
                repeat(data["maxLags"], n_countries),
                repeat(data["periods"], n_countries),
                repeat(frequencies[0], n_countries),
            ),
        )
    elif model == "hwes":
        result: List[pd.DataFrame] = pool.starmap(
            hw_es_fit_and_predict_multi,
            zip(
                filtered_dfs_by_country,
                time_columns,
                feature_columns,
                repeat(frequencies[0], n_countries),
                repeat(data["periods"], n_countries),
                repeat(data["maxLags"], n_countries),
            ),
        )
    pool.close()
    pool.join()

    response_data["x"] = (
        result[0][time_columns[-1][-1]].dt.strftime("%Y-%m-%d").tolist()
    )

    for i, (country, features) in enumerate(zip(countries, feature_columns)):
        response_data[country] = {}

        for feature in features:
            response_data[country][feature] = result[i][feature].tolist()

    return response_data
