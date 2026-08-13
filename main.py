import time
import pandas as pd
import numpy as np

from exchange import exchange
from strategy import check_signal
from indicators import add_indicators
from telegram_bot import send_message


# ============================================================
# DELTA TITAN AI - MAIN ENGINE
# SIGNAL + VIRTUAL TP/SL/TRAILING TEST MODE
#
# IMPORTANT:
# NO REAL BUY
# NO REAL SELL
# NO REAL ORDER
#
# Only Telegram notifications + virtual trade monitoring
# ============================================================


# ============================================================
# SETTINGS
# ============================================================

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT"
]

TIMEFRAME = "5m"

CANDLE_LIMIT = 300
MIN_CANDLES = 210

# Same closed candle duplicate protection
LAST_PROCESSED_CANDLE = {}


# ============================================================
# VIRTUAL TRADE SETTINGS
# ============================================================

# Stop Loss distance
SL_ATR_MULTIPLIER = 1.5

# Take Profit levels
TP1_ATR_MULTIPLIER = 1.0
TP2_ATR_MULTIPLIER = 2.0
TP3_ATR_MULTIPLIER = 3.0

# Trailing SL after TP1
TRAILING_ATR_MULTIPLIER = 1.0


# ============================================================
# VIRTUAL POSITIONS
# ============================================================

# Example:
#
# VIRTUAL_POSITIONS["BTCUSDT"] = {
#     "side": "BUY",
#     "entry": 64000,
#     "atr": 300,
#     "sl": 63550,
#     "tp1": 64300,
#     "tp2": 64600,
#     "tp3": 64900,
#     "trailing_active": False,
#     "trailing_sl": None,
#     "tp1_hit": False,
#     "tp2_hit": False,
#     "tp3_hit": False,
#     "entry_candle": 123456789
# }
#
VIRTUAL_POSITIONS = {}


# ============================================================
# SAFE NUMBER
# ============================================================

def safe_float(value, default=0.0):

    try:

        value = float(value)

        if np.isnan(value) or np.isinf(value):
            return default

        return value

    except Exception:

        return default


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
# TELEGRAM SAFE SEND
# ============================================================

def telegram(message):

    try:

        send_message(message)

        print(
            "✅ Telegram notification sent",
            flush=True
        )

    except Exception as e:

        print(
            f"❌ Telegram ERROR: {e}",
            flush=True
        )


# ============================================================
# CREATE VIRTUAL TRADE
# ============================================================

def create_virtual_trade(
    symbol,
    signal,
    entry_price,
    atr_value,
    candle_time
):

    entry_price = safe_float(entry_price)
    atr_value = safe_float(atr_value)

    if entry_price <= 0:
        return

    if atr_value <= 0:
        print(
            f"{symbol} -> Invalid ATR. "
            f"Virtual trade not created.",
            flush=True
        )
        return

    if signal == "BUY":

        sl = (
            entry_price
            - atr_value * SL_ATR_MULTIPLIER
        )

        tp1 = (
            entry_price
            + atr_value * TP1_ATR_MULTIPLIER
        )

        tp2 = (
            entry_price
            + atr_value * TP2_ATR_MULTIPLIER
        )

        tp3 = (
            entry_price
            + atr_value * TP3_ATR_MULTIPLIER
        )

    else:

        sl = (
            entry_price
            + atr_value * SL_ATR_MULTIPLIER
        )

        tp1 = (
            entry_price
            - atr_value * TP1_ATR_MULTIPLIER
        )

        tp2 = (
            entry_price
            - atr_value * TP2_ATR_MULTIPLIER
        )

        tp3 = (
            entry_price
            - atr_value * TP3_ATR_MULTIPLIER
        )

    VIRTUAL_POSITIONS[symbol] = {

        "side": signal,

        "entry": entry_price,

        "atr": atr_value,

        "sl": sl,

        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,

        "trailing_active": False,

        "trailing_sl": None,

        "tp1_hit": False,
        "tp2_hit": False,
        "tp3_hit": False,

        "entry_candle": candle_time
    }

    message = (
        f"🚨 VIRTUAL {signal} SIGNAL\n\n"

        f"📌 Symbol: {symbol}\n"
        f"⏱ Timeframe: {TIMEFRAME}\n\n"

        f"💰 Entry: {entry_price:.8f}\n"
        f"📊 ATR: {atr_value:.8f}\n\n"

        f"🎯 TP1: {tp1:.8f}\n"
        f"🎯 TP2: {tp2:.8f}\n"
        f"🎯 TP3: {tp3:.8f}\n\n"

        f"🛑 Stop Loss: {sl:.8f}\n\n"

        f"🔄 Trailing SL:\n"
        f"   Activated after TP1\n"
        f"   Distance: {TRAILING_ATR_MULTIPLIER} ATR\n\n"

        f"🧪 MODE: NOTIFICATION ONLY\n"
        f"❌ No real order placed"
    )

    print(
        "\n🚨 VIRTUAL TRADE CREATED",
        flush=True
    )

    print(
        f"{symbol} | {signal}",
        flush=True
    )

    print(
        f"Entry : {entry_price}",
        flush=True
    )

    print(
        f"SL    : {sl}",
        flush=True
    )

    print(
        f"TP1   : {tp1}",
        flush=True
    )

    print(
        f"TP2   : {tp2}",
        flush=True
    )

    print(
        f"TP3   : {tp3}",
        flush=True
    )

    telegram(message)


