import pandas as pd

from indicators import add_indicators


# ============================================================
# DELTA TITAN AI - TREND FOLLOWING STRATEGY
# ============================================================

def check_signal(df):

    if df is None or len(df) < 210:
        return "WAIT"

    # Add professional indicators
    df = add_indicators(df)

    # Last two CLOSED candles
    current = df.iloc[-2]
    previous = df.iloc[-3]

    # --------------------------------------------------------
    # BASIC DATA CHECK
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
        "SUPERTREND_DIRECTION",
        "TREND",
        "TREND_STRENGTH",
        "MOMENTUM"
    ]

    for column in required:
        if pd.isna(current[column]):
            return "WAIT"

    # ========================================================
    # BULLISH TREND FOLLOWING
    # ========================================================

    bullish_trend = (
        current["TREND"] == "BULLISH"
        and current["EMA20"] > current["EMA50"]
        and current["EMA50"] > current["EMA200"]
        and current["SUPERTREND_DIRECTION"] == 1
    )

    bullish_strength = (
        current["ADX"] >= 20
        and current["PLUS_DI"] > current["MINUS_DI"]
    )

    bullish_momentum = (
        current["RSI"] >= 52
        and current["RSI"] <= 72
        and current["MACD"] > current["MACD_SIGNAL"]
        and current["MACD_HIST"] > 0
    )

    bullish_price = (
        current["close"] > current["EMA20"]
        and current["close"] > current["SUPERTREND"]
    )

    # Entry trigger:
    # Price reclaims EMA20 OR MACD momentum turns positive
    bullish_trigger = (
        (
            previous["close"] <= previous["EMA20"]
            and current["close"] > current["EMA20"]
        )
        or
        (
            previous["MACD_HIST"] <= 0
            and current["MACD_HIST"] > 0
        )
        or
        bool(current["BOS"])
        or
        bool(current["CHOCH"])
    )

    if (
        bullish_trend
        and bullish_strength
        and bullish_momentum
        and bullish_price
        and bullish_trigger
    ):
        return "BUY"

    # ========================================================
    # BEARISH TREND FOLLOWING
    # ========================================================

    bearish_trend = (
        current["TREND"] == "BEARISH"
        and current["EMA20"] < current["EMA50"]
        and current["EMA50"] < current["EMA200"]
        and current["SUPERTREND_DIRECTION"] == -1
    )

    bearish_strength = (
        current["ADX"] >= 20
        and current["MINUS_DI"] > current["PLUS_DI"]
    )

    bearish_momentum = (
        current["RSI"] >= 28
        and current["RSI"] <= 48
        and current["MACD"] < current["MACD_SIGNAL"]
        and current["MACD_HIST"] < 0
    )

    bearish_price = (
        current["close"] < current["EMA20"]
        and current["close"] < current["SUPERTREND"]
    )

    bearish_trigger = (
        (
            previous["close"] >= previous["EMA20"]
            and current["close"] < current["EMA20"]
        )
        or
        (
            previous["MACD_HIST"] >= 0
            and current["MACD_HIST"] < 0
        )
        or
        bool(current["BOS"])
        or
        bool(current["CHOCH"])
    )

    if (
        bearish_trend
        and bearish_strength
        and bearish_momentum
        and bearish_price
        and bearish_trigger
    ):
        return "SELL"

    # ========================================================
    # NO TRADE
    # ========================================================

    return "WAIT"
