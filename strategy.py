import pandas as pd
import numpy as np

from indicators import add_indicators


# ============================================================
# DELTA TITAN AI - SIGNAL STRATEGY
# TEST MODE / SIGNAL GENERATION
#
# GOAL:
#   Strategy ko thoda loose rakhna
#   BUY / SELL signals generate karna
#
# IMPORTANT:
#   Abhi profit optimization nahi.
#   Pehle signal generation verify karna hai.
# ============================================================


# ============================================================
# SETTINGS
# ============================================================

MIN_SCORE = 5

# RSI
RSI_BUY_MIN = 45
RSI_BUY_MAX = 72

RSI_SELL_MIN = 28
RSI_SELL_MAX = 55

# ADX
MIN_ADX = 18

# Volume
MIN_VOLUME_RATIO = 0.80

# Recent structure window
STRUCTURE_LOOKBACK = 5


# ============================================================
# SAFE VALUE
# ============================================================

def safe_value(value, default=0):

    try:

        if pd.isna(value):
            return default

        return float(value)

    except Exception:

        return default


# ============================================================
# GET LAST ROW
# ============================================================

def get_last_row(df):

    if df is None:
        return None

    if len(df) == 0:
        return None

    return df.iloc[-1]


# ============================================================
# RECENT TRUE CHECK
# ============================================================

def recent_true(df, column, lookback=5):

    if column not in df.columns:
        return False

    data = df[column].tail(lookback)

    return bool(data.fillna(False).astype(bool).any())


# ============================================================
# BUY SIGNAL
# ============================================================

def calculate_buy_score(df):

    row = get_last_row(df)

    if row is None:
        return 0, []

    score = 0
    reasons = []

    close = safe_value(row.get("close"))
    ema20 = safe_value(row.get("EMA20"))
    ema50 = safe_value(row.get("EMA50"))
    ema200 = safe_value(row.get("EMA200"))

    rsi = safe_value(row.get("RSI"), 50)

    macd = safe_value(row.get("MACD"))
    macd_signal = safe_value(
        row.get("MACD_SIGNAL")
    )

    adx = safe_value(
        row.get("ADX")
    )

    plus_di = safe_value(
        row.get("PLUS_DI")
    )

    minus_di = safe_value(
        row.get("MINUS_DI")
    )

    supertrend_direction = safe_value(
        row.get("SUPERTREND_DIRECTION")
    )

    volume_ratio = safe_value(
        row.get("VOLUME_RATIO"),
        1.0
    )

    trend = str(
        row.get(
            "TREND",
            "SIDEWAYS"
        )
    ).upper()

    momentum = str(
        row.get(
            "MOMENTUM",
            "NEUTRAL"
        )
    ).upper()

    market_zone = str(
        row.get(
            "MARKET_ZONE",
            "EQUILIBRIUM"
        )
    ).upper()

    # --------------------------------------------------------
    # 1. EMA STRUCTURE
    # --------------------------------------------------------

    if (
        ema20 > ema50
        and ema50 > ema200
    ):

        score += 2

        reasons.append(
            "BUY EMA trend"
        )

    elif ema20 > ema50:

        score += 1

        reasons.append(
            "BUY EMA20 > EMA50"
        )

    # --------------------------------------------------------
    # 2. PRICE ABOVE EMA20
    # --------------------------------------------------------

    if close > ema20:

        score += 1

        reasons.append(
            "BUY price above EMA20"
        )

    # --------------------------------------------------------
    # 3. SUPERTREND
    # --------------------------------------------------------

    if supertrend_direction == 1:

        score += 2

        reasons.append(
            "BUY Supertrend"
        )

    # --------------------------------------------------------
    # 4. RSI
    # --------------------------------------------------------

    if (
        RSI_BUY_MIN
        <= rsi
        <= RSI_BUY_MAX
    ):

        score += 1

        reasons.append(
            f"BUY RSI {rsi:.1f}"
        )

    # Strong momentum RSI
    if 52 <= rsi <= 68:

        score += 1

        reasons.append(
            "BUY RSI momentum"
        )

    # --------------------------------------------------------
    # 5. MACD
    # --------------------------------------------------------

    if macd > macd_signal:

        score += 1

        reasons.append(
            "BUY MACD"
        )

    # MACD histogram positive
    macd_hist = safe_value(
        row.get("MACD_HIST")
    )

    if macd_hist > 0:

        score += 1

        reasons.append(
            "BUY MACD histogram"
        )

    # --------------------------------------------------------
    # 6. ADX
    # --------------------------------------------------------

    if adx >= MIN_ADX:

        score += 1

        reasons.append(
            f"BUY ADX {adx:.1f}"
        )

    # --------------------------------------------------------
    # 7. DI
    # --------------------------------------------------------

    if plus_di > minus_di:

        score += 1

        reasons.append(
            "BUY +DI > -DI"
        )

    # --------------------------------------------------------
    # 8. MOMENTUM
    # --------------------------------------------------------

    if momentum == "BULLISH":

        score += 1

        reasons.append(
            "BUY momentum"
        )

    # --------------------------------------------------------
    # 9. TREND
    # --------------------------------------------------------

    if trend == "BULLISH":

        score += 1

        reasons.append(
            "BUY trend"
        )

    # --------------------------------------------------------
    # 10. VOLUME
    # --------------------------------------------------------

    if volume_ratio >= MIN_VOLUME_RATIO:

        score += 1

        reasons.append(
            f"BUY volume {volume_ratio:.2f}x"
        )

    # --------------------------------------------------------
    # 11. MARKET ZONE
    # --------------------------------------------------------

    if market_zone == "DISCOUNT":

        score += 1

        reasons.append(
            "BUY discount zone"
        )

    # --------------------------------------------------------
    # 12. BOS / CHOCH
    # --------------------------------------------------------

    if recent_true(
        df,
        "BOS",
        STRUCTURE_LOOKBACK
    ):

        # BOS is supportive but not mandatory
        if recent_bullish_structure(df):

            score += 1

            reasons.append(
                "BUY recent BOS"
            )

    if recent_bullish_choch(df):

        score += 1

        reasons.append(
            "BUY recent CHOCH"
        )

    # --------------------------------------------------------
    # 13. LIQUIDITY SWEEP
    # --------------------------------------------------------

    if recent_true(
        df,
        "BULLISH_LIQUIDITY_SWEEP",
        STRUCTURE_LOOKBACK
    ):

        score += 1

        reasons.append(
            "BUY liquidity sweep"
        )

    # --------------------------------------------------------
    # 14. FVG
    # --------------------------------------------------------

    if recent_true(
        df,
        "BULLISH_FVG",
        STRUCTURE_LOOKBACK
    ):

        score += 1

        reasons.append(
            "BUY bullish FVG"
        )

    return score, reasons


