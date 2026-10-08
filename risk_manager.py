import math
from datetime import date
from typing import Optional

import MetaTrader5 as mt5

from .config import (
    RISK_PER_TRADE,
    MAX_DAILY_LOSS,
    MAX_OPEN_TRADES,
    MAX_SPREAD_PIPS
)


class RiskManager:

    def __init__(self):
        self.starting_equity: Optional[float] = None
        self.current_day = date.today()

    def update_day(self, equity: float):

        today = date.today()

        if today != self.current_day:

            self.current_day = today
            self.starting_equity = equity

        if self.starting_equity is None:
            self.starting_equity = equity

    def daily_loss_exceeded(
        self,
        equity: float
    ) -> bool:

        self.update_day(equity)

        if not self.starting_equity:
            return False

        loss = (
            self.starting_equity -
            equity
        )

        if loss <= 0:
            return False

        loss_percentage = (
            loss /
            self.starting_equity
        )

        return (
            loss_percentage >=
            MAX_DAILY_LOSS
        )

    @staticmethod
    def pip_size(symbol: str) -> float:

        if "JPY" in symbol.upper():
            return 0.01

        return 0.0001

    def spread_pips(
        self,
        symbol: str
    ) -> float:

        tick = mt5.symbol_info_tick(
            symbol
        )

        if tick is None:
            return float("inf")

        spread = (
            tick.ask -
            tick.bid
        )

        return (
            spread /
            self.pip_size(symbol)
        )

    def calculate_lot_size(
        self,
        symbol: str,
        entry: float,
        stop_loss: float,
        equity: float
    ) -> float:

        symbol_info = mt5.symbol_info(
            symbol
        )

        if symbol_info is None:
            return 0.0

        risk_money = (
            equity *
            RISK_PER_TRADE
        )

        stop_distance = abs(
            entry -
            stop_loss
        )

        if stop_distance <= 0:
            return 0.0

        tick_size = (
            symbol_info.trade_tick_size
        )

        tick_value = (
            symbol_info.trade_tick_value
        )

        if tick_size <= 0:
            return 0.0

        if tick_value <= 0:
            return 0.0

        loss_per_lot = (
            stop_distance /
            tick_size
        ) * tick_value

        if loss_per_lot <= 0:
            return 0.0

        lots = (
            risk_money /
            loss_per_lot
        )

        min_volume = (
            symbol_info.volume_min
        )

        max_volume = (
            symbol_info.volume_max
        )

        volume_step = (
            symbol_info.volume_step
        )

        lots = max(
            min_volume,
            min(lots, max_volume)
        )

        lots = math.floor(
            lots /
            volume_step
        ) * volume_step

        return round(
            lots,
            2
        )

    def can_trade(
        self,
        symbol: str,
        equity: float
    ) -> tuple[bool, str]:

        if self.daily_loss_exceeded(
            equity
        ):
            return (
                False,
                "Daily loss limit reached"
            )

        positions = mt5.positions_get()

        if positions is None:
            positions = []

        bot_positions = [
            p for p in positions
            if p.magic == 26093001
        ]

        if len(bot_positions) >= MAX_OPEN_TRADES:

            return (
                False,
                "Maximum open positions reached"
            )

        spread = self.spread_pips(
            symbol
        )

        if spread > MAX_SPREAD_PIPS:

            return (
                False,
                f"Spread too high: {spread:.2f} pips"
            )

        return (
            True,
            "Risk checks passed"
        )
