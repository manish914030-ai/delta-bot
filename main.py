import time
import pandas as pd

from exchange import exchange
from strategy import check_signal
from telegram_bot import send_message


# ============================================================
# DELTA TITAN AI - MAIN ENGINE
# NOTIFICATION ONLY / VIRTUAL TRADING MODE
#
# IMPORTANT:
# NO REAL BUY ORDER
# NO REAL SELL ORDER
# NO REAL POSITION
#
# Telegram notifications only.
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

# Exchange se requested candles
CANDLE_LIMIT = 300

# Strategy ke liye minimum candles
MIN_CANDLES = 210


# ============================================================
# VIRTUAL TRADE SETTINGS
# ============================================================

# Stop Loss = 1.5 ATR
SL_ATR_MULTIPLIER = 1.5

# Targets
TP1_ATR_MULTIPLIER = 1.0
TP2_ATR_MULTIPLIER = 2.0
TP3_ATR_MULTIPLIER = 3.0

# Trailing distance = 1 ATR
TRAILING_ATR_MULTIPLIER = 1.0


# ============================================================
# STATE
# ============================================================

# Last closed candle processed for signal
LAST_PROCESSED_CANDLE = {}


# One virtual position per symbol
VIRTUAL_POSITIONS = {}


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
# CREATE VIRTUAL POSITION
# ============================================================

def create_virtual_position(
    symbol,
    signal,
    entry,
    atr,
    candle_time
):

    if atr <= 0:

        print(
            f"{symbol} -> Invalid ATR: {atr}",
            flush=True
        )

        return

    # --------------------------------------------------------
    # BUY
    # --------------------------------------------------------

    if signal == "BUY":

        tp1 = entry + (
            atr * TP1_ATR_MULTIPLIER
        )

        tp2 = entry + (
            atr * TP2_ATR_MULTIPLIER
        )

        tp3 = entry + (
            atr * TP3_ATR_MULTIPLIER
        )

        stop_loss = entry - (
            atr * SL_ATR_MULTIPLIER
        )

        direction = "LONG"

    # --------------------------------------------------------
    # SELL
    # --------------------------------------------------------

    elif signal == "SELL":

        tp1 = entry - (
            atr * TP1_ATR_MULTIPLIER
        )

        tp2 = entry - (
            atr * TP2_ATR_MULTIPLIER
        )

        tp3 = entry - (
            atr * TP3_ATR_MULTIPLIER
        )

        stop_loss = entry + (
            atr * SL_ATR_MULTIPLIER
        )

        direction = "SHORT"

    else:

        return


    # --------------------------------------------------------
    # SAVE VIRTUAL POSITION
    # --------------------------------------------------------

    VIRTUAL_POSITIONS[symbol] = {

        "direction": direction,

        "signal": signal,

        "entry": float(entry),

        "atr": float(atr),

        "tp1": float(tp1),

        "tp2": float(tp2),

        "tp3": float(tp3),

        "stop_loss": float(stop_loss),

        "original_stop_loss": float(stop_loss),

        "tp1_hit": False,

        "tp2_hit": False,

        "tp3_hit": False,

        "trailing_active": False,

        "trailing_stop": None,

        "highest_price": float(entry),

        "lowest_price": float(entry),

        "entry_candle": candle_time,

        "last_trailing_candle": None
    }


    # ========================================================
    # TELEGRAM SIGNAL
    # ========================================================

    signal_message = (

        "🚨 SIGNAL ALERT\n\n"

        f"📌 Symbol: {symbol}\n"
        f"📊 Signal: {signal}\n"
        f"⏱ Timeframe: {TIMEFRAME}\n\n"

        f"💰 Price: {entry:.8f}\n"
        f"📊 ATR: {atr:.8f}\n\n"

        "🧪 Notification Only\n"
        "❌ No real order"
    )

    telegram(signal_message)


    # ========================================================
    # TELEGRAM VIRTUAL TRADE
    # ========================================================

    virtual_message = (

        f"🚨 VIRTUAL {signal} SIGNAL\n\n"

        f"📌 Symbol: {symbol}\n"
        f"⏱ Timeframe: {TIMEFRAME}\n\n"

        f"💰 Entry: {entry:.8f}\n"
        f"📊 ATR: {atr:.8f}\n\n"

        f"🎯 TP1: {tp1:.8f}\n"
        f"🎯 TP2: {tp2:.8f}\n"
        f"🎯 TP3: {tp3:.8f}\n\n"

        f"🛑 Stop Loss: {stop_loss:.8f}\n\n"

        "🔄 Trailing SL:\n"
        "Activated after TP1\n"
        f"Distance: {TRAILING_ATR_MULTIPLIER:.1f} ATR\n\n"

        "🧪 MODE: NOTIFICATION ONLY\n"
        "❌ No real order placed"
    )

    telegram(virtual_message)

    print(
        f"🧪 VIRTUAL {signal} CREATED | "
        f"{symbol} | Entry {entry} | "
        f"TP1 {tp1} | TP2 {tp2} | TP3 {tp3} | "
        f"SL {stop_loss}",
        flush=True
    )


