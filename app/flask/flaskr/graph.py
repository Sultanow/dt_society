import json
from time import time_ns
import plotly
import numpy as np
import pandas as pd

from flask import (
    Blueprint,
    jsonify,
    request,
)
from .plots.plots import (
    create_choropleth_slider_plot,
    create_multi_line_plot,
    create_correlation_heatmap,
    create_two_line_plot,
)
from .preprocessing.parse import parse_dataset, merge_dataframes_multi

from .extensions import mongo


bp = Blueprint("graph", __name__, url_prefix="/graph")


@bp.route("/map", methods=["POST"])
def get_map():

    data = request.get_json()["datasets"]

    if data is None:
        return ("Empty request", 400)

    geo_col = data["geoSelected"]
    time_col = data["timeSelected"]
    feature_col = data["featureSelected"]
    data_id = data["id"]
    reshape_col = data["reshapeSelected"] if data["reshapeSelected"] != "N/A" else None

    df = parse_dataset(
        geo_column=geo_col,
        dataset_id=data_id,
        reshape_column=reshape_col,
    )

    df = df.fillna(0)
    d = {}

    for country in df[geo_col].unique().tolist():
        d[country] = {}

        d[country][time_col] = df[df[geo_col] == country][time_col].to_list()
        d[country][feature_col] = df[df[geo_col] == country][feature_col].to_list()

    return d


@bp.route("/history", methods=["GET", "POST"])
def get_history():

    data = request.get_json()["datasets"]
    if data is None:
        return ("Empty request", 400)
    geo_col = data["geoSelected"]
    time_col = data["timeSelected"]
    feature_col = data["featureSelected"]
    data_id = data["id"]
    reshape_col = data["reshapeSelected"] if data["reshapeSelected"] != "N/A" else None

    df = parse_dataset(
        geo_column=geo_col,
        dataset_id=data_id,
        reshape_column=reshape_col,
    )

    df = df.fillna(0)

    d = {}

    for country in df[geo_col].unique().tolist():
        d[country] = {}

        d[country][time_col] = df[df[geo_col] == country][time_col].to_list()
        d[country][feature_col] = df[df[geo_col] == country][feature_col].to_list()

    return d


@bp.route("/heatmap", methods=["POST"])
def get_heatmap():

    if mongo.db is None:
        return ("Database not available", 500)

    data = request.get_json()

    if data is None:
        return ("Empty request", 400)

    geo_col = []
    reshape_col = []
    time_col = []

    for dataset in data["datasets"]:

        geo_col.append(dataset["geoSelected"])
        reshape_col.append(
            dataset["reshapeSelected"] if dataset["reshapeSelected"] != "N/A" else None
        )
        time_col.append(dataset["timeSelected"])

    dfs = []
    time_columns = []

    d = {}

    collection = mongo.db["collection_1"]
    for i in range(collection.count_documents({})):
        df = parse_dataset(
            geo_column=geo_col[i],
            dataset_id=i,
            reshape_column=reshape_col[i],
        )

        selectedcountry = data["country"]

        if selectedcountry in df[geo_col[i]].unique():
            df_by_country = df[df[geo_col[i]] == selectedcountry]

            df_by_country = df_by_country.drop(columns=[geo_col[i]])

            df_by_country[time_col[i]] = pd.to_datetime(
                df_by_country[time_col[i]].astype("str")
            )
            dfs.append(df_by_country)
            time_columns.append(time_col[i])

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

    d["columns"] = correlation_matrix.columns.to_list()

    d["matrix"] = correlation_matrix.values.tolist()

    return jsonify(d)


@bp.route("/corr", methods=["POST"])
def get_correlation_lines():
    if mongo.db is None:
        return ("Database not available", 500)

    data = request.get_json()["datasets"]
    selectedcountry = request.get_json()["country"]

    min_timestamp = None
    max_timestamp = None
    
    if data is None:
        return ("Empty request", 400)

    geo_col = []
    reshape_col = []
    time_col = []

    for dataset in data:

        geo_col.append(dataset["geoSelected"])
        reshape_col.append(
            dataset["reshapeSelected"] if dataset["reshapeSelected"] != "N/A" else None
        )
        time_col.append(dataset["timeSelected"])

    dfs = []
    feature_options = []

    d = []

    collection = mongo.db["collection_1"]
    for i in range(collection.count_documents({})):
        f = {}
        df = parse_dataset(
            geo_column=geo_col[i],
            dataset_id=i,
            reshape_column=reshape_col[i],
        )
        df = df.fillna(0)
        df_by_country = df[df[geo_col[i]] == selectedcountry]

        df_by_country[time_col[i]] = pd.to_datetime(df_by_country[time_col[i]].astype("str"))

        features = [
            feature
            for feature in df_by_country.columns.to_list()
            if feature not in time_col and feature not in geo_col
        ]

        feature_options.append(features)
        dfs.append(df_by_country)

        f[time_col[i]] = df_by_country[time_col[i]].dt.strftime("%Y-%m-%d").to_list()
        for feature in features:
            f[feature] = df_by_country[feature].tolist()
            
        if(not df_by_country[time_col[i]].empty):
            if min_timestamp is None or min_timestamp > min(df_by_country[time_col[i]]):
                min_timestamp = min(df_by_country[time_col[i]])
            if max_timestamp is None or max_timestamp < max(df_by_country[time_col[i]]):
                max_timestamp = max(df_by_country[time_col[i]])

        d.append(f)    

    for dataset in d:
        dataset["timestamps"] = [min_timestamp.strftime("%Y-%m-%d"), max_timestamp.strftime("%Y-%m-%d")]

    return d
