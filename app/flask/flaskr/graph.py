import numpy as np
import pandas as pd
import pycountry

from flask import (
    Blueprint,
    jsonify,
    request,
)
from flask_jwt_extended import get_jwt_identity, jwt_required
from .preprocessing.parse import parse_dataset, merge_dataframes_multi

from .extensions import mongo

bp = Blueprint("graph", __name__, url_prefix="/graph")


@bp.route("/datatable", methods=["GET", "POST"])
@jwt_required()
def get_selected_data():

    data = request.get_json()["datasets"]

    if data is None:
        return ("Empty request", 400)

    dataset_id = data["id"]

    geo_selected = data["geoSelected"] if data["geoSelected"] != "None" else None

    reshape_col = (
        (data["reshapeSelected"] if data["reshapeSelected"] != "N/A" else None)
        if "reshapeSelected" in data
        else None
    )

    session = get_jwt_identity()

    df, _ = parse_dataset(
        geo_column=geo_selected,
        dataset_id=dataset_id,
        reshape_column=reshape_col,
        session_id=session,
        use_preprocessed=False,
    )
    df.fillna(value=0)

    response_data = df.to_json(orient="records")

    return response_data


@bp.route("/history", methods=["GET", "POST"])
@bp.route("/map", methods=["GET", "POST"])
@bp.route("/statistics", methods=["GET", "POST"])
@jwt_required()
def get_selected_feature_data():

    data = request.get_json()["datasets"]

    if data is None:
        return ("Empty request", 400)

    geo_selected = data["geoSelected"] if data["geoSelected"] != "None" else None
    time_selected = data["timeSelected"]
    feature_selected = data["featureSelected"]
    dataset_id = data["id"]
    reshape_col = data["reshapeSelected"] if data["reshapeSelected"] != "N/A" else None

    session = get_jwt_identity()

    df, _ = parse_dataset(
        geo_column=geo_selected,
        dataset_id=dataset_id,
        reshape_column=reshape_col,
        session_id=session,
    )

    df = df.fillna(value=0)

    response_data = {}

    if geo_selected is not None:
        countries = df[geo_selected].unique().tolist()
        for country in countries:

            response_data[country] = {}

            response_data[country][time_selected] = df[df[geo_selected] == country][
                time_selected
            ].to_list()
            response_data[country][feature_selected] = df[df[geo_selected] == country][
                feature_selected
            ].to_list()

            if "statistics" in request.path:
                country_full = pycountry.countries.get(alpha_3=country).name
                response_data[country_full] = response_data.pop(country)

    else:
        response_data[time_selected] = (
            df[time_selected].dt.strftime("%Y-%m-%d").to_list()
        )
        response_data[feature_selected] = df[feature_selected].to_list()

    return response_data


@bp.route("/heatmap", methods=["POST"])
@jwt_required()
def get_heatmap():

    if mongo.db is None:
        return ("Database not available", 500)

    data = request.get_json()
    datasets = data["datasets"]

    if "country" in data:
        selected_country = pycountry.countries.get(name=data["country"]).alpha_3

    if data is None:
        return ("Empty request", 400)

    dfs = []
    time_columns = []
    response_data = {}

    session = get_jwt_identity()

    for dataset in datasets:

        if "geoSelected" in dataset and "reshapeSelected" in dataset:

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

            df, _ = parse_dataset(
                geo_column=geo_selected,
                dataset_id=dataset_id,
                reshape_column=reshape_selected,
                session_id=session,
            )

            if geo_selected is None:
                df[time_selected] = pd.to_datetime(df[time_selected].astype("str"))
                dfs.append(df)
                time_columns.append(time_selected)

            elif (
                geo_selected is not None
                and selected_country in df[geo_selected].unique()
            ):
                df_by_country = df[df[geo_selected] == selected_country]

                df_by_country = df_by_country.drop(columns=[geo_selected])

                df_by_country[time_selected] = pd.to_datetime(
                    df_by_country[time_selected].astype("str")
                )
                dfs.append(df_by_country)
                time_columns.append(time_selected)

    if len(dfs) > 1:
        merged_df, merged_time_col = merge_dataframes_multi(dfs, time_columns)

        merged_df = merged_df.drop(columns=[merged_time_col])[
            data["features"]
        ].infer_objects()

        triangular_upper_mask = np.triu(np.ones(merged_df.corr().shape)).astype(bool)

        correlation_matrix = merged_df.corr().where(~triangular_upper_mask).fillna(0)

    else:
        dfs[0] = dfs[0][data["features"]]

        triangular_upper_mask = np.triu(np.ones(dfs[0].corr().shape)).astype(bool)

        correlation_matrix = dfs[0].corr().where(~triangular_upper_mask).fillna(0)

    response_data["columns"] = correlation_matrix.columns.to_list()

    response_data["matrix"] = correlation_matrix.values.tolist()

    return jsonify(response_data)


@bp.route("/corr", methods=["POST"])
@jwt_required()
def get_correlation_lines():
    if mongo.db is None:
        return ("Database not available", 500)

    data = request.get_json()
    datasets = data["datasets"]

    if "country" in data:
        selectedcountry = pycountry.countries.get(name=data["country"]).alpha_3

    min_timestamp = None
    max_timestamp = None

    if data is None:
        return ("Empty request", 400)

    dfs = []
    feature_options = []

    response_data = []

    session = get_jwt_identity()

    for i, dataset in enumerate(datasets):

        if "geoSelected" in dataset and "reshapeSelected" in dataset:

            datasetid = dataset["id"]
            file_data = {}

            file_data["datasetid"] = datasetid

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

            df, _ = parse_dataset(
                geo_column=geo_selected,
                dataset_id=dataset_id,
                reshape_column=reshape_selected,
                session_id=session,
            )
            df = df.fillna(0)

            if geo_selected is not None:
                df_by_country = df[df[geo_selected] == selectedcountry]
            else:
                df_by_country = df

            print("iter ", i)

            df_by_country[time_selected] = pd.to_datetime(
                df_by_country[time_selected].astype("str")
            )

            features = [
                feature
                for feature in df_by_country.columns.to_list()
                if feature not in (geo_selected, time_selected)
            ]

            feature_options.append(features)
            dfs.append(df_by_country)

            file_data[time_selected] = (
                df_by_country[time_selected].dt.strftime("%Y-%m-%d").to_list()
            )

            for feature in features:
                file_data[feature] = df_by_country[feature].tolist()

            if not df_by_country[time_selected].empty:
                if min_timestamp is None or min_timestamp > min(
                    df_by_country[time_selected]
                ):
                    min_timestamp = min(df_by_country[time_selected])
                if max_timestamp is None or max_timestamp < max(
                    df_by_country[time_selected]
                ):
                    max_timestamp = max(df_by_country[time_selected])

            response_data.append(file_data)

    for dataset in response_data:
        dataset["timestamps"] = [
            min_timestamp.strftime("%Y-%m-%d"),
            max_timestamp.strftime("%Y-%m-%d"),
        ]

    return response_data