# ============================================================
# SELL SIGNAL
# ============================================================

def calculate_sell_score(df):

    row = get_last_row(df)

    if row is None:
        return 0, []

    score = 0
    reasons = []

    close = safe_value(row.get("close"))
    ema20 = safe_value(row.get("EMA20"))
    ema50 = safe_value(row.get("EMA50"))
    ema200 = safe_value(row.get("EMA200"))

    rsi = safe_value(
        row.get("RSI"),
        50
    )

    macd = safe_value(
        row.get("MACD")
    )

    macd_signal = safe_value(
        row.get("MACD_SIGNAL")
    )

    macd_hist = safe_value(
        row.get("MACD_HIST")
    )

    adx = safe_value(
        row.get("ADX")
    )

    plus_di = safe_value(
        row.get("PLUS_DI")
    )

    minus_di = safe_value(
        row.get("MINUS_DI")
    )

    supertrend_direction = safe_value(
        row.get(
            "SUPERTREND_DIRECTION"
        )
    )

    volume_ratio = safe_value(
        row.get(
            "VOLUME_RATIO"
        ),
        1.0
    )

    trend = str(
        row.get(
            "TREND",
            "SIDEWAYS"
        )
    ).upper()

    momentum = str(
        row.get(
            "MOMENTUM",
            "NEUTRAL"
        )
    ).upper()

    market_zone = str(
        row.get(
            "MARKET_ZONE",
            "EQUILIBRIUM"
        )
    ).upper()

    # --------------------------------------------------------
    # 1. EMA STRUCTURE
    # --------------------------------------------------------

    if (
        ema20 < ema50
        and ema50 < ema200
    ):

        score += 2

        reasons.append(
            "SELL EMA trend"
        )

    elif ema20 < ema50:

        score += 1

        reasons.append(
            "SELL EMA20 < EMA50"
        )

    # --------------------------------------------------------
    # 2. PRICE BELOW EMA20
    # --------------------------------------------------------

    if close < ema20:

        score += 1

        reasons.append(
            "SELL price below EMA20"
        )

    # --------------------------------------------------------
    # 3. SUPERTREND
    # --------------------------------------------------------

    if supertrend_direction == -1:

        score += 2

        reasons.append(
            "SELL Supertrend"
        )

    # --------------------------------------------------------
    # 4. RSI
    # --------------------------------------------------------

    if (
        RSI_SELL_MIN
        <= rsi
        <= RSI_SELL_MAX
    ):

        score += 1

        reasons.append(
            f"SELL RSI {rsi:.1f}"
        )

    # Strong bearish RSI
    if 32 <= rsi <= 48:

        score += 1

        reasons.append(
            "SELL RSI momentum"
        )

    # --------------------------------------------------------
    # 5. MACD
    # --------------------------------------------------------

    if macd < macd_signal:

        score += 1

        reasons.append(
            "SELL MACD"
        )

    # --------------------------------------------------------
    # 6. MACD HISTOGRAM
    # --------------------------------------------------------

    if macd_hist < 0:

        score += 1

        reasons.append(
            "SELL MACD histogram"
        )

    # --------------------------------------------------------
    # 7. ADX
    # --------------------------------------------------------

    if adx >= MIN_ADX:

        score += 1

        reasons.append(
            f"SELL ADX {adx:.1f}"
        )

    # --------------------------------------------------------
    # 8. DI
    # --------------------------------------------------------

    if minus_di > plus_di:

        score += 1

        reasons.append(
            "SELL -DI > +DI"
        )

    # --------------------------------------------------------
    # 9. MOMENTUM
    # --------------------------------------------------------

    if momentum == "BEARISH":

        score += 1

        reasons.append(
            "SELL momentum"
        )

    # --------------------------------------------------------
    # 10. TREND
    # --------------------------------------------------------

    if trend == "BEARISH":

        score += 1

        reasons.append(
            "SELL trend"
        )

    # --------------------------------------------------------
    # 11. VOLUME
    # --------------------------------------------------------

    if volume_ratio >= MIN_VOLUME_RATIO:

        score += 1

        reasons.append(
            f"SELL volume {volume_ratio:.2f}x"
        )

    # --------------------------------------------------------
    # 12. PREMIUM ZONE
    # --------------------------------------------------------

    if market_zone == "PREMIUM":

        score += 1

        reasons.append(
            "SELL premium zone"
        )

    # --------------------------------------------------------
    # 13. BEARISH BOS
    # --------------------------------------------------------

    if recent_true(
        df,
        "BOS",
        STRUCTURE_LOOKBACK
    ):

        if recent_bearish_structure(df):

            score += 1

            reasons.append(
                "SELL recent BOS"
            )

    # --------------------------------------------------------
    # 14. BEARISH CHOCH
    # --------------------------------------------------------

    if recent_bearish_choch(df):

        score += 1

        reasons.append(
            "SELL recent CHOCH"
        )

    # --------------------------------------------------------
    # 15. LIQUIDITY SWEEP
    # --------------------------------------------------------

    if recent_true(
        df,
        "BEARISH_LIQUIDITY_SWEEP",
        STRUCTURE_LOOKBACK
    ):

        score += 1

        reasons.append(
            "SELL liquidity sweep"
        )

    # --------------------------------------------------------
    # 16. FVG
    # --------------------------------------------------------

    if recent_true(
        df,
        "BEARISH_FVG",
        STRUCTURE_LOOKBACK
    ):

        score += 1

        reasons.append(
            "SELL bearish FVG"
        )

    return score, reasons


