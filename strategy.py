from indicators import add_indicators

def check_signal(df):
    df = add_indicators(df)

    last = df.iloc[-1]

    buy = (
        last["EMA20"] > last["EMA50"]
        and last["close"] > last["SUPERTREND"]
        and last["ADX"] > 25
    )

    sell = (
        last["EMA20"] < last["EMA50"]
        and last["close"] < last["SUPERTREND"]
        and last["ADX"] > 25
    )

    if buy:
        return "BUY"

    if sell:
        return "SELL"

    return "WAIT"
