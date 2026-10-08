from typing import Optional, Dict

import MetaTrader5 as mt5
import pandas as pd

from .indicators import add_indicators


TIMEFRAME_MAP = {
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
}


def get_market_data(
    symbol: str,
    timeframe_name: str,
    bars: int = 300
) -> Optional[pd.DataFrame]:

    timeframe = TIMEFRAME_MAP.get(
        timeframe_name
    )

    if timeframe is None:
        raise ValueError(
            f"Unsupported timeframe: {timeframe_name}"
        )

    rates = mt5.copy_rates_from_pos(
        symbol,
        timeframe,
        0,
        bars
    )

    if rates is None:
        return None

    if len(rates) < 210:
        return None

    df = pd.DataFrame(rates)

    df["time"] = pd.to_datetime(
        df["time"],
        unit="s"
    )

    return add_indicators(df)


def generate_signal(
    symbol: str,
    timeframe_name: str
) -> Optional[Dict]:

    df = get_market_data(
        symbol,
        timeframe_name
    )

    if df is None:
        return None

    # Use the last completed candle.
    candle = df.iloc[-2]

    required = [
        "ema50",
        "ema200",
        "rsi",
        "atr"
    ]

    for column in required:
        if pd.isna(candle[column]):
            return None

    close = float(candle["close"])
    ema50 = float(candle["ema50"])
    ema200 = float(candle["ema200"])
    rsi = float(candle["rsi"])
    atr = float(candle["atr"])

    # BUY
    if (
        close > ema200
        and ema50 > ema200
        and 50 <= rsi <= 68
    ):
        return {
            "direction": "BUY",
            "price": close,
            "atr": atr,
            "reason": (
                "Price above EMA200, "
                "EMA50 above EMA200, "
                "RSI bullish"
            )
        }

    # SELL
    if (
        close < ema200
        and ema50 < ema200
        and 32 <= rsi <= 50
    ):
        return {
            "direction": "SELL",
            "price": close,
            "atr": atr,
            "reason": (
                "Price below EMA200, "
                "EMA50 below EMA200, "
                "RSI bearish"
            )
        }

    return None