# ============================================================
# STRUCTURE HELPERS
# ============================================================

def recent_bullish_structure(df):

    if "STRUCTURE_BREAK" not in df.columns:
        return False

    values = (
        df["STRUCTURE_BREAK"]
        .tail(STRUCTURE_LOOKBACK)
        .astype(str)
        .str.upper()
    )

    return bool(
        values.isin(
            [
                "BULLISH_BOS",
                "BULLISH_CHOCH"
            ]
        ).any()
    )


def recent_bearish_structure(df):

    if "STRUCTURE_BREAK" not in df.columns:
        return False

    values = (
        df["STRUCTURE_BREAK"]
        .tail(STRUCTURE_LOOKBACK)
        .astype(str)
        .str.upper()
    )

    return bool(
        values.isin(
            [
                "BEARISH_BOS",
                "BEARISH_CHOCH"
            ]
        ).any()
    )


def recent_bullish_choch(df):

    if "STRUCTURE_BREAK" not in df.columns:
        return False

    values = (
        df["STRUCTURE_BREAK"]
        .tail(STRUCTURE_LOOKBACK)
        .astype(str)
        .str.upper()
    )

    return bool(
        values.eq(
            "BULLISH_CHOCH"
        ).any()
    )


def recent_bearish_choch(df):

    if "STRUCTURE_BREAK" not in df.columns:
        return False

    values = (
        df["STRUCTURE_BREAK"]
        .tail(STRUCTURE_LOOKBACK)
        .astype(str)
        .str.upper()
    )

    return bool(
        values.eq(
            "BEARISH_CHOCH"
        ).any()
    )


