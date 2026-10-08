import os
from dotenv import load_dotenv

load_dotenv()


def get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).lower()
    return value in ("true", "1", "yes", "on")


TRADING_MODE = os.getenv("TRADING_MODE", "paper").lower()

MT5_LOGIN = os.getenv("MT5_LOGIN", "")
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER = os.getenv("MT5_SERVER", "")

SYMBOLS = [
    x.strip()
    for x in os.getenv(
        "SYMBOLS",
        "EURUSD,GBPUSD,USDJPY"
    ).split(",")
    if x.strip()
]

TIMEFRAME = os.getenv("TIMEFRAME", "M15").upper()

RISK_PER_TRADE = float(
    os.getenv("RISK_PER_TRADE", "0.005")
)

MAX_DAILY_LOSS = float(
    os.getenv("MAX_DAILY_LOSS", "0.02")
)

MAX_OPEN_TRADES = int(
    os.getenv("MAX_OPEN_TRADES", "3")
)

MAX_SPREAD_PIPS = float(
    os.getenv("MAX_SPREAD_PIPS", "2.0")
)

RISK_REWARD = float(
    os.getenv("RISK_REWARD", "2.0")
)

ATR_MULTIPLIER = float(
    os.getenv("ATR_MULTIPLIER", "1.5")
)

MAGIC_NUMBER = int(
    os.getenv("MAGIC_NUMBER", "26093001")
)

ENABLE_LIVE_TRADING = get_bool(
    "ENABLE_LIVE_TRADING",
    False
)

KILL_SWITCH = get_bool(
    "KILL_SWITCH",
    False
)
