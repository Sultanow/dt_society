import pandas as pd
import numpy as np


def centered_moving_average(D: pd.DataFrame, year_size):

    # hint: the function is set to work for even numbers of year_size!

    estimated_levels = pd.DataFrame()

    D = D.iloc[0 : 4 * year_size, :]
    for i in range(3 * year_size):

        series = (
            D.iloc[i : i + year_size, :].mean()
            + D.iloc[i + 1 : i + year_size + 1, :].mean()
        ) / 2
        estimated_levels = estimated_levels.append(series, ignore_index=True)

    return estimated_levels


def initialize(data: pd.DataFrame, year_size):

    # INITIALIZING L0, S0, AND T0:

    #   i) First, a centered "year_size"-month moving average is applied to the first four years of data. This yields
    #      3*year_size estimated levels.

    estimated_levels = centered_moving_average(data, year_size)

    #   ii)Then, We subtract the above values from X(year_size/2 + 1) ... X(year_size/2 + 3*year_size), and average
    #      the three amounts for each month, in order to get seasonal effects. Then we standardize seasonal effects
    #      to sum to zero.

    X = data.iloc[int(year_size / 2) : int(year_size / 2 + 3 * year_size), :]

    X.reset_index(drop=True, inplace=True)

    temp = (
        X.iloc[0 : int(3 * year_size), :]
        - estimated_levels.iloc[0 : int(3 * year_size), :]
    )

    S0 = pd.DataFrame()

    for i in range(year_size):
        S0 = S0.append(
            (
                temp.iloc[i, :]
                + temp.iloc[i + year_size, :]
                + temp.iloc[i + 2 * year_size, :]
            )
            / 3,
            ignore_index=True,
        )

    temp = S0.iloc[int(year_size / 2) : year_size, :]
    temp = temp.append(S0.iloc[0 : int(year_size / 2), :], ignore_index=True)
    S0 = temp
    temp = pd.DataFrame()
    for i in range(year_size):
        temp = temp.append(S0.iloc[i, :] - S0.mean(), ignore_index=True)
    S0 = temp

    #   iii)Now we estimate T0, based on the formula from the paper:

    T0 = (
        estimated_levels.iloc[2 * year_size : 3 * year_size].mean()
        - estimated_levels.iloc[year_size - 1 : 2 * year_size - 1].mean()
    ) / year_size

    #   we set L0 to the first data values:

    L0 = data.iloc[0, :]

    return L0, T0, S0


def multivariate_ES(
    data: pd.DataFrame, h_period: int, m: int, year_size: int, alpha: int
):

    A = B = C = np.triu(np.full((year_size, year_size), alpha))

    # input descriptions:
    # data: dataframe used for making the model
    # h_period: length of history periods of dataframe for making the model
    # A: convergent matrix of smoothing constants for L (Level)
    # B: convergent matrix of smoothing constants for T (Trend)
    # C: convergent matrix of smoothing constants for S (Seasonality)
    # m: number of future time-steps that we want to forecast
    # year_size: the number of data points in each year

    L = []
    T = []

    data = data.iloc[-h_period:, :]
    inits = initialize(data, year_size)

    L.append(inits[0])
    T.append(inits[1])

    S = []
    for i in range(inits[2].shape[0]):
        ser = pd.Series(dtype="float64")
        ser = ser.append(inits[2].iloc[i, :])
        ser = ser.fillna(0)
        S.append(ser)

    #     all of seasonal effects- it's just used for plotting the seasonal effects later:
    s = []
    for i in range(inits[2].shape[0]):
        ser = pd.Series(dtype="float64")
        ser = ser.append(inits[2].iloc[i, :])
        s.append(ser)

    #     main loop for the calculations of values of level, trend and seasonality. The values in each step are saved in
    #     the corresponding lists L, T and S:

    for i in range(h_period - 1):

        L.append(
            (A @ (data.iloc[i + 1, :].to_numpy() - S[i % year_size].to_numpy()))
            + ((np.identity(year_size) - A) @ (L[i] + T[i]))
        )  # question: which index of S should be used first time?

        T.append((B @ ((L[i + 1]) - L[i])) + ((np.identity(year_size) - B) @ T[i]))

        S[(i + 1) % year_size] = (C @ (data.iloc[i + 1, :].to_numpy() - L[i + 1])) + (
            (np.identity(year_size) - C) @ S[i % year_size].to_numpy()
        )

        Sframe = pd.DataFrame(S)
        Smean = Sframe.mean()
        for j in range(year_size):
            S[j] = S[j] - Smean

        s.append(S[(i + 1) % year_size])

    #     forecast for m step(s) ahead:

    mves = L[-1] + m * T[-1] + S[(h_period - 1) % year_size]

    #     The function will return L, T, s and the m-step-ahead forcast(s) respectively:

    return pd.DataFrame(L), pd.DataFrame(T), pd.DataFrame(s), mves
