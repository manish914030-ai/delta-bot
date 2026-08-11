import numpy as np
import pandas as pd


# ============================================================
# DELTA TITAN AI - PROFESSIONAL INDICATORS ENGINE
# ============================================================
#
# EMA 20 / 50 / 200
# RSI
# MACD
# ATR
# ADX + DI
# ROBUST SUPERTREND
# MARKET STRUCTURE
# BOS / CHOCH
# LIQUIDITY SWEEP
# FAIR VALUE GAP
# PREMIUM / DISCOUNT
# VOLUME
# MOMENTUM
#
# Main function:
#     add_indicators(df)
# ============================================================


# ============================================================
# EMA
# ============================================================

def ema(series, period):

    return series.ewm(
        span=period,
        adjust=False,
        min_periods=period
    ).mean()


# ============================================================
# WILDER SMOOTHING
# ============================================================

def wilder_smoothing(series, period):

    return series.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()


# ============================================================
# RSI - WILDER METHOD
# ============================================================

def rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = wilder_smoothing(
        gain,
        period
    )

    avg_loss = wilder_smoothing(
        loss,
        period
    )

    rs = (
        avg_gain /
        avg_loss.replace(0, np.nan)
    )

    result = 100 - (
        100 / (1 + rs)
    )

    # Strong upward candles
    result = result.where(
        ~(
            (avg_loss == 0)
            & (avg_gain > 0)
        ),
        100.0
    )

    # Flat market
    result = result.where(
        ~(
            (avg_loss == 0)
            & (avg_gain == 0)
        ),
        50.0
    )

    return result


# ============================================================
# MACD
# ============================================================

def macd(
    series,
    fast=12,
    slow=26,
    signal=9
):

    fast_ema = ema(
        series,
        fast
    )

    slow_ema = ema(
        series,
        slow
    )

    macd_line = (
        fast_ema -
        slow_ema
    )

    signal_line = macd_line.ewm(
        span=signal,
        adjust=False,
        min_periods=signal
    ).mean()

    histogram = (
        macd_line -
        signal_line
    )

    return (
        macd_line,
        signal_line,
        histogram
    )


# ============================================================
# TRUE RANGE
# ============================================================

def true_range(df):

    previous_close = df["close"].shift(1)

    high_low = (
        df["high"] -
        df["low"]
    )

    high_close = (
        df["high"] -
        previous_close
    ).abs()

    low_close = (
        df["low"] -
        previous_close
    ).abs()

    tr = pd.concat(
        [
            high_low,
            high_close,
            low_close
        ],
        axis=1
    ).max(axis=1)

    return tr


# ============================================================
# ATR - WILDER METHOD
# ============================================================

def atr(df, period=14):

    tr = true_range(df)

    return wilder_smoothing(
        tr,
        period
    )


# ============================================================
# ADX - WILDER CALCULATION
# ============================================================

def adx(df, period=14):

    high = df["high"]
    low = df["low"]

    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = pd.Series(
        np.where(
            (
                (up_move > down_move)
                & (up_move > 0)
            ),
            up_move,
            0.0
        ),
        index=df.index
    )

    minus_dm = pd.Series(
        np.where(
            (
                (down_move > up_move)
                & (down_move > 0)
            ),
            down_move,
            0.0
        ),
        index=df.index
    )

    tr = true_range(df)

    atr_value = wilder_smoothing(
        tr,
        period
    )

    plus_dm_smoothed = wilder_smoothing(
        plus_dm,
        period
    )

    minus_dm_smoothed = wilder_smoothing(
        minus_dm,
        period
    )

    plus_di = (
        100 *
        plus_dm_smoothed /
        atr_value.replace(
            0,
            np.nan
        )
    )

    minus_di = (
        100 *
        minus_dm_smoothed /
        atr_value.replace(
            0,
            np.nan
        )
    )

    di_sum = (
        plus_di +
        minus_di
    )

    dx = (
        100 *
        (plus_di - minus_di).abs() /
        di_sum.replace(
            0,
            np.nan
        )
    )

    adx_value = wilder_smoothing(
        dx,
        period
    )

    return adx_value


# ============================================================
# +DI / -DI
# ============================================================

