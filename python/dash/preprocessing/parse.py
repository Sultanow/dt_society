from typing import Tuple
from dash import html
import pandas as pd
import base64
import io

from .dataset import DigitalTwinTimeSeries


def parse_dataset(
    contents: str,
    get_countries: bool = False,
    geo_col: str = None,
    upload_file: bool = True,
    separator: str = "\t",
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
            # _, content_string = contents.split(",")

            decoded = base64.b64decode(contents)

            df = DigitalTwinTimeSeries(
                io.StringIO(decoded.decode("utf-8")), geo_col=geo_col, sep=separator
            )
        except Exception as e:
            print(e)
            return html.Div(["There was an error processing this file."])
    else:
        df = DigitalTwinTimeSeries(contents, geo_col="geo\\time", sep=separator)

    columns = df.data.columns.to_list()

    df_json = df.data.to_json()

    if get_countries:
        countries = df.data[geo_col].unique().tolist()
        return df_json, columns, countries
    else:
        return df_json, columns


def get_available_columns(
    contents: str, upload_file: bool = True, separator: str = "\t"
):
    if upload_file:
        try:
            _, content_string = contents.split(",")

            decoded = base64.b64decode(content_string)

            data = pd.read_csv(io.StringIO(decoded.decode("utf-8")), sep=separator)
        except Exception as e:
            print(e)
            return html.Div(["There was an error processing this file."])
    else:
        data = pd.read_csv(io.BytesIO(contents), sep=separator)

    columns = data.columns.tolist()

    fused_cols_i = None

    for col in columns:
        # Check for columns with multiple sub values
        if "," in col:
            fused_cols_i = columns.index(col)
            # Create seperate columns for each sub column
            meta_column = data.columns[fused_cols_i].split(",")
            n_meta_columns = len(meta_column)

            data[meta_column] = data.iloc[:, fused_cols_i].str.split(",", expand=True)
            data = data.drop(data.columns[fused_cols_i], axis=1)

            # Restore original column order
            data = data[
                data.columns[-n_meta_columns:].tolist()
                + data.columns[:-n_meta_columns].tolist()
            ]

    return data.columns.to_list()
