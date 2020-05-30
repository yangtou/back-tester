import numpy as np
import pandas as pd
import quandl

from portfolio import Portfolio
from strategy import Strategy


class RandomForcastingStrategy(Strategy):
    def __init__(self, symbol, bars):
        self.symbol = symbol
        self.bars = bars

    def generate_signals(self):
        signals = pd.DataFrame(index=self.bars.index)
        signals['signal'] = np.sign(np.random.randn(len(signals)))
        signals['signal'][0:5] = 0.0
        return signals


class MarketOnOpenPortfolio(Portfolio):
    """Inherits Portfolio to create a system that purchases 100 units of
    a particular symbol upon a long/short signal, assuming the market
    open price of a bar.

    In addition, there are zero transaction costs and cash can be immediately
    borrowed for shorting (no margin posting or interest requirements).

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, symbol, bars, signals, initial_capital=100000.0):
        self.symbol = symbol
        self.bars = bars
        self.signals = signals
        self.initial_capital = float(initial_capital)
        self.positions = self.generate_positions()

    def generate_positions(self):
        """Creates a 'positions' DataFrame that simply longs or shorts
        100 of the particular symbol based on the forecast signals of
        {1, 0, -1} from the signals DataFrame."""

        # Position is how much share of stock you own at that given time
        positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
        positions[self.symbol] = 100*self.signals['signal']
        return positions

    def backtest_portfolio(self):
        """Constructs a portfolio from the positions DataFrame by
        assuming the ability to trade at the precise market open price
        of each bar (an unrealistic assumption!).

        Calculates the total of cash and the holdings (market price of
        each position per bar), in order to generate an equity curve
        ('total') and a set of bar-based returns ('returns').

        Returns the portfolio object to be used elsewhere."""

        # Construct the portfolio DataFrame to use the same index
        # as 'positions' and with a set of 'trading orders' in the
        # 'pos_diff' object, assuming market open prices.
        portfolio = self.positions*self.bars['Open']
        # diff() means subtract previous element, so if position looks like 100, 0, -100
        # diff() will return -100, -100, that means there are two sell execution of quantity 100
        pos_diff = self.positions.diff()

        # Create the 'holdings' and 'cash' series by running through
        # the trades and adding/subtracting the relevant quantity from
        # each column
        portfolio['holdings'] = (self.positions * self.bars['Open']).sum(axis=1)  # 沿着y轴相加， 合并时间
        portfolio['cash'] = self.initial_capital - (pos_diff * self.bars['Open']).sum(axis=1).cumsum()  # pos_diff * "price" = total notional amount for all executions

        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change()
        return portfolio


if __name__ == "__main__":
    symbol = 'APPL'

    # Obtain daily bars of SPY (ETF that generally
    # follows the S&P500)     # Obtain daily bars of SPY (ETF that generally
    #     # follows the S&P500)
    bars = quandl.get("WIKI/AAPL", collapse="daily", start_date="2017-03-23")

    rfs = RandomForcastingStrategy(symbol, bars)
    signals = rfs.generate_signals()

    portfolio = MarketOnOpenPortfolio(symbol, bars, signals, initial_capital=100000.0)
    returns = portfolio.backtest_portfolio()

    print(returns.tail(10))


