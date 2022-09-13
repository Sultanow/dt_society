import gzip
import base64
from math import floor, log
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
    """Preprocesses an uploaded file

    Args:
        delimiter_value (str): value of delimiter
        geo_column_value (str): value of geo column
        file_content (str): content of uploaded file
        file_name (str): name of uploaded file
        reshape_column_value (str): value of column to reshape on
        reshape_switch_status (bool): value of reshape toggle
        file_upload_children (str): container of file uploaded element
        demo_button_n_clicks (int): number of demo button clicks
        demo_dataset_n (str): value of selected demo dataset
        preset_file (str, optional): content of imported preset file. Defaults to None.

    Returns:
        tuple: _description_
    """

    changed_item = [p["prop_id"] for p in callback_context.triggered][0]

    show_error_notification = no_update

    saved_preset_file = None

    if "demo-button" in changed_item or "table-upload" in changed_item:
        reshape_switch_status = False
        delimiter_value = None
        geo_column_value = None

    if "reset-button" in changed_item:
        reshape_switch_status = False
        delimiter_value = None
        geo_column_value = None
        file_name = None
        reshape_column_value = None

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
            "Demo 0": (
                "arbeitslosenquote_eu.tsv",
                "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/tipsun20.tsv.gz",
            ),
            "Demo 1": (
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

            if "too many values to unpack" in str(e):
                error = "Chosen separator does not match separator in file."
                delimiter_value = None

                file_upload_children["props"]["children"] = html.Div(
                    [
                        "Drag and Drop or ",
                        html.A("Select Files"),
                    ]
                )
            elif preset_file and preset["file-name"] != file_name:
                error = (
                    "Filename in preset does not match filename of uploaded dataset."
                )

            else:
                error = str(e)

                if delimiter_value == "\t":
                    delimiter_value = "\\t"

                if "Column did not contain correct country codes" in error:
                    geo_column_value = None

                if (
                    "Column to reshape on can not be the column that has been set as geo column"
                    in error
                ):
                    if reshape_switch_status:
                        reshape_switch_status = False

                    reshape_column_value = None

            print(e)

            show_error_notification = True

            return (
                no_update,  # data
                no_update,  # geo-dropdown-options
                no_update,  # reshape-dropdown-options
                file_upload_children,  # file-name-container
                no_update,  # feature-dropdown-options
                no_update,  # time-dropdown-options
                no_update,  # table-upload-content
                delimiter_value,  # delimiter-dropdown-value
                no_update,  # file-name
                reshape_switch_status,  # reshape-swtich-status
                geo_column_value,  # geo-dropdown-value
                show_error_notification,  # dataset-fail-display
                no_update,  # feature-dropdown-value
                no_update,  # time-dropdown-value
                no_update,  # preset-upload-content
                reshape_column_value,  # reshape-column-value
                error,  # dataset-fail-message
            )

        geo_options = columns
        feature_options = [col for col in columns if col != geo_column_value]
        time_options = [col for col in columns if col != geo_column_value]

        if reshape_column_value:
            reshape_options = no_update
        elif preset_file is not None:
            reshape_options = ["None"] + columns_pre_reshape
        else:
            reshape_options = ["None"] + columns

        if preset_file is None:
            geo_column_value = no_update
            reshape_column_value = no_update

    else:
        if "reset-button" in changed_item:
            df = None
            geo_options = []
            reshape_options = []
            feature_options = []
            time_options = []
        else:
            df = (
                geo_options
            ) = reshape_options = feature_options = time_options = no_update

    if "reset-button" in changed_item:
        file_upload_children["props"]["children"] = html.Div(
            [
                "Drag and Drop or ",
                html.A("Select Files"),
            ]
        )
    else:
        file_upload_children["props"]["children"] = html.Div(
            [file_name],
            style={
                "text-overflow": "ellipsis",
                "overflow": "hidden",
                "white-space": "nowrap",
            },
        )

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
        no_update,
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
    """Downloads a JSON file containing the selected values for each dropdown. Resulting file can be imported as preset.

    Args:
        delimiter_value (str): value of delimiter
        geo_column_value (str): value of geo column
        reshape_column_value (str): value of reshape column
        reshape_switch_status (str): status of reshape toggle
        time_column_value (str): value of time column
        feature_column_value (str): value of feature column
        filename (str): name of the uploaded dataset

    Raises:
        exceptions.PreventUpdate: Update prevented unless button is pressed

    Returns:
        dict: JSON object, file name
    """

    if (
        delimiter_value
        and geo_column_value
        and time_column_value
        and feature_column_value
    ):
        preset = {
            "file-name": filename,
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
) -> tuple:
    """Creates options for time and country dropdown in statistics section. Slider receives labels based on time data.

    Args:
        df (pd.DataFrame): Data
        geo_column (str): value of column with geo data
        time_column (str): value of column with time data

    Returns:
        tuple: _description_
    """

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

    n_chunks = 7 if len(time_options) >= 7 else 3

    if np.issubdtype(np.datetime64, df[time_column]):
        time_options_strp = np.sort(df[time_column].dt.strftime("%b-%d").unique())
        time_options_split = np.array(
            np.array_split(time_options_strp, n_chunks), dtype="object"
        )
    else:
        time_options_split = np.array(
            np.array_split(time_options, n_chunks), dtype="object"
        )

    marks = {}

    for i, a in enumerate(time_options_split):

        if i != 0:
            value = a[-1]
            key = np.where(np.hstack(time_options_split) == value)[0]

        else:
            value = a[0]
            key = time_min

            marks[int(key) + (len(a) - 1)] = str(a[-1])

        marks[int(key)] = str(value)

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
        marks,
    )


