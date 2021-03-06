from matplotlib.pyplot import margins
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
