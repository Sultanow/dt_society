from typing import List
from typing import Tuple
import pandas as pd

from .dataset import DigitalTwinTimeSeries
from ..extensions import cache, mongo


@cache.memoize(timeout=90)
def parse_dataset(
    geo_column,
    dataset_id,
    session_id,
    reshape_column=None,
    selected_feature: str = None,
) -> Tuple[pd.DataFrame, str]:
    """_summary_

    Args:
        geo_column (_type_): _description_
        dataset_id (_type_): _description_
        reshape_column (_type_, optional): _description_. Defaults to None.

    Returns:
        pd.DataFrame: _description_
    """

    collection = mongo.db[session_id]

    if isinstance(dataset_id, int):
        file_path = collection.find({})[dataset_id]
    elif isinstance(dataset_id, str):
        file_path = collection.find_one({"filename": dataset_id})

    df = DigitalTwinTimeSeries(file_path["data"], geo_col=geo_column, sep="dict")

    if selected_feature is not None:
        features_in_columns = df.data.columns.to_list()

        for feature in features_in_columns:
            if selected_feature in df.data[feature].unique().tolist():
                reshape_column = feature

    if reshape_column is not None:
        df = df.reshape_wide_to_long(value_id_column=reshape_column)

    else:
        df = df.data

    return df, reshape_column


@cache.memoize(timeout=90)
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
