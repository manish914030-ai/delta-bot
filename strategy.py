import pandas as pd

from indicators import add_indicators


# ============================================================
# DELTA TITAN AI - SMART SIGNAL STRATEGY
# ============================================================
#
# Main confirmation:
# EMA 20 / 50 / 200
# Supertrend
# ADX + DI
# RSI
# MACD
#
# Extra confirmation:
# BOS / CHOCH
# Liquidity Sweep
# FVG
#
# Output:
# BUY / SELL / WAIT
# ============================================================


def _safe_bool(value):
    """
    Safely convert indicator values to boolean.
    Handles NaN / None / pandas values.
    """
    try:
        if pd.isna(value):
            return False
        return bool(value)
    except Exception:
        return False


def check_signal(df):

    # ========================================================
    # BASIC CHECK
    # ========================================================

    if df is None:
        return "WAIT"

    if len(df) < 210:
        print(
            f"STRATEGY -> WAIT | Candles: {len(df)}/210",
            flush=True
        )
        return "WAIT"

    try:
        df = add_indicators(df.copy())

    except Exception as e:

        print(
            f"STRATEGY ERROR -> {e}",
            flush=True
        )

        return "WAIT"

    # ========================================================
    # REQUIRED COLUMNS
    # ========================================================

    required = [
        "EMA20",
        "EMA50",
        "EMA200",
        "RSI",
        "MACD",
        "MACD_SIGNAL",
        "MACD_HIST",
        "ATR",
        "ADX",
        "PLUS_DI",
        "MINUS_DI",
        "SUPERTREND",
        "SUPERTREND_DIRECTION",
        "TREND",
        "MOMENTUM"
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        print(
            f"STRATEGY -> WAIT | Missing: {missing}",
            flush=True
        )

        return "WAIT"

    # ========================================================
    # LAST CLOSED CANDLE
    # ========================================================

    current = df.iloc[-2]
    previous = df.iloc[-3]

    # ========================================================
    # NaN CHECK
    # ========================================================

    for column in required:

        if pd.isna(current[column]):

            print(
                f"STRATEGY -> WAIT | Invalid {column}",
                flush=True
            )

            return "WAIT"

    # ========================================================
    # CURRENT MARKET VALUES
    # ========================================================

    close = float(current["close"])

    ema20 = float(current["EMA20"])
    ema50 = float(current["EMA50"])
    ema200 = float(current["EMA200"])

    rsi = float(current["RSI"])

    macd = float(current["MACD"])
    macd_signal = float(current["MACD_SIGNAL"])
    macd_hist = float(current["MACD_HIST"])

    adx = float(current["ADX"])

    plus_di = float(current["PLUS_DI"])
    minus_di = float(current["MINUS_DI"])

    supertrend_direction = int(
        current["SUPERTREND_DIRECTION"]
    )

    # ========================================================
    # BULLISH CONDITIONS
    # ========================================================

    bullish_ema_trend = (
        ema20 > ema50
        and ema50 > ema200
    )

    bullish_supertrend = (
        supertrend_direction == 1
    )

    bullish_di = (
        plus_di > minus_di
    )

    bullish_adx = (
        adx >= 18
    )

    bullish_rsi = (
        50 <= rsi <= 70
    )

    bullish_macd = (
        macd > macd_signal
        and macd_hist > 0
    )

    bullish_price = (
        close > ema20
    )

    # ========================================================
    # BULLISH TRIGGERS
    # ========================================================

    bullish_ema_reclaim = (
        float(previous["close"]) <= float(previous["EMA20"])
        and close > ema20
    )

    bullish_macd_cross = (
        float(previous["MACD_HIST"]) <= 0
        and macd_hist > 0
    )

    bullish_structure = (
        _safe_bool(current.get("BOS", False))
        or
        _safe_bool(current.get("CHOCH", False))
    )

    bullish_liquidity = (
        _safe_bool(
            current.get(
                "BULLISH_LIQUIDITY_SWEEP",
                False
            )
        )
    )

    bullish_fvg = (
        _safe_bool(
            current.get(
                "BULLISH_FVG",
                False
            )
        )
    )

    # ========================================================
    # BUY SCORE
    # ========================================================

    buy_score = 0

    if bullish_ema_trend:
        buy_score += 2

    if bullish_supertrend:
        buy_score += 2

    if bullish_di:
        buy_score += 1

    if bullish_adx:
        buy_score += 1

    if bullish_rsi:
        buy_score += 1

    if bullish_macd:
        buy_score += 1

    if bullish_price:
        buy_score += 1

    if bullish_ema_reclaim:
        buy_score += 2

    if bullish_macd_cross:
        buy_score += 2

    if bullish_structure:
        buy_score += 1

    if bullish_liquidity:
        buy_score += 1

    if bullish_fvg:
        buy_score += 1

    # ========================================================
    # BEARISH CONDITIONS
    # ========================================================

    bearish_ema_trend = (
        ema20 < ema50
        and ema50 < ema200
    )

    bearish_supertrend = (
        supertrend_direction == -1
    )

    bearish_di = (
        minus_di > plus_di
    )

    bearish_adx = (
        adx >= 18
    )

    bearish_rsi = (
        30 <= rsi <= 50
    )

    bearish_macd = (
        macd < macd_signal
        and macd_hist < 0
    )

    bearish_price = (
        close < ema20
    )

    # ========================================================
    # BEARISH TRIGGERS
    # ========================================================

    bearish_ema_reclaim = (
        float(previous["close"]) >= float(previous["EMA20"])
        and close < ema20
    )

    bearish_macd_cross = (
        float(previous["MACD_HIST"]) >= 0
        and macd_hist < 0
    )

    bearish_structure = (
        _safe_bool(current.get("BOS", False))
        or
        _safe_bool(current.get("CHOCH", False))
    )

    bearish_liquidity = (
        _safe_bool(
            current.get(
                "BEARISH_LIQUIDITY_SWEEP",
                False
            )
        )
    )

    bearish_fvg = (
        _safe_bool(
            current.get(
                "BEARISH_FVG",
                False
            )
        )
    )

    # ========================================================
    # SELL SCORE
    # ========================================================

    sell_score = 0

    if bearish_ema_trend:
        sell_score += 2

    if bearish_supertrend:
        sell_score += 2

    if bearish_di:
        sell_score += 1

    if bearish_adx:
        sell_score += 1

    if bearish_rsi:
        sell_score += 1

    if bearish_macd:
        sell_score += 1

    if bearish_price:
        sell_score += 1

    if bearish_ema_reclaim:
        sell_score += 2

    if bearish_macd_cross:
        sell_score += 2

    if bearish_structure:
        sell_score += 1

    if bearish_liquidity:
        sell_score += 1

    if bearish_fvg:
        sell_score += 1

    # ========================================================
    # EXTRA TRIGGER REQUIREMENT
    # ========================================================
    #
    # Sirf trend dekhkar signal nahi.
    # Kam se kam ek fresh trigger/confirmation chahiye.
    # ========================================================

    bullish_trigger = (
        bullish_ema_reclaim
        or bullish_macd_cross
        or bullish_structure
        or bullish_liquidity
        or bullish_fvg
    )

    bearish_trigger = (
        bearish_ema_reclaim
        or bearish_macd_cross
        or bearish_structure
        or bearish_liquidity
        or bearish_fvg
    )

    # ========================================================
    # FINAL BUY
    # ========================================================

    buy_valid = (
        buy_score >= 8
        and bullish_ema_trend
        and bullish_supertrend
        and bullish_di
        and bullish_adx
        and bullish_price
        and bullish_trigger
    )

    # ========================================================
    # FINAL SELL
    # ========================================================

    sell_valid = (
        sell_score >= 8
        and bearish_ema_trend
        and bearish_supertrend
        and bearish_di
        and bearish_adx
        and bearish_price
        and bearish_trigger
    )

    # ========================================================
    # SIGNAL
    # ========================================================

    if buy_valid and not sell_valid:

        print(
            f"🟢 BUY SETUP | "
            f"Score: {buy_score} | "
            f"RSI: {rsi:.2f} | "
            f"ADX: {adx:.2f} | "
            f"Price: {close}",
            flush=True
        )

        return "BUY"

    if sell_valid and not buy_valid:

        print(
            f"🔴 SELL SETUP | "
            f"Score: {sell_score} | "
            f"RSI: {rsi:.2f} | "
            f"ADX: {adx:.2f} | "
            f"Price: {close}",
            flush=True
        )

        return "SELL"

    # ========================================================
    # DIAGNOSTIC LOG
    # ========================================================

    trend_name = current.get(
        "TREND",
        "UNKNOWN"
    )

    print(
        f"⚪ WAIT | "
        f"Trend: {trend_name} | "
        f"BUY Score: {buy_score} | "
        f"SELL Score: {sell_score} | "
        f"RSI: {rsi:.2f} | "
        f"ADX: {adx:.2f}",
        flush=True
    )

    return "WAIT"
