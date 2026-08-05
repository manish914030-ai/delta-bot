import os
from indicators import add_indicators

SIGNAL_FILE = "last_signal.txt"


def load_last_signal():
    if os.path.exists(SIGNAL_FILE):
        with open(SIGNAL_FILE, "r") as f:
            return f.read().strip()
    return ""


def save_last_signal(signal):
    with open(SIGNAL_FILE, "w") as f:
        f.write(signal)


def check_signal(df):
    df = add_indicators(df)
    last = df.iloc[-1]

    buy = (
        last["EMA20"] > last["EMA50"]
        and last["close"] > last["SUPERTREND"]
        and last["RSI"] > 55
        and last["MACD"] > last["MACD_SIGNAL"]
    )

    sell = (
        last["EMA20"] < last["EMA50"]
        and last["close"] < last["SUPERTREND"]
        and last["RSI"] < 45
        and last["MACD"] < last["MACD_SIGNAL"]
    )

    if buy:
        signal = "BUY"
    elif sell:
        signal = "SELL"
    else:
        signal = "WAIT"

    last_signal = load_last_signal()

    if signal == "WAIT":
        return "WAIT"

    if signal == last_signal:
        return "WAIT"

    save_last_signal(signal)
    return signal
