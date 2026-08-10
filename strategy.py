import pandas as pd

from indicators import add_indicators


# ============================================================
# DELTA TITAN AI - PROFESSIONAL TREND + MOMENTUM STRATEGY
# ============================================================
#
# Indicators:
# EMA20 / EMA50 / EMA200
# RSI
# MACD
# ADX + DI
# Supertrend
# Market Structure
# BOS / CHOCH
# Liquidity Sweep
# FVG
# Momentum
#
# Output:
# BUY / SELL / WAIT
#
# IMPORTANT:
# Signal is generated only from CLOSED candle (-2)
# ============================================================


def check_signal(df):

    # ========================================================
    # BASIC DATA CHECK
    # ========================================================

    if df is None:
        return "WAIT"

    if len(df) < 210:
        return "WAIT"

    try:

        df = add_indicators(df)

    except Exception as e:

        print(
            f"STRATEGY ERROR: {e}",
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

    for column in required:

        if column not in df.columns:
            print(
                f"STRATEGY MISSING COLUMN: {column}",
                flush=True
            )
            return "WAIT"


    # ========================================================
    # LAST CLOSED CANDLE
    # ========================================================

    current = df.iloc[-2]
    previous = df.iloc[-3]


    # ========================================================
    # INVALID DATA CHECK
    # ========================================================

    for column in required:

        if pd.isna(current[column]):

            return "WAIT"


    # ========================================================
    # SAFE BOOLEAN HELPER
    # ========================================================

    def flag(column):

        if column not in df.columns:
            return False

        value = current[column]

        if pd.isna(value):
            return False

        return bool(value)


    # ========================================================
    # COMMON VALUES
    # ========================================================

    close = float(current["close"])
    previous_close = float(previous["close"])

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

    supertrend = float(current["SUPERTREND"])
    supertrend_direction = current["SUPERTREND_DIRECTION"]

    trend = str(current["TREND"]).upper()


    # ========================================================
    # ========================================================
    #                     BUY LOGIC
    # ========================================================
    # ========================================================

    buy_score = 0


    # --------------------------------------------------------
    # 1. TREND
    # --------------------------------------------------------

    bullish_trend = (
        trend == "BULLISH"
        and ema20 > ema50
        and ema50 > ema200
        and supertrend_direction == 1
    )

    if bullish_trend:
        buy_score += 2


    # --------------------------------------------------------
    # 2. DI DIRECTION
    # --------------------------------------------------------

    bullish_direction = (
        plus_di > minus_di
    )

    if bullish_direction:
        buy_score += 1


    # --------------------------------------------------------
    # 3. ADX TREND STRENGTH
    # --------------------------------------------------------

    bullish_adx = (
        adx >= 20
    )

    if bullish_adx:
        buy_score += 1


    # --------------------------------------------------------
    # 4. RSI
    #
    # Avoid buying extremely overbought market
    # --------------------------------------------------------

    bullish_rsi = (
        rsi >= 52
        and rsi <= 68
    )

    if bullish_rsi:
        buy_score += 1


    # --------------------------------------------------------
    # 5. MACD
    # --------------------------------------------------------

    bullish_macd = (
        macd > macd_signal
        and macd_hist > 0
    )

    if bullish_macd:
        buy_score += 1


    # --------------------------------------------------------
    # 6. PRICE CONFIRMATION
    # --------------------------------------------------------

    bullish_price = (
        close > ema20
        and close > supertrend
    )

    if bullish_price:
        buy_score += 1


    # --------------------------------------------------------
    # 7. EMA20 RECLAIM
    # --------------------------------------------------------

    bullish_ema_reclaim = (
        previous_close <= float(previous["EMA20"])
        and close > ema20
    )

    if bullish_ema_reclaim:
        buy_score += 2


    # --------------------------------------------------------
    # 8. MACD MOMENTUM CROSS
    # --------------------------------------------------------

    bullish_macd_cross = (
        float(previous["MACD_HIST"]) <= 0
        and macd_hist > 0
    )

    if bullish_macd_cross:
        buy_score += 2


    # --------------------------------------------------------
    # 9. MARKET STRUCTURE
    # --------------------------------------------------------

    bullish_structure = (
        flag("BOS")
        or flag("CHOCH")
    )

    if bullish_structure:
        buy_score += 2


    # --------------------------------------------------------
    # 10. LIQUIDITY SWEEP
    # --------------------------------------------------------

    bullish_liquidity = (
        flag("BULLISH_LIQUIDITY_SWEEP")
    )

    if bullish_liquidity:
        buy_score += 2


    # --------------------------------------------------------
    # 11. FAIR VALUE GAP
    # --------------------------------------------------------

    bullish_fvg = (
        flag("BULLISH_FVG")
    )

    if bullish_fvg:
        buy_score += 1


    # --------------------------------------------------------
    # 12. MOMENTUM
    # --------------------------------------------------------

    bullish_momentum = True

    try:

        momentum_value = current["MOMENTUM"]

        if pd.notna(momentum_value):

            bullish_momentum = (
                float(momentum_value) > 0
            )

    except Exception:

        bullish_momentum = True

    if bullish_momentum:
        buy_score += 1


    # ========================================================
    # BUY TRIGGER
    #
    # At least one real trigger required.
    # ========================================================

    buy_trigger = (
        bullish_ema_reclaim
        or bullish_macd_cross
        or bullish_structure
        or bullish_liquidity
        or bullish_fvg
    )


    # ========================================================
    # BUY FINAL FILTER
    # ========================================================

    if (
        buy_score >= 8
        and bullish_trend
        and bullish_adx
        and bullish_direction
        and bullish_price
        and buy_trigger
    ):

        print(
            f"🟢 BUY SETUP | Score: {buy_score}/16 "
            f"| RSI: {rsi:.2f} "
            f"| ADX: {adx:.2f}",
            flush=True
        )

        return "BUY"


    # ========================================================
    # ========================================================
    #                     SELL LOGIC
    # ========================================================
    # ========================================================

    sell_score = 0


    # --------------------------------------------------------
    # 1. TREND
    # --------------------------------------------------------

    bearish_trend = (
        trend == "BEARISH"
        and ema20 < ema50
        and ema50 < ema200
        and supertrend_direction == -1
    )

    if bearish_trend:
        sell_score += 2


    # --------------------------------------------------------
    # 2. DI DIRECTION
    # --------------------------------------------------------

    bearish_direction = (
        minus_di > plus_di
    )

    if bearish_direction:
        sell_score += 1


    # --------------------------------------------------------
    # 3. ADX
    # --------------------------------------------------------

    bearish_adx = (
        adx >= 20
    )

    if bearish_adx:
        sell_score += 1


    # --------------------------------------------------------
    # 4. RSI
    # --------------------------------------------------------

    bearish_rsi = (
        rsi >= 32
        and rsi <= 48
    )

    if bearish_rsi:
        sell_score += 1


    # --------------------------------------------------------
    # 5. MACD
    # --------------------------------------------------------

    bearish_macd = (
        macd < macd_signal
        and macd_hist < 0
    )

    if bearish_macd:
        sell_score += 1


    # --------------------------------------------------------
    # 6. PRICE
    # --------------------------------------------------------

    bearish_price = (
        close < ema20
        and close < supertrend
    )

    if bearish_price:
        sell_score += 1


    # --------------------------------------------------------
    # 7. EMA20 BREAKDOWN
    # --------------------------------------------------------

    bearish_ema_break = (
        previous_close >= float(previous["EMA20"])
        and close < ema20
    )

    if bearish_ema_break:
        sell_score += 2


    # --------------------------------------------------------
    # 8. MACD MOMENTUM CROSS
    # --------------------------------------------------------

    bearish_macd_cross = (
        float(previous["MACD_HIST"]) >= 0
        and macd_hist < 0
    )

    if bearish_macd_cross:
        sell_score += 2


    # --------------------------------------------------------
    # 9. MARKET STRUCTURE
    # --------------------------------------------------------

    bearish_structure = (
        flag("BOS")
        or flag("CHOCH")
    )

    if bearish_structure:
        sell_score += 2


    # --------------------------------------------------------
    # 10. LIQUIDITY SWEEP
    # --------------------------------------------------------

    bearish_liquidity = (
        flag("BEARISH_LIQUIDITY_SWEEP")
    )

    if bearish_liquidity:
        sell_score += 2


    # --------------------------------------------------------
    # 11. FAIR VALUE GAP
    # --------------------------------------------------------

    bearish_fvg = (
        flag("BEARISH_FVG")
    )

    if bearish_fvg:
        sell_score += 1


    # --------------------------------------------------------
    # 12. MOMENTUM
    # --------------------------------------------------------

    bearish_momentum = True

    try:

        momentum_value = current["MOMENTUM"]

        if pd.notna(momentum_value):

            bearish_momentum = (
                float(momentum_value) < 0
            )

    except Exception:

        bearish_momentum = True

    if bearish_momentum:
        sell_score += 1


    # ========================================================
    # SELL TRIGGER
    # ========================================================

    sell_trigger = (
        bearish_ema_break
        or bearish_macd_cross
        or bearish_structure
        or bearish_liquidity
        or bearish_fvg
    )


    # ========================================================
    # SELL FINAL FILTER
    # ========================================================

    if (
        sell_score >= 8
        and bearish_trend
        and bearish_adx
        and bearish_direction
        and bearish_price
        and sell_trigger
    ):

        print(
            f"🔴 SELL SETUP | Score: {sell_score}/16 "
            f"| RSI: {rsi:.2f} "
            f"| ADX: {adx:.2f}",
            flush=True
        )

        return "SELL"


    # ========================================================
    # NO TRADE
    # ========================================================

    return "WAIT"
