import numpy as np
import pandas as pd

from flask import (
    Blueprint,
    jsonify,
    request,
)
from .preprocessing.parse import parse_dataset, merge_dataframes_multi

from .extensions import mongo

bp = Blueprint("graph", __name__, url_prefix="/graph")


@bp.route("/history", methods=["GET", "POST"])
@bp.route("/map", methods=["GET", "POST"])
def get_selected_feature_data():

    data = request.get_json()["datasets"]

    if data is None:
        return ("Empty request", 400)

    geo_selected = data["geoSelected"]
    time_selected = data["timeSelected"]
    feature_selected = data["featureSelected"]
    dataset_id = data["id"]
    reshape_col = data["reshapeSelected"] if data["reshapeSelected"] != "N/A" else None

    df = parse_dataset(
        geo_column=geo_selected,
        dataset_id=dataset_id,
        reshape_column=reshape_col,
    )

    df = df.fillna(value=0)

    response_data = {}

    for country in df[geo_selected].unique().tolist():
        response_data[country] = {}

        response_data[country][time_selected] = df[df[geo_selected] == country][
            time_selected
        ].to_list()
        response_data[country][feature_selected] = df[df[geo_selected] == country][
            feature_selected
        ].to_list()

    return response_data


@bp.route("/heatmap", methods=["POST"])
def get_heatmap():

    if mongo.db is None:
        return ("Database not available", 500)

    data = request.get_json()
    datasets = data["datasets"]
    selected_country = data["country"]

    if data is None:
        return ("Empty request", 400)

    dfs = []
    time_columns = []
    response_data = {}

    for dataset in datasets:

        reshape_selected = (
            dataset["reshapeSelected"] if dataset["reshapeSelected"] != "N/A" else None
        )
        geo_selected = dataset["geoSelected"]
        dataset_id = dataset["id"]
        time_selected = dataset["timeSelected"]

        df = parse_dataset(
            geo_column=geo_selected,
            dataset_id=dataset_id,
            reshape_column=reshape_selected,
        )

        if selected_country in df[geo_selected].unique():
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
        triangular_upper_mask = np.triu(np.ones(dfs[0].corr().shape)).astype(bool)

        correlation_matrix = dfs[0].corr().where(~triangular_upper_mask).fillna(0)

    response_data["columns"] = correlation_matrix.columns.to_list()

    response_data["matrix"] = correlation_matrix.values.tolist()

    return jsonify(response_data)


@bp.route("/corr", methods=["POST"])
def get_correlation_lines():
    if mongo.db is None:
        return ("Database not available", 500)

    data = request.get_json()
    datasets = data["datasets"]
    selectedcountry = data["country"]

    if data is None:
        return ("Empty request", 400)

    dfs = []
    feature_options = []

    response_data = []

    for dataset in datasets:
        file_data = {}

        reshape_selected = (
            dataset["reshapeSelected"] if dataset["reshapeSelected"] != "N/A" else None
        )
        geo_selected = dataset["geoSelected"]
        dataset_id = dataset["id"]
        time_selected = dataset["timeSelected"]

        df = parse_dataset(
            geo_column=geo_selected,
            dataset_id=dataset_id,
            reshape_column=reshape_selected,
        )
        df = df.fillna(0)
        df_by_country = df[df[geo_selected] == selectedcountry]

        features = [
            feature
            for feature in df_by_country.columns.to_list()
            if feature not in (geo_selected)
        ]

        feature_options.append(features)
        dfs.append(df_by_country)

        file_data[time_selected] = df_by_country[time_selected].to_list()
        for feature in features:
            file_data[feature] = df_by_country[feature].tolist()

        response_data.append(file_data)

    return response_data