# ============================================================
# CALCULATE VIRTUAL PNL
# ============================================================

def calculate_pnl(side, entry, price):

    entry = safe_float(entry)
    price = safe_float(price)

    if entry <= 0:
        return 0.0

    if side == "BUY":

        return (
            (price - entry)
            / entry
        ) * 100

    else:

        return (
            (entry - price)
            / entry
        ) * 100


# ============================================================
# CLOSE VIRTUAL TRADE
# ============================================================

def close_virtual_trade(
    symbol,
    exit_price,
    reason
):

    if symbol not in VIRTUAL_POSITIONS:
        return

    trade = VIRTUAL_POSITIONS[symbol]

    side = trade["side"]
    entry = trade["entry"]

    pnl = calculate_pnl(
        side,
        entry,
        exit_price
    )

    if pnl >= 0:
        result = "🟢 PROFIT"
    else:
        result = "🔴 LOSS"

    message = (
        f"🏁 VIRTUAL TRADE CLOSED\n\n"

        f"📌 Symbol: {symbol}\n"
        f"📊 Side: {side}\n\n"

        f"💰 Entry: {entry:.8f}\n"
        f"💰 Exit: {exit_price:.8f}\n\n"

        f"📌 Reason: {reason}\n\n"

        f"{result}\n"
        f"📈 Virtual P&L: {pnl:.2f}%\n\n"

        f"🧪 NOTIFICATION ONLY\n"
        f"❌ No real order was placed"
    )

    print(
        f"🏁 {symbol} VIRTUAL TRADE CLOSED | "
        f"{reason} | PNL {pnl:.2f}%",
        flush=True
    )

    telegram(message)

    del VIRTUAL_POSITIONS[symbol]


# ============================================================
# UPDATE TRAILING STOP
# ============================================================

def update_trailing_stop(
    symbol,
    trade,
    candle
):

    if not trade["trailing_active"]:
        return

    side = trade["side"]

    atr_value = safe_float(
        trade["atr"]
    )

    high = safe_float(
        candle["high"]
    )

    low = safe_float(
        candle["low"]
    )

    old_trailing = trade["trailing_sl"]

    if side == "BUY":

        new_trailing = (
            high
            - atr_value * TRAILING_ATR_MULTIPLIER
        )

        # Trailing SL only moves UP
        if (
            old_trailing is None
            or new_trailing > old_trailing
        ):

            trade["trailing_sl"] = new_trailing

            print(
                f"🔄 {symbol} BUY trailing updated: "
                f"{new_trailing}",
                flush=True
            )

            telegram(
                f"🔄 TRAILING SL UPDATED\n\n"
                f"📌 Symbol: {symbol}\n"
                f"📊 Side: BUY\n\n"
                f"📉 Previous SL: "
                f"{old_trailing if old_trailing else trade['sl']:.8f}\n"
                f"📈 New Trailing SL: "
                f"{new_trailing:.8f}\n\n"
                f"🧪 Notification Only"
            )

    else:

        new_trailing = (
            low
            + atr_value * TRAILING_ATR_MULTIPLIER
        )

        # Trailing SL only moves DOWN
        if (
            old_trailing is None
            or new_trailing < old_trailing
        ):

            trade["trailing_sl"] = new_trailing

            print(
                f"🔄 {symbol} SELL trailing updated: "
                f"{new_trailing}",
                flush=True
            )

            telegram(
                f"🔄 TRAILING SL UPDATED\n\n"
                f"📌 Symbol: {symbol}\n"
                f"📊 Side: SELL\n\n"
                f"📉 Previous SL: "
                f"{old_trailing if old_trailing else trade['sl']:.8f}\n"
                f"📈 New Trailing SL: "
                f"{new_trailing:.8f}\n\n"
                f"🧪 Notification Only"
            )


