import pandas as pd

def add_indicators(df):
    # EMA
    df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()

    # ATR (14)
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()

    # Real Supertrend
    hl2 = (df["high"] + df["low"]) / 2
    df["SUPERTREND"] = hl2 - (3 * atr)

    # Simple ADX placeholder
    df["ADX"] = atr.fillna(20)

    return df
