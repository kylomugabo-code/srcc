import time

from .broker import MT5Broker
from .config import (
    SYMBOLS,
    TIMEFRAME,
    TRADING_MODE,
    ENABLE_LIVE_TRADING,
    KILL_SWITCH,
    RISK_REWARD,
    ATR_MULTIPLIER
)
from .risk_manager import RiskManager
from .strategy import generate_signal


def build_trade(
    symbol,
    signal,
    equity,
    risk_manager
):

    tick = risk_manager

    import MetaTrader5 as mt5

    market_tick = (
        mt5.symbol_info_tick(symbol)
    )

    if market_tick is None:
        return None

    if signal["direction"] == "BUY":

        entry = market_tick.ask

        stop_distance = (
            signal["atr"] *
            ATR_MULTIPLIER
        )

        stop_loss = (
            entry -
            stop_distance
        )

        take_profit = (
            entry +
            stop_distance *
            RISK_REWARD
        )

    else:

        entry = market_tick.bid

        stop_distance = (
            signal["atr"] *
            ATR_MULTIPLIER
        )

        stop_loss = (
            entry +
            stop_distance
        )

        take_profit = (
            entry -
            stop_distance *
            RISK_REWARD
        )

    lots = (
        risk_manager.calculate_lot_size(
            symbol,
            entry,
            stop_loss,
            equity
        )
    )

    if lots <= 0:
        return None

    return {
        "symbol": symbol,
        "direction": signal["direction"],
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "lots": lots,
        "reason": signal["reason"]
    }


def print_trade(trade):

    print("\n-------------------------------")
    print("TRADE SIGNAL")
    print("-------------------------------")

    print(
        f"Pair:       {trade['symbol']}"
    )

    print(
        f"Direction:  {trade['direction']}"
    )

    print(
        f"Entry:      {trade['entry']}"
    )

    print(
        f"Stop Loss:  {trade['stop_loss']}"
    )

    print(
        f"Take Profit:{trade['take_profit']}"
    )

    print(
        f"Lots:       {trade['lots']}"
    )

    print(
        f"Reason:     {trade['reason']}"
    )

    print("-------------------------------")


def main():

    if KILL_SWITCH:

        print(
            "KILL SWITCH IS ENABLED."
        )

        return

    broker = MT5Broker()

    if not broker.connect():
        return

    risk_manager = RiskManager()

    print(
        f"\nTrading mode: {TRADING_MODE.upper()}"
    )

    print(
        f"Pairs: {', '.join(SYMBOLS)}"
    )

    print(
        f"Timeframe: {TIMEFRAME}"
    )

    if (
        TRADING_MODE == "live"
        and not ENABLE_LIVE_TRADING
    ):

        print(
            "Live mode requested, "
            "but ENABLE_LIVE_TRADING=false."
        )

        print(
            "No real orders will be placed."
        )

        live_allowed = False

    else:

        live_allowed = (
            TRADING_MODE == "live"
            and ENABLE_LIVE_TRADING
        )

    try:

        while True:

            account = broker.account()

            if account is None:

                print(
                    "Could not read account."
                )

                time.sleep(10)
                continue

            equity = account.equity

            for symbol in SYMBOLS:

                if not broker.select_symbol(
                    symbol
                ):
                    continue

                if broker.has_position(
                    symbol
                ):

                    continue

                signal = generate_signal(
                    symbol,
                    TIMEFRAME
                )

                if signal is None:
                    continue

                print(
                    f"\nSignal: "
                    f"{symbol} "
                    f"{signal['direction']}"
                )

                allowed, reason = (
                    risk_manager.can_trade(
                        symbol,
                        equity
                    )
                )

                if not allowed:

                    print(
                        f"Rejected: {reason}"
                    )

                    continue

                trade = build_trade(
                    symbol,
                    signal,
                    equity,
                    risk_manager
                )

                if trade is None:

                    print(
                        "Could not calculate "
                        "valid position size."
                    )

                    continue

                print_trade(trade)

                if not live_allowed:

                    print(
                        "PAPER MODE — "
                        "NO REAL ORDER SENT."
                    )

                    continue

                confirmation = input(
                    "\nType EXECUTE to "
                    "send this live order: "
                )

                if confirmation != "EXECUTE":

                    print(
                        "Live order cancelled."
                    )

                    continue

                result = (
                    broker.market_order(
                        trade
                    )
                )

                if result is None:

                    print(
                        "Order failed."
                    )

                elif result.retcode == 10009:

                    print(
                        "LIVE ORDER EXECUTED."
                    )

                    print(
                        f"Order ID: "
                        f"{result.order}"
                    )

                else:

                    print(
                        "Broker rejected "
                        f"order: {result.retcode}"
                    )

            time.sleep(60)

    except KeyboardInterrupt:

        print(
            "\nBot stopped."
        )

    finally:

        broker.disconnect()


if __name__ == "__main__":
    main()
