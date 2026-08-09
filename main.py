import time
import pandas as pd

from exchange import exchange
from strategy import check_signal
from telegram_bot import send_message


# ============================================================
# DELTA TITAN AI - MAIN ENGINE
# ============================================================

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT"
]

TIMEFRAME = "5m"

# Exchange se maximum candles lene ki koshish
CANDLE_LIMIT = 300

# Strategy ke liye minimum required candles
MIN_CANDLES = 210


# ============================================================
# LAST SIGNAL MEMORY
# ============================================================

last_signals = {
    symbol: "WAIT"
    for symbol in SYMBOLS
}


# ============================================================
# GET MARKET CANDLES
# ============================================================

def get_candles(symbol, timeframe="5m", limit=300):

    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe=timeframe,
        limit=limit
    )

    df = pd.DataFrame(
        ohlcv,
        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


# ============================================================
# MAIN BOT LOOP
# ============================================================

def run():

    print(
        "==================================================",
        flush=True
    )

    print(
        "🚀 DELTA TITAN AI BOT STARTED",
        flush=True
    )

    print(
        f"Timeframe : {TIMEFRAME}",
        flush=True
    )

    print(
        f"Requested Candles : {CANDLE_LIMIT}",
        flush=True
    )

    print(
        f"Minimum Candles   : {MIN_CANDLES}",
        flush=True
    )

    print(
        f"Symbols : {', '.join(SYMBOLS)}",
        flush=True
    )

    print(
        "==================================================",
        flush=True
    )

    send_message(
        "✅ Delta Titan AI Bot Started Successfully\n\n"
        f"📊 Timeframe: {TIMEFRAME}\n"
        f"📈 Symbols: {', '.join(SYMBOLS)}"
    )

    while True:

        for symbol in SYMBOLS:

            try:

                # ------------------------------------------------
                # FETCH MARKET DATA
                # ------------------------------------------------

                df = get_candles(
                    symbol,
                    TIMEFRAME,
                    CANDLE_LIMIT
                )

                # ------------------------------------------------
                # NO DATA
                # ------------------------------------------------

                if df is None or df.empty:

                    print(
                        f"{symbol} -> NO DATA",
                        flush=True
                    )

                    continue

                # ------------------------------------------------
                # MINIMUM DATA CHECK
                # ------------------------------------------------
                # 300 exact candles compulsory nahi.
                # 210+ candles strategy ke liye sufficient hain.

                if len(df) < MIN_CANDLES:

                    print(
                        f"{symbol} -> "
                        f"INSUFFICIENT DATA "
                        f"({len(df)}/{MIN_CANDLES})",
                        flush=True
                    )

                    continue

                # ------------------------------------------------
                # ADD SYMBOL
                # ------------------------------------------------

                df["symbol"] = symbol

                # ------------------------------------------------
                # STRATEGY
                # ------------------------------------------------

                signal = check_signal(df)

                print(
                    f"{symbol} -> {signal} "
                    f"({len(df)} candles)",
                    flush=True
                )

                # ------------------------------------------------
                # CURRENT CLOSED CANDLE PRICE
                # ------------------------------------------------

                current_price = df["close"].iloc[-2]

                # ------------------------------------------------
                # SIGNAL CHANGE DETECTION
                # ------------------------------------------------

                previous_signal = last_signals.get(
                    symbol,
                    "WAIT"
                )

                # ------------------------------------------------
                # NEW BUY / SELL SIGNAL
                # ------------------------------------------------

                if (
                    signal in ["BUY", "SELL"]
                    and signal != previous_signal
                ):

                    send_message(
                        f"🚨 SIGNAL ALERT\n\n"
                        f"Symbol: {symbol}\n"
                        f"Signal: {signal}\n"
                        f"Timeframe: {TIMEFRAME}\n"
                        f"Price: {current_price}"
                    )

                    print(
                        f"📢 NEW SIGNAL -> "
                        f"{symbol} {signal}",
                        flush=True
                    )

                # ------------------------------------------------
                # SAVE CURRENT SIGNAL
                # ------------------------------------------------

                last_signals[symbol] = signal

            except Exception as e:

                print(
                    f"{symbol} ERROR: {e}",
                    flush=True
                )

        # --------------------------------------------------------
        # WAIT
        # --------------------------------------------------------

        print(
            "⏳ Waiting 5 minutes...",
            flush=True
        )

        time.sleep(300)


# ============================================================
# START BOT
# ============================================================

if __name__ == "__main__":
    run()
