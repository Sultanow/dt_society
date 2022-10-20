import enum
import os
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

from urllib.request import urlopen
import json

from typing import List
from ..extensions import cache

# cache = Cache(config={"CACHE_TYPE": "SimpleCache"})

theme = "plotly_dark"


def create_multi_line_plot(
    data: pd.DataFrame, geo_col: str, time_column: str, feature_column: str
) -> go.Figure:
    """Creates a line plot with a line for each country

    Args:
        data (pd.DataFrame): dataframe
        geo_col (str): geo column value
        time_column (str): time column value
        feature_column (str): feature column value

    Returns:
        go.Figure: line plot
    """
    fig = go.Figure()
    if geo_col != "None":
        for country in data[geo_col].unique().tolist():

            filtered_df = data[data[geo_col] == country]
            visibility = None

            if country == "DEU":
                visibility = None
            else:
                visibility = "legendonly"

            fig.add_trace(
                go.Scatter(
                    x=filtered_df[time_column],
                    y=filtered_df[feature_column],
                    name=country,
                    visible=visibility,
                    mode="lines",
                )
            )

        fig.update_layout(
            legend_title="Countries",
        )

    else:
        fig = px.line(x=data[time_column], y=data[feature_column])

    fig.update_layout(transition_duration=500)

    fig.update_layout(
        xaxis_title=time_column,
        yaxis_title=feature_column,
        template=theme,
        margin={"t": 30, "autoexpand": True},
        paper_bgcolor="#232323",
        plot_bgcolor="#232323",
    )

    return fig


def create_choropleth_plot(
    data: pd.DataFrame,
    geo_column: str,
    feature_column: str,
) -> go.Figure:
    """Creates a choropleth plot with timeline

    Args:
        data (pd.DataFrame): Dataframe

    Returns:
        go.Figure: Choropleth plot
    """
    with urlopen(
        "https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson"
    ) as response:
        countries = json.load(response)

    fig = px.choropleth_mapbox(
        data,
        locations=geo_column,
        featureidkey="properties.ISO3",
        color=feature_column,
        geojson=countries,
        zoom=2.5,
        center={"lat": 56.5, "lon": 11},
        mapbox_style="carto-positron",
        opacity=0.5,
        color_continuous_scale="Magma",  # Inferno
    )

    fig.update_layout(
        margin={"r": 0, "t": 1, "l": 0, "b": 0},
        paper_bgcolor="#111111",
        font_color="#f2f2f2",
    )

    return fig


@cache.memoize(timeout=30)
def create_choropleth_slider_plot(
    data: pd.DataFrame,
    geo_column: str,
    feature_column: str,
    time_column: str = None,
    scope="europe",
) -> go.Figure:
    """Creates choropleth plot with time slider and animated transitions

    Args:
        data (pd.DataFrame): Data
        geo_column (str): value of geo column
        feature_column (str): value of feature column
        time_column (str, optional): value of column with time data. Defaults to None.
        scope (str, optional): value of selected scope. Defaults to "Europe".

    Returns:
        go.Figure: Choropleth figure
    """
    fig_dict = {"data": [], "layout": {}, "frames": []}

    fig_dict["layout"] = dict(
        margin=dict(l=0, r=0, b=1, t=1, pad=0, autoexpand=True),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [
                        None,
                        {
                            "frame": {"duration": 500, "redraw": True},
                            "fromcurrent": True,
                            "transition": {
                                "duration": 300,
                                "easing": "quadratic-in-out",
                            },
                        },
                    ],
                    "label": "Play",
                    "method": "animate",
                },
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 10},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top",
        }
    ]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "visible": False,
        },
        "transition": {"duration": 300},
        "pad": {"b": 10, "t": 5},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": [],
    }

    if np.issubdtype(np.datetime64, data[time_column]):
        data[time_column] = data[time_column].dt.strftime("%b-%d")

    first_year = data[time_column].unique()[0]

    geojsons = {
        "global": {
            "url": "https://datahub.io/core/geo-countries/r/countries.geojson",
            "featureid": "properties.ISO_A3",
            "zoom": 1,
            "center": {"lat": 56.5, "lon": 11},
        },
        "europe": {
            "url": "https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson",
            "path": "flaskr/static/geojson/europe.geojson",
            "featureid": "properties.ISO3",
            # "featureid": "properties.adm0_iso",
            "zoom": 2.5,
            "center": {"lat": 53, "lon": 11},
        },
        "germany": {
            "url": "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/3_mittel.geo.json",
            "path": "/assets/3_mittel.geo.json",
            "featureid": "properties.id",
            "zoom": 4.4,
            "center": {"lat": 51.3, "lon": 10},
        },
    }

    with open(geojsons[scope]["path"]) as f:
        countries = json.load(f)

    data_dict = dict(
        type="choroplethmapbox",
        locations=data[data[time_column] == first_year][geo_column],
        geojson=countries,
        featureidkey=geojsons[scope]["featureid"],
        z=data[data[time_column] == first_year][feature_column],
        zmin=0,
        zmax=data[feature_column].max(),
        colorscale="Magma",
        colorbar=go.choroplethmapbox.ColorBar(
            title=go.choroplethmapbox.colorbar.Title(text=feature_column)
        ),
        marker={"opacity": 0.5},
    )

    fig_dict["data"].append(data_dict)

    for time in data[time_column].unique():

        df_per_year = data[data[time_column] == time]

        fig_dict["frames"].append(
            dict(
                data=dict(
                    type="choroplethmapbox",
                    locations=df_per_year[geo_column],
                    featureidkey=geojsons[scope]["featureid"],
                    geojson=countries,
                    z=df_per_year[feature_column],
                ),
                name=str(time),
            )
        )

        slider_step = {
            "args": [
                [time],
                {
                    "frame": {"duration": 300, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 300},
                },
            ],
            "label": str(time),
            "method": "animate",
        }
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]

    fig_choropleth = go.Figure(fig_dict)
    fig_choropleth.update_mapboxes(
        style="carto-positron",
        zoom=geojsons[scope]["zoom"],
        center=geojsons[scope]["center"],
    )

    fig_choropleth.update_layout(template=theme)

    return fig_choropleth