def directional_indicators(
    df,
    period=14
):

    high = df["high"]
    low = df["low"]

    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = pd.Series(
        np.where(
            (
                (up_move > down_move)
                & (up_move > 0)
            ),
            up_move,
            0.0
        ),
        index=df.index
    )

    minus_dm = pd.Series(
        np.where(
            (
                (down_move > up_move)
                & (down_move > 0)
            ),
            down_move,
            0.0
        ),
        index=df.index
    )

    tr = true_range(df)

    atr_value = wilder_smoothing(
        tr,
        period
    )

    plus_dm_smoothed = wilder_smoothing(
        plus_dm,
        period
    )

    minus_dm_smoothed = wilder_smoothing(
        minus_dm,
        period
    )

    plus_di = (
        100 *
        plus_dm_smoothed /
        atr_value.replace(
            0,
            np.nan
        )
    )

    minus_di = (
        100 *
        minus_dm_smoothed /
        atr_value.replace(
            0,
            np.nan
        )
    )

    return (
        plus_di,
        minus_di
    )


# ============================================================
# SUPERTREND - ROBUST ATR BASED VERSION
# ============================================================

def supertrend(
    df,
    period=10,
    multiplier=3.0
):

    atr_value = atr(
        df,
        period
    )

    hl2 = (
        df["high"] +
        df["low"]
    ) / 2

    basic_upper = (
        hl2 +
        (multiplier * atr_value)
    )

    basic_lower = (
        hl2 -
        (multiplier * atr_value)
    )

    final_upper = pd.Series(
        np.nan,
        index=df.index,
        dtype=float
    )

    final_lower = pd.Series(
        np.nan,
        index=df.index,
        dtype=float
    )

    trend = pd.Series(
        np.nan,
        index=df.index,
        dtype=float
    )

    supertrend_value = pd.Series(
        np.nan,
        index=df.index,
        dtype=float
    )

    # --------------------------------------------------------
    # FIND FIRST VALID ATR
    # --------------------------------------------------------

    valid_positions = np.where(
        atr_value.notna().values
    )[0]

    if len(valid_positions) == 0:

        return (
            supertrend_value,
            trend,
            final_upper,
            final_lower
        )

    start = valid_positions[0]

    # --------------------------------------------------------
    # INITIALIZATION
    # --------------------------------------------------------

    final_upper.iloc[start] = (
        basic_upper.iloc[start]
    )

    final_lower.iloc[start] = (
        basic_lower.iloc[start]
    )

    trend.iloc[start] = 1

    supertrend_value.iloc[start] = (
        final_lower.iloc[start]
    )

    # --------------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------------

    for i in range(
        start + 1,
        len(df)
    ):

        current_basic_upper = (
            basic_upper.iloc[i]
        )

        current_basic_lower = (
            basic_lower.iloc[i]
        )

        previous_final_upper = (
            final_upper.iloc[i - 1]
        )

        previous_final_lower = (
            final_lower.iloc[i - 1]
        )

        previous_close = (
            df["close"].iloc[i - 1]
        )

        current_close = (
            df["close"].iloc[i]
        )

        # ----------------------------------------------------
        # INVALID ATR SAFETY
        # ----------------------------------------------------

        if pd.isna(
            atr_value.iloc[i]
        ):

            final_upper.iloc[i] = (
                previous_final_upper
            )

            final_lower.iloc[i] = (
                previous_final_lower
            )

            trend.iloc[i] = (
                trend.iloc[i - 1]
            )

            if trend.iloc[i] == 1:

                supertrend_value.iloc[i] = (
                    final_lower.iloc[i]
                )

            else:

                supertrend_value.iloc[i] = (
                    final_upper.iloc[i]
                )

            continue

        # ----------------------------------------------------
        # FINAL UPPER BAND
        # ----------------------------------------------------

        if (
            current_basic_upper
            < previous_final_upper
            or
            previous_close
            > previous_final_upper
        ):

            final_upper.iloc[i] = (
                current_basic_upper
            )

        else:

            final_upper.iloc[i] = (
                previous_final_upper
            )

        # ----------------------------------------------------
        # FINAL LOWER BAND
        # ----------------------------------------------------

        if (
            current_basic_lower
            > previous_final_lower
            or
            previous_close
            < previous_final_lower
        ):

            final_lower.iloc[i] = (
                current_basic_lower
            )

        else:

            final_lower.iloc[i] = (
                previous_final_lower
            )

        previous_trend = (
            trend.iloc[i - 1]
        )

        # ----------------------------------------------------
        # TREND DIRECTION
        # ----------------------------------------------------

        if previous_trend == 1:

            if (
                current_close
                < final_lower.iloc[i]
            ):

                trend.iloc[i] = -1

            else:

                trend.iloc[i] = 1

        else:

            if (
                current_close
                > final_upper.iloc[i]
            ):

                trend.iloc[i] = 1

            else:

                trend.iloc[i] = -1

        # ----------------------------------------------------
        # SUPERTREND VALUE
        # ----------------------------------------------------

        if trend.iloc[i] == 1:

            supertrend_value.iloc[i] = (
                final_lower.iloc[i]
            )

        else:

            supertrend_value.iloc[i] = (
                final_upper.iloc[i]
            )

    # --------------------------------------------------------
    # FINAL SAFETY
    # --------------------------------------------------------

    trend = trend.ffill()

    supertrend_value = (
        supertrend_value.ffill()
    )

    final_upper = (
        final_upper.ffill()
    )

    final_lower = (
        final_lower.ffill()
    )

    return (
        supertrend_value,
        trend,
        final_upper,
        final_lower
    )


