import pandas as pd

from indicators import add_indicators


# ============================================================
# DELTA TITAN AI - SMART SIGNAL STRATEGY V2
# ============================================================
#
# Core confirmation:
# EMA 20 / 50 / 200
# Supertrend
# ADX + DI
# RSI
# MACD
#
# Trigger:
# EMA reclaim
# MACD cross
# BOS / CHOCH
# Liquidity Sweep
# FVG
#
# IMPORTANT:
# Strong continuation setup ko fresh trigger ke bina bhi
# allow kiya ja sakta hai, lekin uske liye strong trend +
# momentum confirmation required hai.
#
# Output:
# BUY / SELL / WAIT
# ============================================================


def _safe_bool(value):

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

    # ========================================================
    # ADD INDICATORS
    # ========================================================

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
    # VALUES
    # ========================================================

    close = float(current["close"])

    previous_close = float(previous["close"])

    ema20 = float(current["EMA20"])
    ema50 = float(current["EMA50"])
    ema200 = float(current["EMA200"])

    previous_ema20 = float(previous["EMA20"])

    rsi = float(current["RSI"])

    macd = float(current["MACD"])
    macd_signal = float(current["MACD_SIGNAL"])
    macd_hist = float(current["MACD_HIST"])

    previous_macd_hist = float(
        previous["MACD_HIST"]
    )

    adx = float(current["ADX"])

    plus_di = float(current["PLUS_DI"])
    minus_di = float(current["MINUS_DI"])

    supertrend_direction = int(
        current["SUPERTREND_DIRECTION"]
    )

    trend = str(
        current.get(
            "TREND",
            "UNKNOWN"
        )
    ).upper()

    # ========================================================
    # BULLISH CORE
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

    bullish_strong_adx = (
        adx >= 25
    )

    bullish_price = (
        close > ema20
    )

    # RSI:
    #
    # 50-70 = ideal bullish zone
    # 70-75 = strong momentum but caution
    # >75   = overextended
    #
    bullish_rsi = (
        50 <= rsi <= 70
    )

    bullish_rsi_momentum = (
        50 <= rsi <= 75
    )

    bullish_rsi_overextended = (
        rsi > 75
    )

    bullish_macd = (
        macd > macd_signal
        and macd_hist > 0
    )

    # ========================================================
    # BULLISH TRIGGERS
    # ========================================================

    bullish_ema_reclaim = (
        previous_close <= previous_ema20
        and close > ema20
    )

    bullish_macd_cross = (
        previous_macd_hist <= 0
        and macd_hist > 0
    )

    bullish_structure = (
        _safe_bool(
            current.get("BOS", False)
        )
        or
        _safe_bool(
            current.get("CHOCH", False)
        )
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

    bullish_trigger = (
        bullish_ema_reclaim
        or bullish_macd_cross
        or bullish_structure
        or bullish_liquidity
        or bullish_fvg
    )

    # ========================================================
    # BULLISH CONTINUATION
    # ========================================================
    #
    # Fresh trigger na ho, lekin market already strong trend
    # mein ho to continuation setup allow hoga.
    #
    # Isse BTC jaise setup mein Score high hone ke bawajood
    # unnecessary WAIT kam honge.
    # ========================================================

    bullish_continuation = (
        bullish_ema_trend
        and bullish_supertrend
        and bullish_di
        and bullish_strong_adx
        and bullish_price
        and bullish_macd
        and bullish_rsi_momentum
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
    # BEARISH CORE
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

    bearish_strong_adx = (
        adx >= 25
    )

    bearish_price = (
        close < ema20
    )

    # RSI:
    #
    # 30-50 = ideal bearish zone
    # 25-50 = momentum allowance
    # <25   = oversold / caution
    #

    bearish_rsi = (
        30 <= rsi <= 50
    )

    bearish_rsi_momentum = (
        25 <= rsi <= 50
    )

    bearish_rsi_oversold = (
        rsi < 25
    )

    bearish_macd = (
        macd < macd_signal
        and macd_hist < 0
    )

    # ========================================================
    # BEARISH TRIGGERS
    # ========================================================

    bearish_ema_reclaim = (
        previous_close >= previous_ema20
        and close < ema20
    )

    bearish_macd_cross = (
        previous_macd_hist >= 0
        and macd_hist < 0
    )

    bearish_structure = (
        _safe_bool(
            current.get("BOS", False)
        )
        or
        _safe_bool(
            current.get("CHOCH", False)
        )
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

    bearish_trigger = (
        bearish_ema_reclaim
        or bearish_macd_cross
        or bearish_structure
        or bearish_liquidity
        or bearish_fvg
    )

    # ========================================================
    # BEARISH CONTINUATION
    # ========================================================

    bearish_continuation = (
        bearish_ema_trend
        and bearish_supertrend
        and bearish_di
        and bearish_strong_adx
        and bearish_price
        and bearish_macd
        and bearish_rsi_momentum
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
    # FINAL BUY VALIDATION
    # ========================================================
    #
    # Primary:
    # Score >= 8 + core trend + trigger
    #
    # OR
    #
    # Strong continuation:
    # Score >= 8 + continuation confirmation
    #
    # RSI > 75 is blocked to avoid chasing extreme momentum.
    # ========================================================

    buy_trigger_valid = (
        bullish_trigger
        or bullish_continuation
    )

    buy_valid = (
        buy_score >= 8
        and bullish_ema_trend
        and bullish_supertrend
        and bullish_di
        and bullish_adx
        and bullish_price
        and buy_trigger_valid
        and not bullish_rsi_overextended
    )

    # ========================================================
    # FINAL SELL VALIDATION
    # ========================================================

    sell_trigger_valid = (
        bearish_trigger
        or bearish_continuation
    )

    sell_valid = (
        sell_score >= 8
        and bearish_ema_trend
        and bearish_supertrend
        and bearish_di
        and bearish_adx
        and bearish_price
        and sell_trigger_valid
        and not bearish_rsi_oversold
    )

    # ========================================================
    # CONFLICT PROTECTION
    # ========================================================

    if buy_valid and sell_valid:

        print(
            f"⚠️ CONFLICT -> "
            f"BUY {buy_score} / "
            f"SELL {sell_score} | WAIT",
            flush=True
        )

        return "WAIT"

    # ========================================================
    # BUY
    # ========================================================

    if buy_valid:

        print(
            f"🟢 BUY SIGNAL | "
            f"Score: {buy_score} | "
            f"RSI: {rsi:.2f} | "
            f"ADX: {adx:.2f} | "
            f"Trend: {trend} | "
            f"Trigger: {bullish_trigger} | "
            f"Continuation: {bullish_continuation} | "
            f"Price: {close}",
            flush=True
        )

        return "BUY"

    # ========================================================
    # SELL
    # ========================================================

    if sell_valid:

        print(
            f"🔴 SELL SIGNAL | "
            f"Score: {sell_score} | "
            f"RSI: {rsi:.2f} | "
            f"ADX: {adx:.2f} | "
            f"Trend: {trend} | "
            f"Trigger: {bearish_trigger} | "
            f"Continuation: {bearish_continuation} | "
            f"Price: {close}",
            flush=True
        )

        return "SELL"

    # ========================================================
    # DIAGNOSTIC
    # ========================================================

    reasons = []

    if buy_score < 8:
        reasons.append(
            f"BUY score {buy_score}<8"
        )

    if not bullish_ema_trend:
        reasons.append(
            "BUY EMA trend false"
        )

    if not bullish_supertrend:
        reasons.append(
            "BUY Supertrend false"
        )

    if not bullish_di:
        reasons.append(
            "BUY DI false"
        )

    if not bullish_adx:
        reasons.append(
            "BUY ADX false"
        )

    if not bullish_price:
        reasons.append(
            "BUY price below EMA20"
        )

    if bullish_rsi_overextended:
        reasons.append(
            f"BUY RSI overextended {rsi:.2f}"
        )

    if not bullish_trigger and not bullish_continuation:
        reasons.append(
            "BUY trigger/continuation missing"
        )

    if sell_score < 8:
        reasons.append(
            f"SELL score {sell_score}<8"
        )

    if not bearish_ema_trend:
        reasons.append(
            "SELL EMA trend false"
        )

    if not bearish_supertrend:
        reasons.append(
            "SELL Supertrend false"
        )

    if not bearish_di:
        reasons.append(
            "SELL DI false"
        )

    if not bearish_adx:
        reasons.append(
            "SELL ADX false"
        )

    if not bearish_price:
        reasons.append(
            "SELL price above EMA20"
        )

    if bearish_rsi_oversold:
        reasons.append(
            f"SELL RSI oversold {rsi:.2f}"
        )

    if not bearish_trigger and not bearish_continuation:
        reasons.append(
            "SELL trigger/continuation missing"
        )

    print(
        f"⚪ WAIT | "
        f"Trend: {trend} | "
        f"BUY Score: {buy_score} | "
        f"SELL Score: {sell_score} | "
        f"RSI: {rsi:.2f} | "
        f"ADX: {adx:.2f}",
        flush=True
    )

    print(
        "   Reasons: " +
        " | ".join(reasons[:8]),
        flush=True
    )

    return "WAIT"
