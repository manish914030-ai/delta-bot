import pandas as pd

def add_indicators(df):
    df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()

    df["SUPERTREND"] = (
        df["high"].rolling(10).max() +
        df["low"].rolling(10).min()
    ) / 2

    high_low = df["high"] - df["low"]
    df["ADX"] = high_low.rolling(14).mean().fillna(20)

    return df
