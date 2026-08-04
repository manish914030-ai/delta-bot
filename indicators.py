import pandas as pd

def add_indicators(df):
    # EMA
    df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()

    # Temporary Supertrend (EMA20 as placeholder)
    df["SUPERTREND"] = df["EMA20"]

    # Temporary ADX
    df["ADX"] = 30

    return df
