import time
import pandas as pd

from exchange import exchange
from strategy import check_signal
from telegram_bot import send_message


# ============================================================
# DELTA TITAN AI - MAIN ENGINE
# ============================================================

# Trading Symbols
SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT"
]

# Primary timeframe
TIMEFRAME = "5m"

# 300 candles required for EMA200 + strategy calculations
CANDLE_LIMIT = 300


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

    # Make sure numerical columns are numeric
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
        f"Candles   : {CANDLE_LIMIT}",
        flush=True
    )

    print(
        f"Symbols   : {', '.join(SYMBOLS)}",
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
                # Fetch market data
                # ------------------------------------------------

                df = get_candles(
                    symbol,
                    TIMEFRAME,
                    CANDLE_LIMIT
                )

                # ------------------------------------------------
                # Basic candle validation
                # ------------------------------------------------

                if df is None or df.empty:

                    print(
                        f"{symbol} -> NO DATA",
                        flush=True
                    )

                    continue

                if len(df) < CANDLE_LIMIT:

                    print(
                        f"{symbol} -> "
                        f"INSUFFICIENT DATA "
                        f"({len(df)}/{CANDLE_LIMIT})",
                        flush=True
                    )

                    continue

                # ------------------------------------------------
                # Add symbol
                # ------------------------------------------------

                df["symbol"] = symbol

                # ------------------------------------------------
                # Strategy
                # ------------------------------------------------

                signal = check_signal(df)

                print(
                    f"{symbol} -> {signal}",
                    flush=True
                )

                # ------------------------------------------------
                # Telegram Signal
                # ------------------------------------------------

                if signal != "WAIT":

                    current_price = df["close"].iloc[-2]

                    send_message(
                        f"🚨 SIGNAL ALERT\n\n"
                        f"Symbol: {symbol}\n"
                        f"Signal: {signal}\n"
                        f"Timeframe: {TIMEFRAME}\n"
                        f"Price: {current_price}"
                    )

            except Exception as e:

                print(
                    f"{symbol} ERROR: {e}",
                    flush=True
                )

        # --------------------------------------------------------
        # Wait for next 5-minute cycle
        # --------------------------------------------------------

        print(
            "⏳ Waiting 5 minutes...",
            flush=True
        )

        time.sleep(300)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    run()
