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

# Exchange se maximum/requested candles
CANDLE_LIMIT = 300

# Strategy ke liye minimum required candles
MIN_CANDLES = 210


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

    # Remove invalid candle rows
    df.dropna(
        subset=[
            "open",
            "high",
            "low",
            "close"
        ],
        inplace=True
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
        f"Timeframe       : {TIMEFRAME}",
        flush=True
    )

    print(
        f"Requested       : {CANDLE_LIMIT}",
        flush=True
    )

    print(
        f"Minimum Needed  : {MIN_CANDLES}",
        flush=True
    )

    print(
        f"Symbols         : {', '.join(SYMBOLS)}",
        flush=True
    )

    print(
        "==================================================",
        flush=True
    )

    send_message(
        "✅ Delta Titan AI Bot Started Successfully\n\n"
        f"📊 Timeframe: {TIMEFRAME}\n"
        f"🕯 Requested Candles: {CANDLE_LIMIT}\n"
        f"📌 Minimum Candles: {MIN_CANDLES}\n"
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
                # Basic validation
                # ------------------------------------------------

                if df is None or df.empty:

                    print(
                        f"{symbol} -> NO DATA",
                        flush=True
                    )

                    continue

                candle_count = len(df)

                # ------------------------------------------------
                # IMPORTANT:
                # 300 requested hai, lekin exchange kabhi-kabhi
                # 300 se kam candles return karta hai.
                #
                # Strategy ko 210 candles chahiye.
                # Isliye 210+ hone par strategy chalegi.
                # ------------------------------------------------

                if candle_count < MIN_CANDLES:

                    print(
                        f"{symbol} -> "
                        f"INSUFFICIENT DATA "
                        f"({candle_count}/{MIN_CANDLES})",
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
                    f"{symbol} -> "
                    f"{signal} "
                    f"({candle_count} candles)",
                    flush=True
                )

                # ------------------------------------------------
                # Telegram Signal
                # ------------------------------------------------

                if signal != "WAIT":

                    current_price = df["close"].iloc[-2]

                    send_message(
                        f"🚨 SIGNAL ALERT\n\n"
                        f"📌 Symbol: {symbol}\n"
                        f"📊 Signal: {signal}\n"
                        f"⏱ Timeframe: {TIMEFRAME}\n"
                        f"💰 Price: {current_price}\n"
                        f"🕯 Candles: {candle_count}"
                    )

            except Exception as e:

                print(
                    f"{symbol} ERROR: {e}",
                    flush=True
                )

        # --------------------------------------------------------
        # Wait for next cycle
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
