from fileinput import filename
from typing import Tuple
from dash import Dash, dcc, html, Input, Output, exceptions, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import re
import base64
import io

from .dataset import DigitalTwinTimeSeries


def parse_dataset(
    contents: str,
    get_countries: bool = False,
    geo_col: str = None,
    upload_file: bool = True,
) -> Tuple[str, list]:
    """Parses a dataset and converts it into dataframe

    Args:
        contents (str): Uploaded dataset
        get_countries (bool, optional): Returns all countries present in the dataset. Defaults to False.

    Returns:
        Tuple[str, list]: tuple of converted dataset and available indicator columns
    """
    if upload_file:
        try:
            _, content_string = contents.split(",")

            decoded = base64.b64decode(content_string)

            df = DigitalTwinTimeSeries(io.StringIO(decoded.decode("utf-8")))
        except Exception as e:
            print(e)
            return html.Div(["There was an error processing this file."])
    else:
        df = DigitalTwinTimeSeries(contents)

    years_excluded_re = re.compile("[^1-2][^0-9]*")
    columns = df.data.columns.to_list()
    filtered_columns = [colum for colum in columns if years_excluded_re.match(colum)]

    if geo_col is not None:
        if geo_col in filtered_columns:
            filtered_columns.remove(geo_col)

    df_json = df.data.to_json()

    if get_countries:
        countries = df.data["geo"].unique().tolist()
        return df_json, filtered_columns, countries
    else:
        return df_json, filtered_columns
