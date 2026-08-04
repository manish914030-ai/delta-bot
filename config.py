from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("DELTA_API_KEY")
API_SECRET = os.getenv("DELTA_API_SECRET")

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XAUUSD"
]

TIMEFRAMES = [
    "5m",
    "15m",
    "30m",
    "1h"
]

LEVERAGE = 10
RISK_PERCENT = 2
ACCOUNT_BALANCE = 80
