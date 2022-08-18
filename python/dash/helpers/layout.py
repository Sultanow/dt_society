import gzip
import base64
import urllib
from dash import (
    no_update,
    html,
    callback_context,
)
import json
import numpy as np
import pandas as pd
import time

from preprocessing.parse import parse_dataset


def preprocess_dataset(
    delimiter_value: str,
    geo_column_value: str,
    file_content: str,
    file_name: str,
    reshape_column_value: str,
    reshape_switch_status: bool,
    file_upload_children: str,
    demo_button_n_clicks: int,
    demo_dataset_n: str,
    preset_file: str = None,
) -> tuple:

    changed_item = [p["prop_id"] for p in callback_context.triggered][0]

    show_error_notification = no_update

    saved_preset_file = None

    if "demo-button" in changed_item or "table-upload" in changed_item:
        reshape_switch_status = False
        delimiter_value = None
        geo_column_value = None

    if preset_file is not None:
        _, content = preset_file.split(",")
        decoded = base64.b64decode(content)
        preset = json.loads(decoded)

        delimiter_value = preset["separator"]
        geo_column_value = preset["geo-column"]
        reshape_switch_status = preset["reshape"]
        reshape_column_value = preset["reshape-column"]
        time_column_value = preset["time-column"]
        feature_column_value = preset["feature-column"]

    else:
        time_column_value = no_update
        feature_column_value = no_update

    if "demo-button" in changed_item:
        demo_data = {
            "Demo 1": (
                "arbeitslosenquote_eu.tsv",
                "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tipsun20.tsv.gz",
            ),
            "Demo 2": (
                "bip_europa.tsv",
                "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tec00001.tsv.gz",
            ),
        }
        file_name = demo_data[demo_dataset_n][0]
        df_url = demo_data[demo_dataset_n][1]

        content = urllib.request.urlopen(df_url).read()
        content = gzip.decompress(content)
        file_content = base64.b64encode(content).decode("utf-8")
        delimiter_value = "\t"

    if delimiter_value:

        if delimiter_value == "\\t":
            delimiter_value = "\t"

        if not geo_column_value:
            geo_column_value = "None"

        if not reshape_switch_status:
            reshape_column_value = None

        try:
            content = file_content.split(",")
            df, columns, columns_pre_reshape = parse_dataset(
                content[-1],
                separator=delimiter_value,
                geo_col=geo_column_value,
                reshape_col=reshape_column_value,
            )

        except Exception as e:
            print(e)
            show_error_notification = True
            file_upload_children["props"]["children"] = html.Div(
                [
                    "Drag and Drop or ",
                    html.A("Select Files"),
                ]
            )
            return (
                no_update,  # data
                no_update,  # geo-dropdown-options
                no_update,  # reshape-dropdown-options
                file_upload_children,  # file-name-container
                no_update,  # feature-dropdown-options
                no_update,  # time-dropdown-options
                no_update,  # table-upload-content
                None,  # delimiter-dropdown-value
                no_update,  # file-name
                no_update,  # reshape-swtich-status
                no_update,  # geo-dropdown-value
                show_error_notification,  # dataset-fail-display
                no_update,  # feature-dropdown-value
                no_update,  # time-dropdown-value
                no_update,  # reshape-column-value
            )

        geo_options = columns
        feature_options = [col for col in columns if col != geo_column_value]
        time_options = [col for col in columns if col != geo_column_value]

        if reshape_column_value:
            reshape_options = no_update
        elif preset_file is not None:
            reshape_options = columns_pre_reshape
        else:
            reshape_options = columns

        if preset_file is None:
            geo_column_value = no_update
            reshape_column_value = no_update

    else:
        df = no_update
        geo_options = no_update
        reshape_options = no_update
        feature_options = no_update
        time_options = no_update

    file_upload_children["props"]["children"] = html.Div([file_name])

    if delimiter_value == "\t":
        delimiter_value = "\\t"

    return (
        df,
        geo_options,
        reshape_options,
        file_upload_children,
        feature_options,
        time_options,
        file_content,
        delimiter_value,
        file_name,
        reshape_switch_status,
        geo_column_value,
        show_error_notification,
        feature_column_value,
        time_column_value,
        saved_preset_file,
        reshape_column_value,
    )


def export_settings(
    delimiter_value: str,
    geo_column_value: str,
    reshape_column_value: str,
    reshape_switch_status: str,
    time_column_value: str,
    feature_column_value: str,
    filename: str,
) -> dict:

    if (
        delimiter_value
        and geo_column_value
        and time_column_value
        and feature_column_value
    ):
        preset = {
            "separator": delimiter_value,
            "geo-column": geo_column_value,
            "reshape": reshape_switch_status,
            "reshape-column": reshape_column_value,
            "time-column": time_column_value,
            "feature-column": feature_column_value,
        }
        timestamp = int(time.time())
        filename = filename.split(".")[0]

        return dict(
            content=json.dumps(preset),
            filename=f"preset_{filename}_{timestamp}.json",
        )


def get_year_and_country_options_stats(
    df: pd.DataFrame, geo_column: str, time_column: str
):

    if geo_column != None:

        geo_options = df[geo_column].unique()
        geo_selection = geo_options[0]
    else:
        geo_options = no_update
        geo_selection = no_update

    time_options = np.sort(df[time_column].unique())

    time_selection = time_options[0]
    time_min = 0
    time_max = time_options.size - 1

    time_span = [time_min, time_max]

    if isinstance(time_selection, np.datetime64):
        time_selection = np.datetime_as_string(time_selection)

    return (
        time_options,
        time_selection,
        geo_options,
        geo_selection,
        time_options,
        time_selection,
        time_min,
        time_max,
        geo_options,
        geo_options[0],
        geo_options,
        geo_options[0],
        time_span,
    )


def compute_stats(
    df: pd.DataFrame,
    feature_column: str,
    geo_column: str,
) -> tuple:

    mean = round(df[feature_column].mean(axis=0), 2)
    max = round(df[feature_column].max(), 2)
    min = round(df[feature_column].min(), 2)

    country_max = df.loc[df[feature_column].idxmax()][geo_column]
    country_min = df.loc[df[feature_column].idxmin()][geo_column]

    return (
        mean,
        max,
        min,
        country_max,
        country_min,
    )


def compute_growth_rate(
    df: pd.DataFrame, feature_column: str, time_span: list
) -> tuple:

    start_value = df[feature_column].sort_values().values[time_span[0]]
    end_value = df[feature_column].sort_values().values[time_span[-1]]
    growth_rate = ((end_value - start_value) / end_value) * 100

    return round(growth_rate, 2)
