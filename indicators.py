from indicators import add_indicators

def check_signal(df):
    df = add_indicators(df)

    last = df.iloc[-1]

    # BUY
    if (
        last["EMA20"] > last["EMA50"]
        and last["close"] > last["SUPERTREND"]
        and last["ADX"] > 20
    ):
        return "BUY"

    # SELL
    elif (
        last["EMA20"] < last["EMA50"]
        and last["close"] < last["SUPERTREND"]
        and last["ADX"] > 20
    ):
        return "SELL"

    return None
