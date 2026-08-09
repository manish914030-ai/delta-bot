import pandas as pd

from indicators import add_indicators


# ============================================================
# DELTA TITAN AI - PROFESSIONAL SIGNAL STRATEGY
# ============================================================
#
# Uses:
# EMA 20 / 50 / 200
# RSI
# MACD
# ADX + DI
# Supertrend
# Market Structure
# BOS / CHOCH
# Liquidity Sweep
# FVG
# Premium / Discount
# Volume
#
# Output:
# BUY / SELL / WAIT
# ============================================================


def check_signal(df):

    # --------------------------------------------------------
    # BASIC DATA CHECK
    # --------------------------------------------------------
    if df is None:
        return "WAIT"

    # EMA200 ke liye minimum data
    if len(df) < 210:
        return "WAIT"

    try:
        df = add_indicators(df)

    except Exception as e:
        print(f"STRATEGY ERROR: {e}", flush=True)
        return "WAIT"

    # --------------------------------------------------------
    # LAST CLOSED CANDLE
    # --------------------------------------------------------
    current = df.iloc[-2]
    previous = df.iloc[-3]

    # --------------------------------------------------------
    # REQUIRED INDICATORS
    # --------------------------------------------------------
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
            return "WAIT"

        if pd.isna(current[column]):
            return "WAIT"

    # ========================================================
    # BULLISH CONDITIONS
    # ========================================================

    bullish_trend = (
        current["EMA20"] > current["EMA50"]
        and current["EMA50"] > current["EMA200"]
        and current["SUPERTREND_DIRECTION"] == 1
    )

    bullish_direction = (
        current["PLUS_DI"] > current["MINUS_DI"]
    )

    bullish_adx = (
        current["ADX"] >= 20
    )

    bullish_rsi = (
        current["RSI"] >= 50
        and current["RSI"] <= 72
    )

    bullish_macd = (
        current["MACD"] > current["MACD_SIGNAL"]
        and current["MACD_HIST"] > 0
    )

    bullish_price = (
        current["close"] > current["EMA20"]
        and current["close"] > current["SUPERTREND"]
    )

    # --------------------------------------------------------
    # BULLISH TRIGGER
    # --------------------------------------------------------

    bullish_ema_cross = (
        previous["close"] <= previous["EMA20"]
        and current["close"] > current["EMA20"]
    )

    bullish_macd_cross = (
        previous["MACD_HIST"] <= 0
        and current["MACD_HIST"] > 0
    )

    bullish_structure = (
        bool(current["BOS"])
        or bool(current["CHOCH"])
    )

    bullish_liquidity = (
        bool(current["BULLISH_LIQUIDITY_SWEEP"])
    )

    bullish_fvg = (
        bool(current["BULLISH_FVG"])
    )

    # ========================================================
    # BULLISH SCORE
    # ========================================================

    buy_score = 0

    if bullish_trend:
        buy_score += 2

    if bullish_direction:
        buy_score += 1

    if bullish_adx:
        buy_score += 1

    if bullish_rsi:
        buy_score += 1

    if bullish_macd:
        buy_score += 1

    if bullish_price:
        buy_score += 1

    if bullish_ema_cross:
        buy_score += 2

    if bullish_macd_cross:
        buy_score += 2

    if bullish_structure:
        buy_score += 2

    if bullish_liquidity:
        buy_score += 2

    if bullish_fvg:
        buy_score += 1

    # --------------------------------------------------------
    # BUY FILTER
    # --------------------------------------------------------

    if (
        buy_score >= 8
        and bullish_trend
        and bullish_adx
        and bullish_direction
        and bullish_price
    ):
        return "BUY"

    # ========================================================
    # BEARISH CONDITIONS
    # ========================================================

    bearish_trend = (
        current["EMA20"] < current["EMA50"]
        and current["EMA50"] < current["EMA200"]
        and current["SUPERTREND_DIRECTION"] == -1
    )

    bearish_direction = (
        current["MINUS_DI"] > current["PLUS_DI"]
    )

    bearish_adx = (
        current["ADX"] >= 20
    )

    bearish_rsi = (
        current["RSI"] >= 28
        and current["RSI"] <= 50
    )

    bearish_macd = (
        current["MACD"] < current["MACD_SIGNAL"]
        and current["MACD_HIST"] < 0
    )

    bearish_price = (
        current["close"] < current["EMA20"]
        and current["close"] < current["SUPERTREND"]
    )

    # --------------------------------------------------------
    # BEARISH TRIGGER
    # --------------------------------------------------------

    bearish_ema_cross = (
        previous["close"] >= previous["EMA20"]
        and current["close"] < current["EMA20"]
    )

    bearish_macd_cross = (
        previous["MACD_HIST"] >= 0
        and current["MACD_HIST"] < 0
    )

    bearish_structure = (
        bool(current["BOS"])
        or bool(current["CHOCH"])
    )

    bearish_liquidity = (
        bool(current["BEARISH_LIQUIDITY_SWEEP"])
    )

    bearish_fvg = (
        bool(current["BEARISH_FVG"])
    )

    # ========================================================
    # BEARISH SCORE
    # ========================================================

    sell_score = 0

    if bearish_trend:
        sell_score += 2

    if bearish_direction:
        sell_score += 1

    if bearish_adx:
        sell_score += 1

    if bearish_rsi:
        sell_score += 1

    if bearish_macd:
        sell_score += 1

    if bearish_price:
        sell_score += 1

    if bearish_ema_cross:
        sell_score += 2

    if bearish_macd_cross:
        sell_score += 2

    if bearish_structure:
        sell_score += 2

    if bearish_liquidity:
        sell_score += 2

    if bearish_fvg:
        sell_score += 1

    # --------------------------------------------------------
    # SELL FILTER
    # --------------------------------------------------------

    if (
        sell_score >= 8
        and bearish_trend
        and bearish_adx
        and bearish_direction
        and bearish_price
    ):
        return "SELL"

    # ========================================================
    # NO VALID SIGNAL
    # ========================================================

    return "WAIT"
