import pandas as pd

def add_indicators(df):
    df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()

    df["SUPERTREND"] = df["EMA20"]
    df["ADX"] = 25
    df["ATR"] = (df["high"] - df["low"]).rolling(14).mean()

    return df
