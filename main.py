import time
import pandas as pd

from exchange import exchange
from strategy import check_signal
from telegram_bot import send_message

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XAUUSD"]
TIMEFRAME = "5m"


def get_candles(symbol, timeframe="5m", limit=200):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    df = pd.DataFrame(
        ohlcv,
        columns=["time", "open", "high", "low", "close", "volume"]
    )

    return df


def run():
    print("Delta Bot Started...")
    send_message("✅ Delta Bot Started Successfully")

    while True:
        for symbol in SYMBOLS:
            try:
                df = get_candles(symbol, TIMEFRAME)
                signal = check_signal(df)

                print(f"{symbol}: {signal}")

                if signal != "WAIT":
                    send_message(
                        f"🚨 Signal Alert\n\n"
                        f"Symbol: {symbol}\n"
                        f"Signal: {signal}"
                    )

            except Exception as e:
                print(symbol, e)

        time.sleep(60)


if __name__ == "__main__":
    run()