# ============================================================
# MARKET STRUCTURE
# HH / HL / LH / LL
# ============================================================

def market_structure(
    df,
    swing_length=3
):

    high = df["high"]
    low = df["low"]

    swing_high = pd.Series(
        False,
        index=df.index
    )

    swing_low = pd.Series(
        False,
        index=df.index
    )

    for i in range(
        swing_length,
        len(df) - swing_length
    ):

        current_high = high.iloc[i]
        current_low = low.iloc[i]

        left_highs = high.iloc[
            i - swing_length:i
        ]

        right_highs = high.iloc[
            i + 1:
            i + swing_length + 1
        ]

        left_lows = low.iloc[
            i - swing_length:i
        ]

        right_lows = low.iloc[
            i + 1:
            i + swing_length + 1
        ]

        if (
            current_high >
            left_highs.max()
            and
            current_high >
            right_highs.max()
        ):

            swing_high.iloc[i] = True

        if (
            current_low <
            left_lows.min()
            and
            current_low <
            right_lows.min()
        ):

            swing_low.iloc[i] = True

    structure = pd.Series(
        "NONE",
        index=df.index,
        dtype="object"
    )

    previous_swing_high = np.nan
    previous_swing_low = np.nan

    for i in range(len(df)):

        if swing_high.iloc[i]:

            current_high = (
                high.iloc[i]
            )

            if not np.isnan(
                previous_swing_high
            ):

                if (
                    current_high
                    > previous_swing_high
                ):

                    structure.iloc[i] = "HH"

                else:

                    structure.iloc[i] = "LH"

            previous_swing_high = (
                current_high
            )

        elif swing_low.iloc[i]:

            current_low = (
                low.iloc[i]
            )

            if not np.isnan(
                previous_swing_low
            ):

                if (
                    current_low
                    > previous_swing_low
                ):

                    structure.iloc[i] = "HL"

                else:

                    structure.iloc[i] = "LL"

            previous_swing_low = (
                current_low
            )

    return (
        structure,
        swing_high,
        swing_low
    )


# ============================================================
# BOS / CHoCH
# ============================================================

def structure_breaks(
    df,
    swing_length=3
):

    (
        structure,
        swing_high,
        swing_low
    ) = market_structure(
        df,
        swing_length
    )

    bos = pd.Series(
        False,
        index=df.index
    )

    choch = pd.Series(
        False,
        index=df.index
    )

    break_type = pd.Series(
        "NONE",
        index=df.index,
        dtype="object"
    )

    last_high = np.nan
    last_low = np.nan

    market_bias = 0

    for i in range(len(df)):

        if swing_high.iloc[i]:

            last_high = (
                df["high"].iloc[i]
            )

        if swing_low.iloc[i]:

            last_low = (
                df["low"].iloc[i]
            )

        close = df["close"].iloc[i]

        bullish_break = (
            not np.isnan(last_high)
            and
            close > last_high
        )

        bearish_break = (
            not np.isnan(last_low)
            and
            close < last_low
        )

        if bullish_break:

            if market_bias == -1:

                choch.iloc[i] = True

                break_type.iloc[i] = (
                    "BULLISH_CHOCH"
                )

            else:

                bos.iloc[i] = True

                break_type.iloc[i] = (
                    "BULLISH_BOS"
                )

            market_bias = 1

            # Prevent repeated break signals
            last_high = np.nan

        elif bearish_break:

            if market_bias == 1:

                choch.iloc[i] = True

                break_type.iloc[i] = (
                    "BEARISH_CHOCH"
                )

            else:

                bos.iloc[i] = True

                break_type.iloc[i] = (
                    "BEARISH_BOS"
                )

            market_bias = -1

            # Prevent repeated break signals
            last_low = np.nan

    return (
        bos,
        choch,
        break_type
    )


# ============================================================
# LIQUIDITY SWEEPS
# ============================================================

