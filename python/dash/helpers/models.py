import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from typing import Tuple

from .layout import get_time_marks
from .smoothing import multivariate_ES
from preprocessing.parse import merge_dataframes, merge_dataframes_multi


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

    df["ds"] = df["ds"].replace(to_replace=time, value=time_range)

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


def fit_and_predict(
    df: pd.DataFrame,
    time_column: str,
    feature_column: str,
    frequency: str,
    periods: int,
    model: str,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Fits a scikit-learn model to given dataframe and returns predictions for set amount of periods

    Args:
        df (pd.DataFrame): dataframe
        time_column (str): value of time column
        feature_column (str): value of feature column
        frequency (str): time frequency in the given dataframe such as yearly
        periods (int): amount of future time periods to predict
        model (str): name of scikit-learn model to use

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: forecast dataframe, original dataframe
    """

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

    df[time_column] = df[time_column].replace(to_replace=time, value=time_range)

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


def var_fit_and_predict_multi(
    dataframes,
    time_columns,
    feature_columns,
    max_lags,
    periods,
    frequency,
):

    frequencies = {
        "Yearly": ("AS", 365),
        "Monthly": ("MS", 30),
        "Weekly": ("W", 7),
        "Daily": ("D", 1),
    }

    merged_df, time = merge_dataframes_multi(dataframes, time_columns)

    marks = get_time_marks(merged_df, time_column=time, frequency=frequency)

    merged_df[time] = pd.to_datetime(merged_df[time].astype(str))

    merged_df_diff = merged_df[feature_columns].diff().astype("float32").dropna()

    model = VAR(merged_df_diff)

    result = model.fit(maxlags=max_lags)

    forecast = result.forecast(merged_df_diff[-max_lags:].values, periods)

    forecast_df = pd.DataFrame()

    forecast_df[time] = pd.date_range(
        start=marks[1], periods=periods, freq=frequencies[frequency][0]
    )

    forecast_df[feature_columns] = forecast

    df_final = pd.concat([merged_df, forecast_df], ignore_index=True)

    df_final.loc[len(merged_df) - 1 :, feature_columns] = df_final[feature_columns][
        len(merged_df) - 1 :
    ].cumsum()

    return df_final, marks


def hw_es_fit_and_predict_multi(
    dataframes,
    time_columns,
    feature_columns: list,
    frequency,
    periods,
    alpha,
):

    frequencies = {
        "Yearly": ("AS", 365),
        "Monthly": ("MS", 30),
        "Weekly": ("W", 7),
        "Daily": ("D", 1),
    }

    merged_df, time = merge_dataframes_multi(dataframes, time_columns)

    marks = get_time_marks(merged_df, time_column=time, frequency=frequency)

    merged_df[time] = pd.to_datetime(merged_df[time].astype(str))

    df_features = (
        merged_df[feature_columns]
        .reset_index(drop=True)
        .reindex(sorted(feature_columns), axis=1)
        .rename(columns={feature: i for i, feature in enumerate(feature_columns)})
    )

    forecast = []

    for t in range(periods):
        test = multivariate_ES(
            df_features, len(df_features), t + 1, len(feature_columns), alpha
        )
        forecast.append(test[-1])

    forecast_df = pd.DataFrame()

    forecast_df[time] = pd.date_range(
        start=marks[1], periods=periods, freq=frequencies[frequency][0]
    )

    for i, feature in enumerate(sorted(feature_columns)):
        forecast_df[feature] = [x[i] for x in forecast]

    df_final = pd.concat([merged_df, forecast_df], ignore_index=True)

    return df_final, marks


def prophet_fit_and_predict_n(
    dataframes, time_columns, feature_columns, scenarios, frequency, y_feature_index
):

    frequencies = {
        "Yearly": ("AS", 365),
        "Monthly": ("MS", 30),
        "Weekly": ("W", 7),
        "Daily": ("D", 1),
    }

    merged_df, time = merge_dataframes_multi(dataframes, time_columns)

    # if feature_column_1 == feature_column_2:
    #     feature_column_1 += "_x"
    #     feature_column_2 += "_y"

    y_feature = feature_columns.pop(y_feature_index)

    merged_df = merged_df.rename(columns={time: "ds", y_feature: "y"})

    merged_df["ds"] = pd.to_datetime(merged_df["ds"].astype(str))

    model = Prophet()

    for feature in feature_columns:
        model.add_regressor(feature)

    model.fit(merged_df)

    scenario_min_len = len(min(scenarios, key=len))
    future = model.make_future_dataframe(
        periods=scenario_min_len, freq=frequencies[frequency][0]
    )

    for feature, scenario in zip(feature_columns, scenarios):
        artificial_scenario = np.append(
            merged_df[feature].values,
            scenario[:scenario_min_len],
        )

        future[feature] = artificial_scenario

    predictions = model.predict(future)

    forecast = predictions[len(merged_df) :][["ds", "yhat", "yhat_upper", "yhat_lower"]]

    future_df = future[len(merged_df) - 1 :][["ds", *feature_columns]]

    return forecast, merged_df, future_df, y_feature
