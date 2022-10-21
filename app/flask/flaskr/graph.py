import json
import plotly

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

    data = request.get_json()

    if data is None:
        return ("Empty request", 400)

    geo_col = data["geoSelected"]
    time_col = data["timeSelected"]
    feature_col = data["featureSelected"]
    data_id = data["id"]
    reshape_col = data["reshapeSelected"]

    df = parse_dataset(
        geo_column=geo_col,
        dataset_id=data_id,
        reshape_column=reshape_col,
    )

    fig = create_choropleth_slider_plot(
        df,
        geo_column=geo_col,
        feature_column=feature_col,
        time_column=time_col,
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    response = jsonify(json.loads(graphJSON))

    return response


@bp.route("/history", methods=["GET", "POST"])
def get_history():

    data = request.get_json()
    if data is None:
        return ("Empty request", 400)
    geo_col = data["geoSelected"]
    time_col = data["timeSelected"]
    feature_col = data["featureSelected"]
    data_id = data["id"]
    reshape_col = data["reshapeSelected"]

    df = parse_dataset(
        geo_column=geo_col,
        dataset_id=data_id,
        reshape_column=reshape_col,
    )

    fig = create_multi_line_plot(
        df, geo_col=geo_col, time_column=time_col, feature_column=feature_col
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    response = jsonify(json.loads(graphJSON))

    return response


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

    for dataset in data:
        geo_col.append(dataset["geoSelected"])
        reshape_col.append(dataset["reshapeSelected"])
        time_col.append(dataset["timeSelected"])

    dfs = []
    time_columns = []

    collection = mongo.db["collection_1"]
    for i in range(collection.count_documents({})):
        df = parse_dataset(
            geo_column=geo_col[i],
            dataset_id=i,
            reshape_column=reshape_col[i],
        )
        # replace "AUT" with country selection
        if "AUT" in df[geo_col[i]].unique():
            df_by_country = df[df[geo_col[i]] == "AUT"]
            df_by_country = df_by_country.drop(columns=[geo_col[i]])
            dfs.append(df_by_country)

            time_columns.append(time_col[i])

    if len(dfs) > 1:
        merged_df, merged_time_col = merge_dataframes_multi(dfs, time_columns)

        merged_df = merged_df.drop(columns=[merged_time_col]).infer_objects()
        fig = create_correlation_heatmap(merged_df)

    else:
        fig = create_correlation_heatmap(dfs[0])

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    response = jsonify(json.loads(graphJSON))

    return response


@bp.route("/corr", methods=["POST"])
def get_correlation_lines():
    if mongo.db is None:
        return ("Database not available", 500)

    data = request.get_json()

    if data is None:
        return ("Empty request", 400)

    geo_col = []
    reshape_col = []
    time_col = []

    for dataset in data:
        geo_col.append(dataset["geoSelected"])
        reshape_col.append(dataset["reshapeSelected"])
        time_col.append(dataset["timeSelected"])

    dfs = []
    feature_options = []

    collection = mongo.db["collection_1"]
    for i in range(collection.count_documents({})):
        df = parse_dataset(
            geo_column=geo_col[i],
            dataset_id=i,
            reshape_column=reshape_col[i],
        )
        df_by_country = df[df[geo_col[i]] == "AUT"]

        features = [
            feature
            for feature in df_by_country.columns.to_list()
            if feature not in time_col and feature not in geo_col
        ]

        feature_options.append(features)
        dfs.append(df_by_country)

    fig = create_two_line_plot(dfs, time_col, feature_options)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    response = jsonify(json.loads(graphJSON))

    return response