def liquidity_sweeps(
    df,
    lookback=20
):

    rolling_high = (
        df["high"]
        .shift(1)
        .rolling(
            lookback,
            min_periods=lookback
        )
        .max()
    )

    rolling_low = (
        df["low"]
        .shift(1)
        .rolling(
            lookback,
            min_periods=lookback
        )
        .min()
    )

    # Bearish sweep
    bearish_sweep = (
        (df["high"] > rolling_high)
        &
        (df["close"] < rolling_high)
    )

    # Bullish sweep
    bullish_sweep = (
        (df["low"] < rolling_low)
        &
        (df["close"] > rolling_low)
    )

    return (
        bullish_sweep,
        bearish_sweep
    )


# ============================================================
# FAIR VALUE GAP
# ============================================================

def fair_value_gaps(df):

    bullish_fvg = (
        df["low"] >
        df["high"].shift(2)
    )

    bearish_fvg = (
        df["high"] <
        df["low"].shift(2)
    )

    bullish_fvg_size = pd.Series(
        np.nan,
        index=df.index
    )

    bearish_fvg_size = pd.Series(
        np.nan,
        index=df.index
    )

    bullish_fvg_size.loc[
        bullish_fvg
    ] = (
        df.loc[bullish_fvg, "low"]
        -
        df["high"].shift(2).loc[
            bullish_fvg
        ]
    )

    bearish_fvg_size.loc[
        bearish_fvg
    ] = (
        df["low"].shift(2).loc[
            bearish_fvg
        ]
        -
        df.loc[bearish_fvg, "high"]
    )

    return (
        bullish_fvg,
        bearish_fvg,
        bullish_fvg_size,
        bearish_fvg_size
    )


# ============================================================
# PREMIUM / DISCOUNT
# ============================================================

def premium_discount(
    df,
    lookback=50
):

    rolling_high = (
        df["high"]
        .rolling(
            lookback,
            min_periods=lookback
        )
        .max()
    )

    rolling_low = (
        df["low"]
        .rolling(
            lookback,
            min_periods=lookback
        )
        .min()
    )

    equilibrium = (
        rolling_high +
        rolling_low
    ) / 2

    range_size = (
        rolling_high -
        rolling_low
    )

    premium_level = (
        equilibrium +
        range_size * 0.25
    )

    discount_level = (
        equilibrium -
        range_size * 0.25
    )

    zone = pd.Series(
        "EQUILIBRIUM",
        index=df.index,
        dtype="object"
    )

    zone.loc[
        df["close"] >= premium_level
    ] = "PREMIUM"

    zone.loc[
        df["close"] <= discount_level
    ] = "DISCOUNT"

    return (
        equilibrium,
        premium_level,
        discount_level,
        zone
    )


# ============================================================
# VOLUME ANALYSIS
# ============================================================

def volume_analysis(
    df,
    period=20
):

    if "volume" not in df.columns:

        volume_average = pd.Series(
            np.nan,
            index=df.index
        )

        volume_ratio = pd.Series(
            np.nan,
            index=df.index
        )

        volume_confirmed = pd.Series(
            True,
            index=df.index
        )

        return (
            volume_average,
            volume_ratio,
            volume_confirmed
        )

    volume_average = (
        df["volume"]
        .rolling(
            period,
            min_periods=period
        )
        .mean()
    )

    volume_ratio = (
        df["volume"] /
        volume_average.replace(
            0,
            np.nan
        )
    )

    volume_confirmed = (
        volume_ratio >= 1.0
    )

    return (
        volume_average,
        volume_ratio,
        volume_confirmed
    )


# ============================================================
# MAIN INDICATOR FUNCTION
# ============================================================

