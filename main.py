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

# Exchange se requested candles
CANDLE_LIMIT = 300

# Strategy ke liye minimum candles
MIN_CANDLES = 210

# Same closed candle par duplicate signal prevent karega
LAST_PROCESSED_CANDLE = {}


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

    # Invalid rows remove
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

    # Startup Telegram message
    try:

        send_message(
            "✅ Delta Titan AI Bot Started Successfully\n\n"
            f"📊 Timeframe: {TIMEFRAME}\n"
            f"🕯 Requested Candles: {CANDLE_LIMIT}\n"
            f"📌 Minimum Candles: {MIN_CANDLES}\n"
            f"📈 Symbols: {', '.join(SYMBOLS)}"
        )

    except Exception as e:

        print(
            f"Telegram startup error: {e}",
            flush=True
        )

    # ========================================================
    # CONTINUOUS LOOP
    # ========================================================

    while True:

        cycle_start = time.time()

        print(
            "\n==================================================",
            flush=True
        )

        print(
            "🔄 NEW MARKET SCAN",
            flush=True
        )

        print(
            "==================================================",
            flush=True
        )

        for symbol in SYMBOLS:

            try:

                # ------------------------------------------------
                # Fetch candles
                # ------------------------------------------------

                df = get_candles(
                    symbol,
                    TIMEFRAME,
                    CANDLE_LIMIT
                )

                # ------------------------------------------------
                # No data
                # ------------------------------------------------

                if df is None or df.empty:

                    print(
                        f"{symbol} -> NO DATA",
                        flush=True
                    )

                    continue

                candle_count = len(df)

                # ------------------------------------------------
                # Minimum candle check
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
                # IMPORTANT:
                # Last candle may still be forming.
                #
                # Strategy uses -2 = last CLOSED candle.
                # ------------------------------------------------

                closed_candle = df.iloc[-2]

                closed_candle_time = closed_candle["time"]

                current_price = closed_candle["close"]

                # ------------------------------------------------
                # Duplicate candle protection
                # ------------------------------------------------

                if LAST_PROCESSED_CANDLE.get(symbol) == closed_candle_time:

                    print(
                        f"{symbol} -> "
                        f"Already processed candle "
                        f"{closed_candle_time}",
                        flush=True
                    )

                    continue

                # ------------------------------------------------
                # Mark this closed candle as processed
                # ------------------------------------------------

                LAST_PROCESSED_CANDLE[symbol] = closed_candle_time

                # ------------------------------------------------
                # Strategy
                # ------------------------------------------------

                signal = check_signal(df)

                print(
                    f"{symbol} -> {signal} "
                    f"| Price: {current_price} "
                    f"| Candles: {candle_count}",
                    flush=True
                )

                # ------------------------------------------------
                # Telegram signal
                # ------------------------------------------------

                if signal != "WAIT":

                    message = (
                        f"🚨 SIGNAL ALERT\n\n"
                        f"📌 Symbol: {symbol}\n"
                        f"📊 Signal: {signal}\n"
                        f"⏱ Timeframe: {TIMEFRAME}\n"
                        f"💰 Price: {current_price}\n"
                        f"🕯 Candles: {candle_count}\n"
                        f"🕐 Candle: {closed_candle_time}"
                    )

                    print(
                        f"📨 Sending Telegram signal: "
                        f"{symbol} -> {signal}",
                        flush=True
                    )

                    try:

                        send_message(message)

                        print(
                            "✅ Telegram signal sent",
                            flush=True
                        )

                    except Exception as telegram_error:

                        print(
                            f"❌ Telegram ERROR: "
                            f"{telegram_error}",
                            flush=True
                        )

                else:

                    print(
                        f"{symbol} -> WAIT "
                        f"(No valid setup)",
                        flush=True
                    )

            except Exception as e:

                print(
                    f"{symbol} ERROR: {e}",
                    flush=True
                )

        # ========================================================
        # WAIT
        # ========================================================

        elapsed = time.time() - cycle_start

        remaining = max(
            5,
            300 - int(elapsed)
        )

        print(
            "==================================================",
            flush=True
        )

        print(
            f"⏳ Scan completed. "
            f"Next scan in approximately {remaining} seconds...",
            flush=True
        )

        print(
            "==================================================",
            flush=True
        )

        time.sleep(remaining)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    run()
