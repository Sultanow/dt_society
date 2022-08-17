import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
from typing import Tuple


def prophet_fit_and_predict(
    df: pd.DataFrame,
    time_column: str,
    feature_column: str,
    periods: int,
    frequency: str,
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

    time = np.sort(df["ds"].unique())

    frequencies = {"Yearly": "AS", "Monthly": "MS", "Weekly": "W", "Daily": "D"}

    time_range = pd.date_range(
        start=str(time[0]), end=str(time[-1]), freq=frequencies[frequency]
    )

    df = df.replace(to_replace=time, value=time_range)

    model = Prophet()

    model.fit(df)

    future = model.make_future_dataframe(periods=periods, freq=frequencies[frequency])

    predictions = model.predict(future)[["ds", "yhat", "yhat_upper", "yhat_lower"]]

    df["yhat"] = predictions[: len(df)]["yhat"].values

    forecast = predictions[len(df) :][["ds", "yhat"]]

    forecast["error"] = (
        predictions["yhat_upper"][len(df) :] - predictions["yhat_lower"][len(df) :]
    )
    return forecast, df


def fit_and_predict(df, time_column, feature_column, frequency, periods, model: str):

    models = {
        "Regression": LinearRegression(),
    }

    frequencies = {
        "Yearly": ("AS", 365),
        "Monthly": ("MS", 30),
        "Weekly": ("W", 7),
        "Daily": ("D", 1),
    }

    time = np.sort(df[time_column].unique())

    time_range = pd.date_range(
        start=str(time[0]), end=str(time[-1]), freq=frequencies[frequency][0]
    )

    df = df.replace(to_replace=time, value=time_range)

    future_start = time_range[-1] + pd.Timedelta(
        np.timedelta64(1 * frequencies[frequency][-1], "D")
    )

    future_end = time_range[-1] + pd.Timedelta(
        np.timedelta64(periods * frequencies[frequency][-1], "D")
    )

    future = pd.date_range(
        start=future_start, end=future_end, freq=frequencies[frequency][0]
    )

    model = models[model]

    x = np.expand_dims(df[time_column], axis=1)

    model.fit(X=x.astype("float64"), y=df[feature_column])

    model_fit = model.predict(x.astype("float64"))

    rmse = np.sqrt(mean_squared_error(df[feature_column], model_fit))

    rmse = np.repeat(rmse, future.size)

    forecast = model.predict(np.expand_dims(future, axis=1).astype("float64"))

    f = {"ds": future, "yhat": forecast, "error": rmse}

    f_df = pd.DataFrame(f)

    df = df.rename(columns={time_column: "ds", feature_column: "y"})

    df["yhat"] = model_fit

    return f_df, df
