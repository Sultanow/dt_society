from matplotlib.pyplot import margins
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

from urllib.request import urlopen
import json

theme = "plotly_dark"


def create_multi_line_plot(data: pd.DataFrame) -> go.Figure:
    """Creates a line plot with a line for each country

    Args:
        data (pd.DataFrame): Dataset

    Returns:
        go.Figure: line plot
    """
    fig = go.Figure()

    for i, country in enumerate(data["geo"]):
        visibility = None

        if country == "DEU":
            visibility = None
        else:
            visibility = "legendonly"

        fig.add_trace(
            go.Scatter(
                x=data.columns[2:],
                y=data.iloc[i, 2:],
                name=country,
                visible=visibility,
                mode="lines",
            )
        )

    fig.update_layout(
        xaxis_title="Year", legend_title="Countries", template=theme, margin={"t": 30}
    )

    fig.update_layout(transition_duration=500)

    return fig


def create_choropleth_plot(
    data: pd.DataFrame, facet: str = None, year: str = None
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
        counties = json.load(response)

    fig = px.choropleth_mapbox(
        data[data["year"] == year],
        locations="geo",
        featureidkey="properties.ISO3",
        color="value",
        geojson=counties,
        zoom=2.5,
        center={"lat": 56.5, "lon": 11},
        mapbox_style="carto-positron",
        opacity=0.5,
        color_continuous_scale="Magma",  # Inferno
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="#111111",
        font_color="#f2f2f2",
    )

    return fig


def create_two_line_plot(
    dataset_1: pd.DataFrame,
    dataset_2: pd.DataFrame,
    row_index_1: int,
    row_index_2: int,
    column_index_1: int,
    column_index_2: int,
    selected_unit_1: str,
    selected_unit_2: str,
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

    fig.add_trace(
        go.Scatter(
            x=dataset_1.columns[column_index_1:],
            y=dataset_1.iloc[row_index_1, column_index_1:],
            name=selected_unit_1 + " (left ax)",
            mode="lines",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=dataset_2.columns[column_index_2:],
            y=dataset_2.iloc[row_index_2, column_index_2:],
            name=selected_unit_2 + " (right ax)",
            mode="lines",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        transition_duration=500, template=theme, margin={"t": 20, "b": 20}, height=300
    )

    return fig