# ============================================================
# CLOSE VIRTUAL POSITION
# ============================================================

def close_virtual_position(
    symbol,
    reason,
    exit_price
):

    position = VIRTUAL_POSITIONS.get(symbol)

    if position is None:
        return

    direction = position["direction"]

    entry = position["entry"]

    if direction == "LONG":

        pnl = exit_price - entry

    else:

        pnl = entry - exit_price

    pnl_percent = (
        (pnl / entry) * 100
        if entry != 0
        else 0
    )

    # --------------------------------------------------------
    # TARGET HIT
    # --------------------------------------------------------

    if reason == "TP1":

        message = (

            "🎯 TARGET 1 ACHIEVED\n\n"

            f"📌 Symbol: {symbol}\n"
            f"📊 Direction: {direction}\n"
            f"💰 Entry: {entry:.8f}\n"
            f"🎯 TP1 Price: {exit_price:.8f}\n\n"

            "🔄 Trailing Stop Activated\n"
            f"📏 Distance: "
            f"{TRAILING_ATR_MULTIPLIER:.1f} ATR\n\n"

            "🧪 Notification Only\n"
            "❌ No real order"
        )

        telegram(message)

        # Do NOT close position
        return


    if reason == "TP2":

        message = (

            "🎯 TARGET 2 ACHIEVED\n\n"

            f"📌 Symbol: {symbol}\n"
            f"📊 Direction: {direction}\n"
            f"💰 Entry: {entry:.8f}\n"
            f"🎯 TP2 Price: {exit_price:.8f}\n\n"

            "🔄 Trailing SL remains ACTIVE\n\n"

            "🧪 Notification Only\n"
            "❌ No real order"
        )

        telegram(message)

        return


    if reason == "TP3":

        message = (

            "🏆 TARGET 3 ACHIEVED\n\n"

            f"📌 Symbol: {symbol}\n"
            f"📊 Direction: {direction}\n"
            f"💰 Entry: {entry:.8f}\n"
            f"🎯 TP3 Price: {exit_price:.8f}\n\n"

            f"📈 Virtual P/L: {pnl:.8f}\n"
            f"📊 P/L %: {pnl_percent:.3f}%\n\n"

            "✅ VIRTUAL TRADE COMPLETED\n"
            "🧪 Notification Only\n"
            "❌ No real order"
        )

        telegram(message)

        del VIRTUAL_POSITIONS[symbol]

        return


    # --------------------------------------------------------
    # STOP LOSS
    # --------------------------------------------------------

    if reason == "STOP LOSS":

        message = (

            "🛑 STOP LOSS HIT\n\n"

            f"📌 Symbol: {symbol}\n"
            f"📊 Direction: {direction}\n"

            f"💰 Entry: {entry:.8f}\n"
            f"🛑 Exit: {exit_price:.8f}\n\n"

            f"📉 Virtual P/L: {pnl:.8f}\n"
            f"📊 P/L %: {pnl_percent:.3f}%\n\n"

            "❌ Virtual trade closed\n"
            "🧪 Notification Only\n"
            "❌ No real order"
        )

        telegram(message)

        del VIRTUAL_POSITIONS[symbol]

        return


    # --------------------------------------------------------
    # TRAILING STOP
    # --------------------------------------------------------

    if reason == "TRAILING SL":

        message = (

            "🔄 TRAILING STOP LOSS HIT\n\n"

            f"📌 Symbol: {symbol}\n"
            f"📊 Direction: {direction}\n"

            f"💰 Entry: {entry:.8f}\n"
            f"🔄 Exit: {exit_price:.8f}\n\n"

            f"📈 Virtual P/L: {pnl:.8f}\n"
            f"📊 P/L %: {pnl_percent:.3f}%\n\n"

            "❌ Virtual trade closed\n"
            "🧪 Notification Only\n"
            "❌ No real order"
        )

        telegram(message)

        del VIRTUAL_POSITIONS[symbol]

        return


