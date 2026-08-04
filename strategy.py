from indicators import add_indicators

last_signal = None

def check_signal(df):
    global last_signal

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

    signal = "WAIT"

    if buy:
        signal = "BUY"
    elif sell:
        signal = "SELL"

    if signal == last_signal:
        return "WAIT"

    last_signal = signal
    return signal