def compute_stats(
    df: pd.DataFrame,
    feature_column: str,
    geo_column: str,
) -> tuple:
    """Compute statistics of a given dataset

    Args:
        df (pd.DataFrame): dataframe
        feature_column (str): value of feature column
        geo_column (str): value of geo column

    Returns:
        tuple: mean, max, min, country name of max, country name of min
    """

    def human_format(number):
        units = ["", "K", "M", "G", "T", "P"]
        k = 1000.0
        if number != 0.0 and number >= 1:
            magnitude = int(floor(log(number, k)))
        else:
            magnitude = 0
        return "%.2f%s" % (number / k**magnitude, units[magnitude])

    mean = round(df[feature_column].mean(axis=0), 2)
    max = round(df[feature_column].max(), 2)
    min = round(df[feature_column].min(), 2)

    country_max = df.loc[df[feature_column].idxmax()][geo_column]
    country_min = df.loc[df[feature_column].idxmin()][geo_column]

    return (
        human_format(mean),
        human_format(max),
        human_format(min),
        country_max,
        country_min,
    )


def compute_growth_rate(
    df: pd.DataFrame, feature_column: str, time_span: list
) -> float:
    """Computes the growth rate of a feature in a given time window

    Args:
        df (pd.DataFrame): dataframe
        feature_column (str): name of feature column
        time_span (list): list defining the time window

    Returns:
        float: growth rate
    """

    start_value = df[feature_column].sort_values().values[time_span[0]]
    end_value = df[feature_column].sort_values().values[time_span[-1]]
    growth_rate = ((end_value - start_value) / end_value) * 100

    return round(growth_rate, 2)


def get_time_marks(df: pd.DataFrame, time_column: str, frequency: str) -> dict:
    """Creates dictionary to assign time labels to slider marks

    Args:
        df (pd.DataFrame): Data
        time_column (str): value of column containing time data
        frequency (str): frequency of underlying time data

    Returns:
        dict: key value pairs ( slider mark:label )
    """
    frequencies = {
        "Yearly": ("AS", 365, "%Y"),
        "Monthly": ("MS", 30, "%b-%Y"),
        "Weekly": ("W", 7, "%Y-%m-%d"),
        "Daily": ("D", 1, "%Y-%b-%d"),
    }

    time_max = pd.to_datetime(str(df[time_column].max()), infer_datetime_format=True)

    future_start = time_max + pd.Timedelta(
        np.timedelta64(1 * frequencies[frequency][1], "D")
    )

    future_range = np.array(
        pd.date_range(
            start=future_start, periods=30, freq=frequencies[frequency][0]
        ).strftime(frequencies[frequency][2])
    )

    future_range_slice = future_range[::3]

    marks = {}

    for i, date in enumerate(future_range_slice):

        marks[i * 3 + 1] = str(date)

        if i == len(future_range_slice) - 1:
            marks[len(future_range)] = future_range[-1]

    return marks
