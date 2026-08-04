def calculate_position(balance, risk_percent, entry_price, stop_loss):
    risk_amount = balance * (risk_percent / 100)

    stop_distance = abs(entry_price - stop_loss)

    if stop_distance == 0:
        return 0

    qty = risk_amount / stop_distance

    return round(qty, 4)
