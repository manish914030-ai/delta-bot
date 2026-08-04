import pandas as pd
import pandas_ta as ta

def add_indicators(df):
    # EMA
    df["EMA20"] = ta.ema(df["close"], length=20)
    df["EMA50"] = ta.ema(df["close"], length=50)

    # Supertrend
    st = ta.supertrend(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        length=10,
        multiplier=3.0
    )
    df["SUPERTREND"] = st["SUPERT_10_3.0"]

    # ADX
    adx = ta.adx(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        length=14
    )
    df["ADX"] = adx["ADX_14"]

    return df
