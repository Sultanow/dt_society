from typing import Tuple
from dash import html
import pandas as pd
import base64
import io

from .dataset import DigitalTwinTimeSeries


def parse_dataset(
    contents: str,
    geo_col: str = None,
    separator: str = "\t",
    reshape_col: str = None,
) -> Tuple[str, list]:
    """Parses a dataset and converts it into dataframe

    Args:
        contents (str): Uploaded dataset
        get_countries (bool, optional): Returns all countries present in the dataset. Defaults to False.

    Returns:
        Tuple[str, list]: tuple of converted dataset and available indicator columns
    """

    decoded = base64.b64decode(contents)

    df = DigitalTwinTimeSeries(
        io.StringIO(decoded.decode("utf-8")), geo_col=geo_col, sep=separator
    )

    if reshape_col is not None:
        df = df.reshape_wide_to_long(value_id_column=reshape_col)
        columns = df.columns.to_list()
        df_json = df.to_json()

    else:
        columns = df.data.columns.to_list()
        df_json = df.data.to_json()

    return df_json, columns