# ============================================================
# MAIN SIGNAL FUNCTION
# ============================================================

def check_signal(df):

    try:

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if df is None:
            return "WAIT"

        if len(df) < 210:

            print(
                f"WAIT | Not enough candles: {len(df)}"
            )

            return "WAIT"

        # ----------------------------------------------------
        # ADD INDICATORS
        # ----------------------------------------------------

        df = add_indicators(df)

        if df is None or len(df) == 0:

            return "WAIT"

        row = df.iloc[-1]

        # ----------------------------------------------------
        # CURRENT PRICE
        # ----------------------------------------------------

        price = safe_value(
            row.get("close")
        )

        # ----------------------------------------------------
        # SCORES
        # ----------------------------------------------------

        buy_score, buy_reasons = (
            calculate_buy_score(df)
        )

        sell_score, sell_reasons = (
            calculate_sell_score(df)
        )

        # ----------------------------------------------------
        # CURRENT MARKET DATA
        # ----------------------------------------------------

        trend = str(
            row.get(
                "TREND",
                "SIDEWAYS"
            )
        )

        rsi_value = safe_value(
            row.get("RSI"),
            50
        )

        adx_value = safe_value(
            row.get("ADX"),
            0
        )

        supertrend = safe_value(
            row.get(
                "SUPERTREND_DIRECTION"
            )
        )

        # ----------------------------------------------------
        # DEBUG LOG
        # ----------------------------------------------------

        print(
            "\n"
            "=================================================="
        )

        print(
            f"📊 MARKET | Price: {price:.4f}"
        )

        print(
            f"📈 Trend: {trend}"
        )

        print(
            f"📊 RSI: {rsi_value:.2f}"
        )

        print(
            f"📊 ADX: {adx_value:.2f}"
        )

        print(
            f"📊 Supertrend: {supertrend}"
        )

        print(
            f"🟢 BUY SCORE: {buy_score}"
        )

        print(
            f"🔴 SELL SCORE: {sell_score}"
        )

        # ----------------------------------------------------
        # BUY
        # ----------------------------------------------------

        if (
            buy_score >= MIN_SCORE
            and
            buy_score > sell_score
        ):

            print(
                f"🚀 BUY SIGNAL | "
                f"Score {buy_score}/{MIN_SCORE}"
            )

            print(
                "Reasons:",
                " | ".join(
                    buy_reasons
                )
            )

            print(
                "=================================================="
            )

            return "BUY"

        # ----------------------------------------------------
        # SELL
        # ----------------------------------------------------

        if (
            sell_score >= MIN_SCORE
            and
            sell_score > buy_score
        ):

            print(
                f"🔻 SELL SIGNAL | "
                f"Score {sell_score}/{MIN_SCORE}"
            )

            print(
                "Reasons:",
                " | ".join(
                    sell_reasons
                )
            )

            print(
                "=================================================="
            )

            return "SELL"

        # ----------------------------------------------------
        # WAIT
        # ----------------------------------------------------

        print(
            f"⏳ WAIT | "
            f"BUY {buy_score} | "
            f"SELL {sell_score} | "
            f"Required {MIN_SCORE}"
        )

        if buy_reasons:

            print(
                "BUY reasons:",
                " | ".join(
                    buy_reasons
                )
            )

        if sell_reasons:

            print(
                "SELL reasons:",
                " | ".join(
                    sell_reasons
                )
            )

        print(
            "=================================================="
        )

        return "WAIT"

    except Exception as e:

        print(
            f"❌ Strategy Error: {e}"
        )

        return "WAIT"
