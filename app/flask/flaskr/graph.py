import json
import plotly

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from .plots.plots import (
    create_choropleth_slider_plot,
    create_multi_line_plot,
    create_correlation_heatmap,
    create_two_line_plot,
)
from .preprocessing.parse import parse_dataset, merge_dataframes_multi
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import mongo

bp = Blueprint("graph", __name__, url_prefix="/graph")


@bp.route("/map", methods=["GET"])
def getMap():
    geo_col = request.args.get("geo")
    time_col = request.args.get("x")
    feature_col = request.args.get("y")
    data_id = int(request.args.get("id"))
    reshape_col = request.args.get("rshp")

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

    return render_template("figure.html", graphJSON=graphJSON)
    # return jsonify(graphJSON)


@bp.route("/history", methods=["GET"])
def getHistory():
    geo_col = request.args.get("geo")
    time_col = request.args.get("x")
    feature_col = request.args.get("y")
    data_id = int(request.args.get("id"))
    reshape_col = request.args.get("rshp")

    df = parse_dataset(
        geo_column=geo_col,
        dataset_id=data_id,
        reshape_column=reshape_col,
    )

    fig = create_multi_line_plot(
        df, geo_col=geo_col, time_column=time_col, feature_column=feature_col
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("figure.html", graphJSON=graphJSON)
    # return jsonify(graphJSON)


@bp.route("/heatmap", methods=["GET"])
def getHeatmap():
    geo_col = request.args.getlist("geo")
    reshape_col = request.args.getlist("rshp")
    time_col = request.args.getlist("x")

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

    return render_template("figure.html", graphJSON=graphJSON)


@bp.route("/corr", methods=["GET"])
def getCorrLines():
    geo_col = request.args.getlist("geo")
    time_col = request.args.getlist("x")
    reshape_col = request.args.getlist("rshp")

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

    return render_template("figure.html", graphJSON=graphJSON)
    # return jsonify(graphJSON)
