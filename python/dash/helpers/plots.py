import datetime
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

from urllib.request import urlopen
import json

theme = "plotly_dark"


def create_multi_line_plot(
    data: pd.DataFrame, geo_col, time_column, feature_column
) -> go.Figure:
    """Creates a line plot with a line for each country

    Args:
        data (pd.DataFrame): Dataset

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
        margin={"t": 30},
    )

    return fig


def create_choropleth_plot(
    data: pd.DataFrame,
    geo_column: str,
    feature_column: str,
    facet: str = None,
    year: str = None,
) -> go.Figure:
    """Creates a choropleth plot with timeline

    Args:
        data (pd.DataFrame): Data

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


def create_choropleth_slider_plot(
    data: pd.DataFrame,
    geo_column: str,
    feature_column: str,
    time_column: str = None,
) -> go.Figure:
    """Creates choropleth plot with time slider and animation

    Args:
        data (pd.DataFrame): Data
        geo_column (str): value of geo column
        feature_column (str): value of feature column
        time_column (str, optional): value of column with time data. Defaults to None.

    Returns:
        go.Figure: Choropleth figure
    """
    fig_dict = {"data": [], "layout": {}, "frames": []}

    fig_dict["layout"] = dict(
        geo=dict(
            scope="world",
            projection={"type": "natural earth2", "scale": 4.5},
            bgcolor="rgba(0,0,0,0)",
            center=dict(lat=50.5, lon=11),
        ),
        margin=dict(l=0, r=0, b=0, t=1, pad=0, autoexpand=True),
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
            "pad": {"r": 10, "t": 0},
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
        "pad": {"b": 10, "t": 0},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": [],
    }

    if np.issubdtype(np.datetime64, data[time_column]):
        data[time_column] = data[time_column].dt.strftime("%b-%d")

    first_year = data[time_column].unique()[0]

    data_dict = dict(
        type="choropleth",
        locations=data[data[time_column] == first_year][geo_column],
        locationmode="ISO-3",
        z=data[data[time_column] == first_year][feature_column],
        zmin=0,
        zmax=data[feature_column].max(),
        colorscale="Magma",
        colorbar=go.choropleth.ColorBar(
            title=go.choropleth.colorbar.Title(text=feature_column)
        ),
        marker_line_color="darkgray",
        marker_line_width=0.5,
    )

    fig_dict["data"].append(data_dict)

    for time in data[time_column].unique():

        df_per_year = data[data[time_column] == time]

        fig_dict["frames"].append(
            dict(
                data=dict(
                    type="choropleth",
                    locations=df_per_year[geo_column],
                    locationmode="ISO-3",
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
    fig_choropleth.update_geos(
        showcoastlines=True, showsubunits=True, showframe=False, resolution=50
    )
    fig_choropleth.update_layout(template=theme)

    return fig_choropleth


def create_two_line_plot(
    datasets: tuple, feature_columns: tuple, time_columns: tuple
) -> go.Figure:
    """Creates a line plot with two lines, where the second line belongs to an additional subplot

    Args:
        dataset_1 (pd.DataFrame): First dataset
        dataset_2 (pd.DataFrame): Second dataset
        row_index_1 (int): index of the selected row in dataset_1
        row_index_2 (int): index of the selected row in dataset_2
        column_index_1 (int): index of first column in timeline
        column_index_2 (int): index of second column in timeline
        selected_unit_1 (str): selected value in the first unit dropdown
        selected_unit_2 (str): selected value in the second unit dropdown

    Returns:
        go.Figure: Line plot with one line per subplot
    """

    fig = go.Figure(make_subplots(specs=[[{"secondary_y": True}]]))

    for i, df in enumerate(datasets):
        secondary_y = True if i % 2 else False
        fig.add_trace(
            go.Scatter(
                x=df[time_columns[i]],
                y=df[feature_columns[i]],
                name=feature_columns[i] + "",
                mode="lines",
            ),
            secondary_y=secondary_y,
        )

    fig.update_layout(
        transition_duration=500,
        template=theme,
        margin={"t": 20, "b": 20},
        height=300,
        yaxis1_title=feature_columns[0],
        yaxis2_title=feature_columns[1],
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

    fig.update_layout(template=theme, margin={"t": 20})

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
    )

    return fig


def create_multivariate_forecast(
    forecast, df, future_df, feature_column_1, feature_column_2
):
    if feature_column_1 == feature_column_2:
        feature_column_1 += "_x"
        feature_column_2 += "_y"

    fig = go.Figure(make_subplots(specs=[[{"secondary_y": True}]]))

    fig.add_trace(
        go.Scatter(
            x=df["ds"],
            y=df["y"],
            name=feature_column_1,
            mode="lines",
            line={"color": "mediumpurple"},
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["ds"],
            y=df[feature_column_2],
            name=feature_column_2,
            mode="lines",
            line={"color": "mediumspringgreen"},
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(
            x=future_df["ds"],
            y=future_df[feature_column_2],
            name=feature_column_2,
            mode="lines",
            line={"dash": "dash", "color": "mediumspringgreen"},
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat"],
            name="Prediction " + feature_column_1,
            mode="lines+markers",
            line={"dash": "dash"},
            marker=go.scatter.Marker(symbol="triangle-up", color="mediumpurple"),
            error_y=go.scatter.ErrorY(
                array=forecast["yhat_upper"] - forecast["yhat"],
                arrayminus=forecast["yhat"] - forecast["yhat_lower"],
            ),
        ),
        secondary_y=False,
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
        secondary_y=False,
    )

    fig.update_layout(
        template="plotly_dark",
        yaxis1_title=feature_column_1,
        yaxis2_title=feature_column_2,
        margin={"t": 20},
    )

    return fig


def create_var_forecast_plot(
    df, feature_column_1, feature_column_2, time_column, periods
):

    if feature_column_1 == feature_column_2:
        feature_column_1 += "_x"
        feature_column_2 += "_y"

    fig = go.Figure(make_subplots(specs=[[{"secondary_y": True}]]))

    fig.add_trace(
        go.Scatter(
            x=df[time_column][:-periods],
            y=df[feature_column_1][:-periods],
            name=feature_column_1,
            mode="lines",
            line={"color": "mediumpurple"},
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df[time_column][-periods - 1 :],
            y=df[feature_column_1][-periods - 1 :],
            name=feature_column_1 + " Prediction",
            mode="lines",
            line={"dash": "dash", "color": "mediumpurple"},
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df[time_column][:-periods],
            y=df[feature_column_2][:-periods],
            name=feature_column_2,
            mode="lines",
            line={"color": "mediumspringgreen"},
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(
            x=df[time_column][-periods - 1 :],
            y=df[feature_column_2][-periods - 1 :],
            name=feature_column_2 + " Prediction",
            mode="lines",
            line={"dash": "dash", "color": "mediumspringgreen"},
        ),
        secondary_y=True,
    )

    fig.update_layout(
        template="plotly_dark",
        yaxis1_title=feature_column_1,
        yaxis2_title=feature_column_2,
        margin={"t": 20},
    )

    return fig
