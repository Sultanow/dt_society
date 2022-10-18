from typing import Tuple
import base64
import io
import pandas as pd
from typing import List

from .dataset import DigitalTwinTimeSeries

# from flask_caching import Cache
from ..extensions import cache
from ..extensions import mongo


@cache.memoize(timeout=30)
def parse_dataset(geo_column, dataset_id, reshape_column=None) -> pd.DataFrame:

    collection = mongo.db["collection_1"]

    if isinstance(dataset_id, int):
        file_path = collection.find({})[dataset_id]
    elif isinstance(dataset_id, str):
        file_path = collection.find({"filename": dataset_id})[0]

    # file_path = session["files"][dataset_id]

    df = DigitalTwinTimeSeries(file_path["data"], geo_col=geo_column, sep="dict")

    if reshape_column is not None:
        df = df.reshape_wide_to_long(value_id_column=reshape_column)

    else:
        df = df.data

    return df


def merge_dataframes(dataframe_1, dataframe_2, time_column_1, time_column_2):

    merged_df = pd.merge(
        dataframe_1,
        dataframe_2,
        left_on=[time_column_1],
        right_on=[time_column_2],
        how="inner",
    )

    if time_column_1 != time_column_2:
        if len(dataframe_1[time_column_1]) > len(dataframe_2[time_column_2]):
            column_to_drop = time_column_2
            time = time_column_1

        elif len(dataframe_1[time_column_1]) < len(dataframe_2[time_column_2]):
            column_to_drop = time_column_1
            time = time_column_2

        merged_df = merged_df.drop(columns=[column_to_drop])
    else:
        time = time_column_1

    return merged_df, time


def merge_dataframes_multi(
    dataframes: List[pd.DataFrame], time_columns: List[str]
) -> Tuple[pd.DataFrame, str]:
    """Merges all dataframes along timestamp intersection

    Args:
        dataframes (List[pd.DataFrame]): available datasets
        time_columns (List[str]): selected time columns

    Returns:
        Tuple[pd.DataFrame, str]: merged dataframe, name of time column in merged dataframe
    """

    merged_df = None
    for i in range(len(dataframes) - 1):

        if merged_df is None:
            merged_df = pd.merge(
                dataframes[i],
                dataframes[i + 1],
                left_on=[time_columns[i]],
                right_on=[time_columns[i + 1]],
            )

        else:
            merged_df = pd.merge(
                merged_df,
                dataframes[i + 1],
                left_on=[time_columns[i]],
                right_on=[time_columns[i + 1]],
            )

        if time_columns[i] != time_columns[i + 1]:
            merged_df = merged_df.drop(columns=[time_columns[i]])

        time_col = time_columns[i + 1]

    return merged_df, time_col