# ============================================================
# MONITOR VIRTUAL POSITION
# ============================================================

def monitor_virtual_position(
    symbol,
    df
):

    position = VIRTUAL_POSITIONS.get(symbol)

    if position is None:

        return


    if df is None or df.empty:

        return


    # --------------------------------------------------------
    # Use latest candle for monitoring
    # --------------------------------------------------------

    latest = df.iloc[-1]

    candle_time = latest["time"]

    high = float(latest["high"])

    low = float(latest["low"])


    direction = position["direction"]

    entry = position["entry"]

    atr = position["atr"]


    # ========================================================
    # LONG
    # ========================================================

    if direction == "LONG":

        # ----------------------------------------------------
        # Update highest price
        # ----------------------------------------------------

        if high > position["highest_price"]:

            position["highest_price"] = high


        # ----------------------------------------------------
        # TP1
        # ----------------------------------------------------

        if (
            not position["tp1_hit"]
            and high >= position["tp1"]
        ):

            position["tp1_hit"] = True

            close_virtual_position(
                symbol,
                "TP1",
                position["tp1"]
            )

            # Activate trailing
            position["trailing_active"] = True

            position["trailing_stop"] = (
                position["highest_price"]
                - atr * TRAILING_ATR_MULTIPLIER
            )

            # Never let trailing SL go below entry
            position["trailing_stop"] = max(
                position["trailing_stop"],
                entry
            )

            telegram(

                "🔄 TRAILING SL ACTIVATED\n\n"

                f"📌 Symbol: {symbol}\n"
                f"📊 Direction: LONG\n\n"

                f"💰 Entry: {entry:.8f}\n"
                f"🔄 Trailing SL: "
                f"{position['trailing_stop']:.8f}\n\n"

                "🧪 Notification Only\n"
                "❌ No real order"
            )


        # ----------------------------------------------------
        # TP2
        # ----------------------------------------------------

        if (
            position["tp1_hit"]
            and not position["tp2_hit"]
            and high >= position["tp2"]
        ):

            position["tp2_hit"] = True

            close_virtual_position(
                symbol,
                "TP2",
                position["tp2"]
            )


        # ----------------------------------------------------
        # TP3
        # ----------------------------------------------------

        if (
            position["tp2_hit"]
            and not position["tp3_hit"]
            and high >= position["tp3"]
        ):

            position["tp3_hit"] = True

            close_virtual_position(
                symbol,
                "TP3",
                position["tp3"]
            )

            return


        # ----------------------------------------------------
        # Update trailing SL
        # ----------------------------------------------------

        if position["trailing_active"]:

            new_trailing = (
                position["highest_price"]
                - atr * TRAILING_ATR_MULTIPLIER
            )

            new_trailing = max(
                new_trailing,
                entry
            )

            old_trailing = position["trailing_stop"]

            if (
                old_trailing is None
                or new_trailing > old_trailing
            ):

                position["trailing_stop"] = new_trailing

                if (
                    position["last_trailing_candle"]
                    != candle_time
                ):

                    position[
                        "last_trailing_candle"
                    ] = candle_time

                    telegram(

                        "🔄 TRAILING SL UPDATED\n\n"

                        f"📌 Symbol: {symbol}\n"
                        f"📊 Direction: LONG\n\n"

                        f"📈 Highest: "
                        f"{position['highest_price']:.8f}\n"

                        f"🔄 New Trailing SL: "
                        f"{new_trailing:.8f}\n\n"

                        "🧪 Notification Only\n"
                        "❌ No real order"
                    )


            # ------------------------------------------------
            # Trailing SL hit
            # ------------------------------------------------

            if low <= position["trailing_stop"]:

                trailing_price = (
                    position["trailing_stop"]
                )

                close_virtual_position(
                    symbol,
                    "TRAILING SL",
                    trailing_price
                )

                return


        # ----------------------------------------------------
        # Original SL
        # ----------------------------------------------------

        if not position["trailing_active"]:

            if low <= position["stop_loss"]:

                close_virtual_position(
                    symbol,
                    "STOP LOSS",
                    position["stop_loss"]
                )

                return


    # ========================================================
    # SHORT
    # ========================================================

    elif direction == "SHORT":

        # ----------------------------------------------------
        # Update lowest price
        # ----------------------------------------------------

        if low < position["lowest_price"]:

            position["lowest_price"] = low


        # ----------------------------------------------------
        # TP1
        # ----------------------------------------------------

        if (
            not position["tp1_hit"]
            and low <= position["tp1"]
        ):

            position["tp1_hit"] = True

            close_virtual_position(
                symbol,
                "TP1",
                position["tp1"]
            )

            # Activate trailing
            position["trailing_active"] = True

            position["trailing_stop"] = (
                position["lowest_price"]
                + atr * TRAILING_ATR_MULTIPLIER
            )

            # Never let trailing SL go above entry
            position["trailing_stop"] = min(
                position["trailing_stop"],
                entry
            )

            telegram(

                "🔄 TRAILING SL ACTIVATED\n\n"

                f"📌 Symbol: {symbol}\n"
                f"📊 Direction: SHORT\n\n"

                f"💰 Entry: {entry:.8f}\n"
                f"🔄 Trailing SL: "
                f"{position['trailing_stop']:.8f}\n\n"

                "🧪 Notification Only\n"
                "❌ No real order"
            )


        # ----------------------------------------------------
        # TP2
        # ----------------------------------------------------

        if (
            position["tp1_hit"]
            and not position["tp2_hit"]
            and low <= position["tp2"]
        ):

            position["tp2_hit"] = True

            close_virtual_position(
                symbol,
                "TP2",
                position["tp2"]
            )


        # ----------------------------------------------------
        # TP3
        # ----------------------------------------------------

        if (
            position["tp2_hit"]
            and not position["tp3_hit"]
            and low <= position["tp3"]
        ):

            position["tp3_hit"] = True

            close_virtual_position(
                symbol,
                "TP3",
                position["tp3"]
            )

            return


        # ----------------------------------------------------
        # Update trailing SL
        # ----------------------------------------------------

        if position["trailing_active"]:

            new_trailing = (
                position["lowest_price"]
                + atr * TRAILING_ATR_MULTIPLIER
            )

            new_trailing = min(
                new_trailing,
                entry
            )

            old_trailing = position["trailing_stop"]

            if (
                old_trailing is None
                or new_trailing < old_trailing
            ):

                position["trailing_stop"] = new_trailing

                if (
                    position["last_trailing_candle"]
                    != candle_time
                ):

                    position[
                        "last_trailing_candle"
                    ] = candle_time

                    telegram(

                        "🔄 TRAILING SL UPDATED\n\n"

                        f"📌 Symbol: {symbol}\n"
                        f"📊 Direction: SHORT\n\n"

                        f"📉 Lowest: "
                        f"{position['lowest_price']:.8f}\n"

                        f"🔄 New Trailing SL: "
                        f"{new_trailing:.8f}\n\n"

                        "🧪 Notification Only\n"
                        "❌ No real order"
                    )


            # ------------------------------------------------
            # Trailing SL hit
            # ------------------------------------------------

            if high >= position["trailing_stop"]:

                trailing_price = (
                    position["trailing_stop"]
                )

                close_virtual_position(
                    symbol,
                    "TRAILING SL",
                    trailing_price
                )

                return


        # ----------------------------------------------------
        # Original SL
        # ----------------------------------------------------

        if not position["trailing_active"]:

            if high >= position["stop_loss"]:

                close_virtual_position(
                    symbol,
                    "STOP LOSS",
                    position["stop_loss"]
                )

                return


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
        "❌ REAL ORDERS DISABLED",
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

    telegram(

        "✅ Delta Titan AI Bot Started Successfully\n\n"

        f"📊 Timeframe: {TIMEFRAME}\n"
        f"🕯 Requested Candles: {CANDLE_LIMIT}\n"
        f"📌 Minimum Candles: {MIN_CANDLES}\n"
        f"📈 Symbols: {', '.join(SYMBOLS)}\n\n"

        "🧪 MODE: NOTIFICATION ONLY\n"
        "❌ No real orders will be placed\n\n"

        "🎯 TP1: 1 ATR\n"
        "🎯 TP2: 2 ATR\n"
        "🎯 TP3: 3 ATR\n"
        "🛑 SL: 1.5 ATR\n"
        "🔄 Trailing: 1 ATR after TP1"
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


                if df is None or df.empty:

                    print(
                        f"{symbol} -> NO DATA",
                        flush=True
                    )

                    continue


                candle_count = len(df)


                # ------------------------------------------------
                # Minimum candles
                # ------------------------------------------------

                if candle_count < MIN_CANDLES:

                    print(
                        f"{symbol} -> "
                        f"INSUFFICIENT DATA "
                        f"({candle_count}/{MIN_CANDLES})",
                        flush=True
                    )

                    continue


                # =================================================
                # MONITOR EXISTING VIRTUAL POSITION
                # =================================================

                if symbol in VIRTUAL_POSITIONS:

                    print(
                        f"{symbol} -> "
                        "Monitoring virtual position",
                        flush=True
                    )

                    monitor_virtual_position(
                        symbol,
                        df
                    )


                    # If position was closed
                    if symbol not in VIRTUAL_POSITIONS:

                        print(
                            f"{symbol} -> "
                            "Virtual position closed",
                            flush=True
                        )

                    # Do not create another trade
                    continue


                # =================================================
                # CLOSED CANDLE FOR SIGNAL
                # =================================================

                if len(df) < 2:

                    continue


                closed_candle = df.iloc[-2]

                closed_candle_time = (
                    closed_candle["time"]
                )

                closed_price = float(
                    closed_candle["close"]
                )


                # ------------------------------------------------
                # Duplicate signal protection
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


                LAST_PROCESSED_CANDLE[
                    symbol
                ] = closed_candle_time


                # =================================================
                # STRATEGY
                #
                # IMPORTANT:
                # Last row may still be forming.
                # Isliye strategy ko sirf CLOSED candles denge.
                # =================================================

                strategy_df = df.iloc[:-1].copy()

                strategy_df["symbol"] = symbol


                signal = check_signal(
                    strategy_df
                )


                print(
                    f"{symbol} -> {signal} "
                    f"| Price: {closed_price} "
                    f"| Candles: {candle_count}",
                    flush=True
                )


                # =================================================
                # BUY / SELL
                # =================================================

                if signal in [
                    "BUY",
                    "SELL"
                ]:

                    # ------------------------------------------------
                    # ATR
                    # ------------------------------------------------

                    try:

                        atr = float(
                            strategy_df.iloc[-1].get(
                                "ATR",
                                0
                            )
                        )

                    except Exception:

                        atr = 0


                    if atr <= 0:

                        print(
                            f"{symbol} -> "
                            f"Signal {signal} but invalid ATR "
                            f"{atr}",
                            flush=True
                        )

                        continue


                    # ------------------------------------------------
                    # CREATE VIRTUAL POSITION
                    # ------------------------------------------------

                    create_virtual_position(

                        symbol=symbol,

                        signal=signal,

                        entry=closed_price,

                        atr=atr,

                        candle_time=closed_candle_time
                    )


                else:

                    print(
                        f"{symbol} -> WAIT "
                        "(No valid setup)",
                        flush=True
                    )


            except Exception as e:

                print(
                    f"{symbol} ERROR: {e}",
                    flush=True
                )


        # ========================================================
        # SCAN TIMING
        # ========================================================

        elapsed = time.time() - cycle_start

        # Check approximately every 60 seconds.
        # Signal itself is still protected by closed candle.
        remaining = max(
            10,
            60 - int(elapsed)
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
            "🧪 Virtual/Notification mode active",
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
