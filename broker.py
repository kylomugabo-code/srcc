from typing import Optional, Dict

import MetaTrader5 as mt5

from .config import (
    MT5_LOGIN,
    MT5_PASSWORD,
    MT5_SERVER,
    MAGIC_NUMBER
)


class MT5Broker:

    def connect(self) -> bool:

        if not MT5_LOGIN:
            print("MT5_LOGIN is missing.")
            return False

        if not MT5_PASSWORD:
            print("MT5_PASSWORD is missing.")
            return False

        if not MT5_SERVER:
            print("MT5_SERVER is missing.")
            return False

        if not mt5.initialize():

            print(
                "MT5 initialization failed:",
                mt5.last_error()
            )

            return False

        result = mt5.login(
            login=int(MT5_LOGIN),
            password=MT5_PASSWORD,
            server=MT5_SERVER
        )

        if not result:

            print(
                "MT5 login failed:",
                mt5.last_error()
            )

            return False

        print("Connected to MetaTrader 5.")

        return True

    def disconnect(self):

        mt5.shutdown()

    def account(self):

        return mt5.account_info()

    def positions(self):

        positions = mt5.positions_get()

        if positions is None:
            return []

        return list(positions)

    def select_symbol(
        self,
        symbol: str
    ) -> bool:

        info = mt5.symbol_info(
            symbol
        )

        if info is None:
            print(
                f"Symbol not found: {symbol}"
            )
            return False

        if not info.visible:

            if not mt5.symbol_select(
                symbol,
                True
            ):
                print(
                    f"Could not select {symbol}"
                )
                return False

        return True

    def has_position(
        self,
        symbol: str
    ) -> bool:

        positions = self.positions()

        return any(
            p.symbol == symbol
            and p.magic == MAGIC_NUMBER
            for p in positions
        )

    def market_order(
        self,
        trade: Dict
    ) -> Optional[object]:

        symbol = trade["symbol"]

        if not self.select_symbol(symbol):
            return None

        tick = mt5.symbol_info_tick(
            symbol
        )

        if tick is None:
            return None

        if trade["direction"] == "BUY":

            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask

        else:

            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": trade["lots"],
            "type": order_type,
            "price": price,
            "sl": trade["stop_loss"],
            "tp": trade["take_profit"],
            "deviation": 10,
            "magic": MAGIC_NUMBER,
            "comment": "GitHubForexBot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(
            request
        )

        return result