def create_two_line_plot(
    datasets: List[pd.DataFrame],
    time_columns: List[str],
    feature_options: List[List[str]],
) -> go.Figure:
    """Creates a line plot with n subplots divided into rows and columns

    Args:
        datasets (List[pd.DataFrame]): available datasets
        feature_columns (List[str]): selected feature columns
        time_columns (List[str]): selected time columns

    Returns:
        go.Figure: line plot figure with subplots
    """

    rows = len(datasets) // 3 if len(datasets) // 3 >= 1 else 1

    fig = go.Figure(
        make_subplots(
            rows=rows,
            cols=len(datasets),
            subplot_titles=[f"Dataset {i+1}" for i in range(len(datasets))],
        )
    )

    min_timestamp = None
    max_timestamp = None

    for i, features in enumerate(feature_options):
        datasets[i][time_columns[i]] = pd.to_datetime(
            datasets[i][time_columns[i]].astype("str")
        )

        if min_timestamp is None or min_timestamp > min(datasets[i][time_columns[i]]):
            min_timestamp = min(datasets[i][time_columns[i]])

        if max_timestamp is None or max_timestamp < max(datasets[i][time_columns[i]]):
            max_timestamp = max(datasets[i][time_columns[i]])

        # features.remove(time_columns[i])
        for j, feature in enumerate(features):

            visibility = True if j == 0 else "legendonly"
            legend_group_title = f"Dataset {i+1}" if j == 0 else None

            print(legend_group_title)

            fig.add_trace(
                go.Scatter(
                    x=datasets[i][time_columns[i]],
                    y=datasets[i][feature],
                    name=feature,
                    mode="lines",
                    visible=visibility,
                    legendgroup=f"df_{i}",
                    legendgrouptitle_text=legend_group_title,
                ),
                col=i + 1,
                row=1,
            )

    fig.update_xaxes(range=[min_timestamp, max_timestamp])

    fig.update_layout(
        transition_duration=500,
        template=theme,
        margin={"t": 20, "b": 20},
        # height=300,
        legend={"groupclick": "toggleitem"},
        paper_bgcolor="#232323",
        plot_bgcolor="#232323",
    )

    return fig