def add_indicators(df):

    """
    Add all Delta Titan AI indicators.

    Required:
        open
        high
        low
        close

    Optional:
        volume
    """

    # --------------------------------------------------------
    # COPY DATAFRAME
    # --------------------------------------------------------

    df = df.copy()

    required_columns = [
        "open",
        "high",
        "low",
        "close"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing required OHLC columns: {missing}"
        )

    # --------------------------------------------------------
    # NUMERIC CONVERSION
    # --------------------------------------------------------

    for column in required_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    if "volume" in df.columns:

        df["volume"] = pd.to_numeric(
            df["volume"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # REMOVE INVALID OHLC
    # --------------------------------------------------------

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # --------------------------------------------------------
    # EMA
    # --------------------------------------------------------

    df["EMA20"] = ema(
        df["close"],
        20
    )

    df["EMA50"] = ema(
        df["close"],
        50
    )

    df["EMA200"] = ema(
        df["close"],
        200
    )

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    df["RSI"] = rsi(
        df["close"],
        14
    )

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    (
        df["MACD"],
        df["MACD_SIGNAL"],
        df["MACD_HIST"]
    ) = macd(
        df["close"],
        12,
        26,
        9
    )

    # --------------------------------------------------------
    # ATR
    # --------------------------------------------------------

    df["ATR"] = atr(
        df,
        14
    )

    df["ATR_PCT"] = (
        df["ATR"] /
        df["close"]
    ) * 100

    # --------------------------------------------------------
    # ADX
    # --------------------------------------------------------

    df["ADX"] = adx(
        df,
        14
    )

    (
        df["PLUS_DI"],
        df["MINUS_DI"]
    ) = directional_indicators(
        df,
        14
    )

    # --------------------------------------------------------
    # ROBUST SUPERTREND
    # --------------------------------------------------------

    (
        df["SUPERTREND"],
        df["SUPERTREND_DIRECTION"],
        df["SUPERTREND_UPPER"],
        df["SUPERTREND_LOWER"]
    ) = supertrend(
        df,
        period=10,
        multiplier=3.0
    )

    # --------------------------------------------------------
    # TREND
    # --------------------------------------------------------

    df["TREND"] = "SIDEWAYS"

    bullish_trend = (
        (df["EMA20"] > df["EMA50"])
        &
        (df["EMA50"] > df["EMA200"])
        &
        (df["SUPERTREND_DIRECTION"] == 1)
    )

    bearish_trend = (
        (df["EMA20"] < df["EMA50"])
        &
        (df["EMA50"] < df["EMA200"])
        &
        (df["SUPERTREND_DIRECTION"] == -1)
    )

    df.loc[
        bullish_trend,
        "TREND"
    ] = "BULLISH"

    df.loc[
        bearish_trend,
        "TREND"
    ] = "BEARISH"

    # --------------------------------------------------------
    # TREND STRENGTH
    # --------------------------------------------------------

    df["TREND_STRENGTH"] = "WEAK"

    df.loc[
        df["ADX"] >= 25,
        "TREND_STRENGTH"
    ] = "STRONG"

    df.loc[
        df["ADX"] >= 40,
        "TREND_STRENGTH"
    ] = "VERY_STRONG"

    # --------------------------------------------------------
    # MARKET STRUCTURE
    # --------------------------------------------------------

    (
        df["MARKET_STRUCTURE"],
        df["SWING_HIGH"],
        df["SWING_LOW"]
    ) = market_structure(
        df,
        swing_length=3
    )

    # --------------------------------------------------------
    # BOS / CHOCH
    # --------------------------------------------------------

    (
        df["BOS"],
        df["CHOCH"],
        df["STRUCTURE_BREAK"]
    ) = structure_breaks(
        df,
        swing_length=3
    )

    # --------------------------------------------------------
    # LIQUIDITY SWEEP
    # --------------------------------------------------------

    (
        df["BULLISH_LIQUIDITY_SWEEP"],
        df["BEARISH_LIQUIDITY_SWEEP"]
    ) = liquidity_sweeps(
        df,
        lookback=20
    )

    # --------------------------------------------------------
    # FAIR VALUE GAP
    # --------------------------------------------------------

    (
        df["BULLISH_FVG"],
        df["BEARISH_FVG"],
        df["BULLISH_FVG_SIZE"],
        df["BEARISH_FVG_SIZE"]
    ) = fair_value_gaps(df)

    # --------------------------------------------------------
    # PREMIUM / DISCOUNT
    # --------------------------------------------------------

    (
        df["EQUILIBRIUM"],
        df["PREMIUM_LEVEL"],
        df["DISCOUNT_LEVEL"],
        df["MARKET_ZONE"]
    ) = premium_discount(
        df,
        lookback=50
    )

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    (
        df["VOLUME_AVG"],
        df["VOLUME_RATIO"],
        df["VOLUME_CONFIRMED"]
    ) = volume_analysis(
        df,
        period=20
    )

    # --------------------------------------------------------
    # MOMENTUM
    # --------------------------------------------------------

    df["MOMENTUM"] = "NEUTRAL"

    bullish_momentum = (
        (df["RSI"] > 50)
        &
        (df["MACD"] > df["MACD_SIGNAL"])
    )

    bearish_momentum = (
        (df["RSI"] < 50)
        &
        (df["MACD"] < df["MACD_SIGNAL"])
    )

    df.loc[
        bullish_momentum,
        "MOMENTUM"
    ] = "BULLISH"

    df.loc[
        bearish_momentum,
        "MOMENTUM"
    ] = "BEARISH"

    # --------------------------------------------------------
    # FINAL CLEANUP
    # --------------------------------------------------------

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    return df
