import pandas as pd
from prophet import Prophet
from typing import Tuple


def prophet_fit_and_predict(
    df: pd.DataFrame, time_column: str, feature_column: str, periods: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Fits a Prophet model to given dataframe and returns predictions for set amount of periods

    Args:
        df (pd.DataFrame): Dataset
        time_column (str): name of the column that contains time data
        feature_column (str): name of the column that contains feature data
        periods (int): amount of future periods to make predictions for

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Dataframe with forecast data and original dataframe
    """

    df = df.rename(columns={time_column: "ds", feature_column: "y"})

    df["ds"] = pd.to_datetime(df["ds"], format="%Y")

    model = Prophet()

    model.fit(df)

    future = model.make_future_dataframe(periods=periods, freq="AS")

    forecast = model.predict(future)[["ds", "yhat", "yhat_upper", "yhat_lower"]]

    return forecast, df
