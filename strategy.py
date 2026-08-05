from indicators import add_indicators
import json
import os

SIGNAL_FILE = "last_signal.json"


def load_last_signal(symbol):
    if os.path.exists(SIGNAL_FILE):
        try:
            with open(SIGNAL_FILE, "r") as f:
                data = json.load(f)
                return data.get(symbol)
        except:
            return None
    return None


def save_last_signal(symbol, signal):
    data = {}

    if os.path.exists(SIGNAL_FILE):
        try:
            with open(SIGNAL_FILE, "r") as f:
                data = json.load(f)
        except:
            data = {}

    data[symbol] = signal

    with open(SIGNAL_FILE, "w") as f:
        json.dump(data, f)


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

    signal = "WAIT"

    if buy:
        signal = "BUY"
    elif sell:
        signal = "SELL"

    symbol = last.get("symbol", "UNKNOWN")
    last_signal = load_last_signal(symbol)

    if signal == last_signal:
        return "WAIT"

    if signal != "WAIT":
        save_last_signal(symbol, signal)

    return signal
