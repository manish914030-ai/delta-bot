# ------------------------------------------------------------
# SUPERTREND - ROBUST ATR BASED VERSION
# ------------------------------------------------------------
def supertrend(df, period=10, multiplier=3.0):

    atr_value = atr(df, period)

    hl2 = (df["high"] + df["low"]) / 2

    basic_upper = hl2 + (multiplier * atr_value)
    basic_lower = hl2 - (multiplier * atr_value)

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

    # First candle where ATR becomes valid
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
    final_upper.iloc[start] = basic_upper.iloc[start]
    final_lower.iloc[start] = basic_lower.iloc[start]

    trend.iloc[start] = 1

    supertrend_value.iloc[start] = (
        final_lower.iloc[start]
    )

    # --------------------------------------------------------
    # MAIN SUPERTREND LOOP
    # --------------------------------------------------------
    for i in range(start + 1, len(df)):

        current_basic_upper = basic_upper.iloc[i]
        current_basic_lower = basic_lower.iloc[i]

        previous_final_upper = final_upper.iloc[i - 1]
        previous_final_lower = final_lower.iloc[i - 1]

        previous_close = df["close"].iloc[i - 1]
        current_close = df["close"].iloc[i]

        # ----------------------------------------------------
        # If current ATR is invalid, carry previous values
        # ----------------------------------------------------
        if pd.isna(atr_value.iloc[i]):

            final_upper.iloc[i] = previous_final_upper
            final_lower.iloc[i] = previous_final_lower
            trend.iloc[i] = trend.iloc[i - 1]

            supertrend_value.iloc[i] = (
                final_lower.iloc[i]
                if trend.iloc[i] == 1
                else final_upper.iloc[i]
            )

            continue

        # ----------------------------------------------------
        # FINAL UPPER BAND
        # ----------------------------------------------------
        if (
            current_basic_upper < previous_final_upper
            or previous_close > previous_final_upper
        ):
            final_upper.iloc[i] = current_basic_upper
        else:
            final_upper.iloc[i] = previous_final_upper

        # ----------------------------------------------------
        # FINAL LOWER BAND
        # ----------------------------------------------------
        if (
            current_basic_lower > previous_final_lower
            or previous_close < previous_final_lower
        ):
            final_lower.iloc[i] = current_basic_lower
        else:
            final_lower.iloc[i] = previous_final_lower

        previous_trend = trend.iloc[i - 1]

        # ----------------------------------------------------
        # TREND DIRECTION
        # ----------------------------------------------------
        if previous_trend == 1:

            if current_close < final_lower.iloc[i]:
                trend.iloc[i] = -1
            else:
                trend.iloc[i] = 1

        else:

            if current_close > final_upper.iloc[i]:
                trend.iloc[i] = 1
            else:
                trend.iloc[i] = -1

        # ----------------------------------------------------
        # SUPERTREND VALUE
        # ----------------------------------------------------
        if trend.iloc[i] == 1:
            supertrend_value.iloc[i] = final_lower.iloc[i]
        else:
            supertrend_value.iloc[i] = final_upper.iloc[i]

    # --------------------------------------------------------
    # FINAL SAFETY
    # --------------------------------------------------------
    trend = trend.ffill()

    supertrend_value = supertrend_value.ffill()

    final_upper = final_upper.ffill()
    final_lower = final_lower.ffill()

    return (
        supertrend_value,
        trend,
        final_upper,
        final_lower
    )
