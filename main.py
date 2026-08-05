df = get_candles(symbol, TIMEFRAME)
signal = check_signal(df)

print(f"{symbol} -> {signal}")

if signal != "WAIT":
    send_message(
        f"🚨 Signal Alert\n\n"
        f"Symbol: {symbol}\n"
        f"Signal: {signal}"
    )
