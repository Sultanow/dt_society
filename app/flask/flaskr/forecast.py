import json
import plotly

from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    session,
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

bp = Blueprint("forecast", __name__, url_prefix="/forecast")


@bp.route("/var", methods=["GET"])
def forecastVAR():
    geo_col = request.args.getlist("geo")
    time_col = request.args.getlist("x")
    feature_col = request.args.getlist("y")
    reshape_col = request.args.getlist("rshp")

    filtered_dfs = []
    for i in range(len(session["files"])):
        df = parse_dataset(
            session=session,
            geo_column=geo_col[i],
            dataset_id=i,
            reshape_column=reshape_col[i],
        )
        filtered_df = df[df[geo_col[i]] == "AUT"][[time_col[i], feature_col[i]]]

        filtered_dfs.append(filtered_df)

    forecast = var_fit_and_predict_multi(
        filtered_dfs,
        time_col,
        feature_col,
        max_lags=2,
        periods=5,
        frequency="Yearly",
    )

    fig = create_var_forecast_plot_multi(forecast, feature_col, time_col[-1], 5)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("figure.html", graphJSON=graphJSON)
    # return jsonify(graphJSON)


@bp.route("hwes", methods=["GET"])
def forecastHWES():
    geo_col = request.args.getlist("geo")
    time_col = request.args.getlist("x")
    feature_col = request.args.getlist("y")
    reshape_col = request.args.getlist("rshp")

    filtered_dfs = []
    for i in range(len(session["files"])):
        df = parse_dataset(
            session=session,
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
    for i in range(len(session["files"])):
        df = parse_dataset(
            session=session,
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
