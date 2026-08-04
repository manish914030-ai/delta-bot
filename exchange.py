import ccxt
from config import API_KEY, API_SECRET

exchange = ccxt.delta({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "enableRateLimit": True,
})

def get_balance():
    return exchange.fetch_balance()

def get_ticker(symbol):
    return exchange.fetch_ticker(symbol)

def place_market_order(symbol, side, amount):
    return exchange.create_market_order(symbol, side, amount)