def create_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Creates a correlation heatmap between all features in the dataset using Pearsons correlation coefficient.

    Args:
        df (pd.DataFrame): Dataframe containing features exclusively

    Returns:
        go.Figure: Heatmap of lower triangular correlation matrix
    """
    triangular_upper_mask = np.triu(np.ones(df.corr().shape)).astype(bool)
    fig = px.imshow(
        df.corr().where(~triangular_upper_mask),
        aspect="auto",
        color_continuous_scale="Viridis",
        labels={"color": "Pearson r"},
    )

    fig.update_layout(
        template=theme,
        margin={"t": 20},
        paper_bgcolor="#232323",
        plot_bgcolor="#232323",
    )

    return fig


def create_forecast_plot(
    forecast: pd.DataFrame, df: pd.DataFrame, time_column: str, feature_column: str
) -> go.Figure:
    """Creates a forecast plot with predictions made by the Prophet predictor. (https://facebook.github.io/prophet/)

    Args:
        forecast (pd.DataFrame): resulting predictions made by the Prophet predictor
        df (pd.DataFrame): original dataframe
        time_column (str): name of the time column in original dataframe
        feature_column (str): name of the feature column in original dataframe

    Returns:
        go.Figure: Lineplot with subplots for observations, model fit and future predictions respectively
    """
    fig = go.Figure()

    fig.add_traces(
        go.Scatter(
            x=df["ds"],
            y=df["y"],
            name="Observations",
            mode="markers",
            marker=go.scatter.Marker(symbol="x"),
        )
    )

    fig.add_traces(
        go.Scatter(
            x=df["ds"],
            y=df["yhat"],
            name="Regression Fit",
            mode="lines",
        )
    )

    fig.add_traces(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat"],
            error_y=go.scatter.ErrorY(array=forecast["error"]),
            mode="markers",
            name="Predictions",
            marker=go.scatter.Marker(symbol="triangle-up"),
        ),
    )

    fig.update_layout(
        template=theme,
        xaxis_title=time_column,
        yaxis_title=feature_column,
        margin={"t": 20},
        paper_bgcolor="#232323",
        plot_bgcolor="#232323",
    )

    return fig


def create_var_forecast_plot_multi(
    forecast: pd.DataFrame,
    feature_columns: List[str],
    time_column: List[str],
    periods: int,
) -> go.Figure:
    """Create multivariate forecast plot with predictions from a Vector Auto Regression/HW exponential smoothing model

    Args:
        forecast (pd.DataFrame): forecast dataframe
        feature_columns (List[str]): selected features
        time_column (List[str]): selected time columns
        periods (int): number of forecasts predicted

    Returns:
        go.Figure: figure with line plot for each forecast
    """
    colors = ("mediumpurple", "mediumspringgreen", "hotpink", "mediumblue", "goldenrod")

    fig = go.Figure(make_subplots(rows=1, cols=len(feature_columns)))

    for i, feature in enumerate(feature_columns):
        fig.add_trace(
            go.Scatter(
                x=forecast[time_column][:-periods],
                y=forecast[feature][:-periods],
                name=feature,
                mode="lines",
                line={"color": f"{colors[i]}"},
            ),
            col=i + 1,
            row=1,
        )

        fig.add_trace(
            go.Scatter(
                x=forecast[time_column][-periods - 1 :],
                y=forecast[feature][-periods - 1 :],
                name=feature + "Prediction",
                mode="lines",
                line={"dash": "dash", "color": f"{colors[i]}"},
            ),
            col=i + 1,
            row=1,
        )

    yax_titles = {
        f"yaxis{i+1}_title": feature for i, feature in enumerate(feature_columns)
    }

    fig.update_layout(
        template="plotly_dark",
        margin={"t": 20, "b": 20},
        paper_bgcolor="#232323",
        plot_bgcolor="#232323",
        **yax_titles,
    )

    return fig


def create_multivariate_forecast_prophet(
    forecast: pd.DataFrame,
    df: pd.DataFrame,
    future_df: pd.DataFrame,
    y_feature: str,
    feature_columns: List[str],
) -> go.Figure:
    """Creates multivariate forecast plot with predictions from a Prophet model with given scenarios

    Args:
        forecast (pd.DataFrame): forecast result
        df (pd.DataFrame): initial dataframe
        future_df (pd.DataFrame): dataframe with future scenarios
        y_feature (str): value of dependent feature
        feature_columns (List[str]): list of independent feature

    Returns:
        go.Figure: figure with line plot for prophet forecast and all other future scenarios
    """

    # if feature_column_1 == feature_column_2:
    #     feature_column_1 += "_x"
    #     feature_column_2 += "_y"

    colors = ("mediumspringgreen", "hotpink", "mediumblue", "goldenrod")

    fig = go.Figure(
        make_subplots(
            rows=1,
            cols=len(feature_columns) + 1,
            subplot_titles=(
                "Forecast",
                *["Scenario" for i in range(len(feature_columns))],
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["ds"],
            y=df["y"],
            name=y_feature,
            mode="lines",
            line={"color": "mediumpurple"},
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat"],
            name="Prediction " + y_feature,
            mode="lines+markers",
            line={"dash": "dash"},
            marker=go.scatter.Marker(symbol="triangle-up", color="mediumpurple"),
            error_y=go.scatter.ErrorY(
                array=forecast["yhat_upper"] - forecast["yhat"],
                arrayminus=forecast["yhat"] - forecast["yhat_lower"],
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=pd.concat([df.iloc[-1], forecast.rename(columns={"yhat": "y"}).iloc[0]])[
                "ds"
            ],
            y=pd.concat([df.iloc[-1], forecast.rename(columns={"yhat": "y"}).iloc[0]])[
                "y"
            ],
            mode="lines",
            line={"dash": "dash", "color": "mediumpurple"},
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    for i, feature in enumerate(feature_columns):

        fig.add_trace(
            go.Scatter(
                x=df["ds"],
                y=df[feature],
                name=feature,
                mode="lines",
                line={"color": colors[i]},
            ),
            row=1,
            col=i + 2,
        )

        fig.add_trace(
            go.Scatter(
                x=future_df["ds"],
                y=future_df[feature],
                name=feature,
                mode="lines",
                line={"dash": "dash", "color": colors[i]},
            ),
            row=1,
            col=i + 2,
        )

    yax_titles = {
        f"yaxis{i+1}_title": feature
        for i, feature in enumerate([y_feature] + feature_columns)
    }

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#232323",
        plot_bgcolor="#232323",
        margin={"t": 20},
        **yax_titles,
    )

    return fig
