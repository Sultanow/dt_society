from typing import List
from typing import Tuple
import gridfs
import pandas as pd

from .dataset import DigitalTwinTimeSeries
from ..extensions import cache, mongo


@cache.memoize(timeout=90)
def parse_dataset(
    geo_column: str,
    dataset_id: str,
    session_id: str,
    use_preprocessed: bool = True,
    reshape_column: str = None,
    selected_feature: str = None,
) -> Tuple[pd.DataFrame, str]:
    """
    Preprocess dataset from database

    Args:
        geo_column (str): name of column with geo data
        dataset_id (str): id of dataset in database
        session_id (str): id of the session requesting the dataset
        use_preprocessed (bool, optional): whether to retrieve the dataset in its preprocessed state. Defaults to True.
        reshape_column (str, optional): name of the feature column to reshape on. Defaults to None.
        selected_feature (str, optional): value of selected feature. Reshape column will be inferred from selected feature, if possible. Defaults to None.

    Returns:
        Tuple[pd.DataFrame, str]: Processed dataset, value of inferred reshape column
    """

    bucket = gridfs.GridFS(mongo.db, session_id)

    if use_preprocessed:
        selected_df = bucket.find_one({"id": dataset_id, "state": "processed"})
        return (
            pd.read_json(selected_df.read().decode("utf-8"), orient="records"),
            None,
        )

    else:
        selected_df = (
            bucket.find_one({"id": dataset_id, "state": "original"})
            .read()
            .decode("utf-8")
        )

    df = DigitalTwinTimeSeries(selected_df, geo_col=geo_column, sep="dict")

    if selected_feature is not None and reshape_column is None:
        features_in_columns = df.data.columns.to_list()

        for feature in features_in_columns:
            if selected_feature in df.data[feature].unique().tolist():
                reshape_column = feature

    if reshape_column is not None:
        df = df.reshape_wide_to_long(feature_column=reshape_column)
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