# ============================================================
# MONITOR VIRTUAL TRADE
# ============================================================

def monitor_virtual_trade(
    symbol,
    df
):

    if symbol not in VIRTUAL_POSITIONS:
        return

    trade = VIRTUAL_POSITIONS[symbol]

    # Last CLOSED candle
    candle = df.iloc[-2]

    high = safe_float(
        candle["high"]
    )

    low = safe_float(
        candle["low"]
    )

    close = safe_float(
        candle["close"]
    )

    side = trade["side"]

    entry = trade["entry"]

    sl = trade["sl"]

    tp1 = trade["tp1"]
    tp2 = trade["tp2"]
    tp3 = trade["tp3"]

    # ========================================================
    # BUY
    # ========================================================

    if side == "BUY":

        # ----------------------------------------------------
        # SL CHECK FIRST
        #
        # Conservative assumption if same candle
        # touches both SL and TP.
        # ----------------------------------------------------

        active_sl = sl

        if trade["trailing_active"]:

            active_sl = trade["trailing_sl"]

        if active_sl is not None:

            if low <= active_sl:

                close_virtual_trade(
                    symbol,
                    active_sl,
                    "TRAILING STOP HIT"
                    if trade["trailing_active"]
                    else "STOP LOSS HIT"
                )

                return

        # ----------------------------------------------------
        # TP1
        # ----------------------------------------------------

        if (
            not trade["tp1_hit"]
            and high >= tp1
        ):

            trade["tp1_hit"] = True

            trade["trailing_active"] = True

            initial_trailing = (
                close
                - trade["atr"]
                * TRAILING_ATR_MULTIPLIER
            )

            # Never put trailing below original SL
            trade["trailing_sl"] = max(
                initial_trailing,
                sl
            )

            telegram(
                f"🎯 TP1 HIT\n\n"
                f"📌 Symbol: {symbol}\n"
                f"📊 Side: BUY\n"
                f"💰 Entry: {entry:.8f}\n"
                f"🎯 TP1: {tp1:.8f}\n"
                f"📍 Candle High: {high:.8f}\n\n"
                f"🔄 TRAILING SL ACTIVATED\n"
                f"🛑 Trailing SL: "
                f"{trade['trailing_sl']:.8f}\n\n"
                f"🧪 Notification Only"
            )

            print(
                f"🎯 {symbol} TP1 HIT | "
                f"Trailing activated",
                flush=True
            )

        # ----------------------------------------------------
        # TP2
        # ----------------------------------------------------

        if (
            not trade["tp2_hit"]
            and high >= tp2
        ):

            trade["tp2_hit"] = True

            telegram(
                f"🎯 TP2 HIT\n\n"
                f"📌 Symbol: {symbol}\n"
                f"📊 Side: BUY\n"
                f"💰 Entry: {entry:.8f}\n"
                f"🎯 TP2: {tp2:.8f}\n"
                f"📍 Price: {high:.8f}\n\n"
                f"🔄 Trailing SL remains ACTIVE\n\n"
                f"🧪 Notification Only"
            )

        # ----------------------------------------------------
        # TP3
        # ----------------------------------------------------

        if (
            not trade["tp3_hit"]
            and high >= tp3
        ):

            trade["tp3_hit"] = True

            telegram(
                f"🎯 TP3 HIT\n\n"
                f"📌 Symbol: {symbol}\n"
                f"📊 Side: BUY\n"
                f"💰 Entry: {entry:.8f}\n"
                f"🎯 TP3: {tp3:.8f}\n"
                f"📍 Price: {high:.8f}\n\n"
                f"🏁 Virtual trade completed\n\n"
                f"🧪 Notification Only"
            )

            close_virtual_trade(
                symbol,
                tp3,
                "TP3 HIT"
            )

            return

    # ========================================================
    # SELL
    # ========================================================

    else:

        # ----------------------------------------------------
        # SL CHECK FIRST
        # ----------------------------------------------------

        active_sl = sl

        if trade["trailing_active"]:

            active_sl = trade["trailing_sl"]

        if active_sl is not None:

            if high >= active_sl:

                close_virtual_trade(
                    symbol,
                    active_sl,
                    "TRAILING STOP HIT"
                    if trade["trailing_active"]
                    else "STOP LOSS HIT"
                )

                return

        # ----------------------------------------------------
        # TP1
        # ----------------------------------------------------

        if (
            not trade["tp1_hit"]
            and low <= tp1
        ):

            trade["tp1_hit"] = True

            trade["trailing_active"] = True

            initial_trailing = (
                close
                + trade["atr"]
                * TRAILING_ATR_MULTIPLIER
            )

            # Never put trailing above original SL
            trade["trailing_sl"] = min(
                initial_trailing,
                sl
            )

            telegram(
                f"🎯 TP1 HIT\n\n"
                f"📌 Symbol: {symbol}\n"
                f"📊 Side: SELL\n"
                f"💰 Entry: {entry:.8f}\n"
                f"🎯 TP1: {tp1:.8f}\n"
                f"📍 Candle Low: {low:.8f}\n\n"
                f"🔄 TRAILING SL ACTIVATED\n"
                f"🛑 Trailing SL: "
                f"{trade['trailing_sl']:.8f}\n\n"
                f"🧪 Notification Only"
            )

            print(
                f"🎯 {symbol} TP1 HIT | "
                f"Trailing activated",
                flush=True
            )

        # ----------------------------------------------------
        # TP2
        # ----------------------------------------------------

        if (
            not trade["tp2_hit"]
            and low <= tp2
        ):

            trade["tp2_hit"] = True

            telegram(
                f"🎯 TP2 HIT\n\n"
                f"📌 Symbol: {symbol}\n"
                f"📊 Side: SELL\n"
                f"💰 Entry: {entry:.8f}\n"
                f"🎯 TP2: {tp2:.8f}\n"
                f"📍 Price: {low:.8f}\n\n"
                f"🔄 Trailing SL remains ACTIVE\n\n"
                f"🧪 Notification Only"
            )

        # ----------------------------------------------------
        # TP3
        # ----------------------------------------------------

        if (
            not trade["tp3_hit"]
            and low <= tp3
        ):

            trade["tp3_hit"] = True

            telegram(
                f"🎯 TP3 HIT\n\n"
                f"📌 Symbol: {symbol}\n"
                f"📊 Side: SELL\n"
                f"💰 Entry: {entry:.8f}\n"
                f"🎯 TP3: {tp3:.8f}\n"
                f"📍 Price: {low:.8f}\n\n"
                f"🏁 Virtual trade completed\n\n"
                f"🧪 Notification Only"
            )

            close_virtual_trade(
                symbol,
                tp3,
                "TP3 HIT"
            )

            return

    # ========================================================
    # TRAILING UPDATE
    # ========================================================

    if symbol in VIRTUAL_POSITIONS:

        update_trailing_stop(
            symbol,
            VIRTUAL_POSITIONS[symbol],
            candle
        )


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
        "🧪 MODE: NOTIFICATION ONLY",
        flush=True
    )

    print(
        "❌ REAL ORDERS: DISABLED",
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

    # ========================================================
    # STARTUP TELEGRAM
    # ========================================================

    try:

        send_message(
            "✅ Delta Titan AI Bot Started Successfully\n\n"

            f"📊 Timeframe: {TIMEFRAME}\n"
            f"🕯 Requested Candles: {CANDLE_LIMIT}\n"
            f"📌 Minimum Candles: {MIN_CANDLES}\n"
            f"📈 Symbols: {', '.join(SYMBOLS)}\n\n"

            "🧪 MODE: NOTIFICATION ONLY\n"
            "❌ Real BUY/SELL disabled\n\n"

            "🎯 TP1 = 1.0 ATR\n"
            "🎯 TP2 = 2.0 ATR\n"
            "🎯 TP3 = 3.0 ATR\n"
            "🛑 SL = 1.5 ATR\n"
            "🔄 Trailing = 1.0 ATR after TP1"
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
                # FETCH CANDLES
                # ------------------------------------------------

                df = get_candles(
                    symbol,
                    TIMEFRAME,
                    CANDLE_LIMIT
                )

                if df is None or df.empty:

                    print(
                        f"{symbol} -> NO DATA",
                        flush=True
                    )

                    continue

                candle_count = len(df)

                # ------------------------------------------------
                # MINIMUM CANDLES
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
                # LAST CLOSED CANDLE
                # ------------------------------------------------

                closed_candle = df.iloc[-2]

                closed_candle_time = (
                    closed_candle["time"]
                )

                current_price = safe_float(
                    closed_candle["close"]
                )

                # ------------------------------------------------
                # MONITOR EXISTING VIRTUAL TRADE
                #
                # IMPORTANT:
                # Existing trade ko har new closed candle
                # par monitor karna hai.
                # ------------------------------------------------

                if symbol in VIRTUAL_POSITIONS:

                    print(
                        f"📊 {symbol} -> "
                        f"Monitoring virtual "
                        f"{VIRTUAL_POSITIONS[symbol]['side']} trade",
                        flush=True
                    )

                    monitor_virtual_trade(
                        symbol,
                        df
                    )

                # ------------------------------------------------
                # DUPLICATE SIGNAL PROTECTION
                # ------------------------------------------------

                if (
                    LAST_PROCESSED_CANDLE.get(symbol)
                    == closed_candle_time
                ):

                    print(
                        f"{symbol} -> "
                        f"Already processed candle "
                        f"{closed_candle_time}",
                        flush=True
                    )

                    continue

                LAST_PROCESSED_CANDLE[symbol] = (
                    closed_candle_time
                )

                # ------------------------------------------------
                # IMPORTANT:
                # ONLY CLOSED CANDLES FOR STRATEGY
                #
                # Remove current forming candle.
                # ------------------------------------------------

                strategy_df = df.iloc[:-1].copy()

                # ------------------------------------------------
                # STRATEGY
                # ------------------------------------------------

                signal = check_signal(
                    strategy_df
                )

                print(
                    f"{symbol} -> {signal} "
                    f"| Price: {current_price} "
                    f"| Candles: {candle_count}",
                    flush=True
                )

                # ------------------------------------------------
                # SIGNAL
                # ------------------------------------------------

                if signal != "WAIT":

                    # ------------------------------------------------
                    # If virtual trade already exists,
                    # don't create another one.
                    # ------------------------------------------------

                    if symbol in VIRTUAL_POSITIONS:

                        existing_side = (
                            VIRTUAL_POSITIONS[symbol]["side"]
                        )

                        print(
                            f"{symbol} -> "
                            f"New {signal} signal ignored. "
                            f"Existing virtual "
                            f"{existing_side} trade active.",
                            flush=True
                        )

                        continue

                    # ------------------------------------------------
                    # ADD INDICATORS FOR ATR
                    # ------------------------------------------------

                    indicator_df = add_indicators(
                        strategy_df
                    )

                    if (
                        indicator_df is None
                        or indicator_df.empty
                    ):

                        print(
                            f"{symbol} -> "
                            f"Could not calculate indicators",
                            flush=True
                        )

                        continue

                    signal_row = (
                        indicator_df.iloc[-1]
                    )

                    atr_value = safe_float(
                        signal_row.get("ATR")
                    )

                    # ------------------------------------------------
                    # BASIC SIGNAL TELEGRAM
                    # ------------------------------------------------

                    message = (
                        f"🚨 SIGNAL ALERT\n\n"

                        f"📌 Symbol: {symbol}\n"
                        f"📊 Signal: {signal}\n"
                        f"⏱ Timeframe: {TIMEFRAME}\n"
                        f"💰 Price: {current_price:.8f}\n"
                        f"🕯 Candles: {candle_count}\n"
                        f"🕐 Candle: {closed_candle_time}\n\n"

                        f"📊 ATR: {atr_value:.8f}\n\n"

                        f"🧪 Notification Only\n"
                        f"❌ No real order"
                    )

                    print(
                        f"📨 Sending Telegram signal: "
                        f"{symbol} -> {signal}",
                        flush=True
                    )

                    telegram(message)

                    # ------------------------------------------------
                    # CREATE VIRTUAL TRADE
                    # ------------------------------------------------

                    create_virtual_trade(
                        symbol=symbol,
                        signal=signal,
                        entry_price=current_price,
                        atr_value=atr_value,
                        candle_time=closed_candle_time
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
        # STATUS
        # ========================================================

        print(
            "\n📊 ACTIVE VIRTUAL TRADES",
            flush=True
        )

        if not VIRTUAL_POSITIONS:

            print(
                "None",
                flush=True
            )

        else:

            for symbol, trade in (
                VIRTUAL_POSITIONS.items()
            ):

                print(
                    f"{symbol} | "
                    f"{trade['side']} | "
                    f"Entry: {trade['entry']} | "
                    f"SL: {trade['sl']} | "
                    f"TP1: {trade['tp1']} | "
                    f"TP2: {trade['tp2']} | "
                    f"TP3: {trade['tp3']} | "
                    f"Trailing: "
                    f"{trade['trailing_sl']}",
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
            f"Next scan in approximately "
            f"{remaining} seconds...",
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
