import pandas as pd
import pandas_ta as ta

def add_indicators(df):
    df["EMA20"] = ta.ema(df["close"], length=20)
    df["EMA50"] = ta.ema(df["close"], length=50)

    st = ta.supertrend(
        df["high"],
        df["low"],
        df["close"],
        length=10,
        multiplier=3.0
    )

    df["SUPERTREND"] = st.iloc[:, 0]
    df["ADX"] = ta.adx(df["high"], df["low"], df["close"])["ADX_14"]
    df["ATR"] = ta.atr(df["high"], df["low"], df["close"], length=14)

    return df
