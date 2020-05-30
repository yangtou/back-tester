import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_datareader as pdr
import mplcursors

from portfolio import Portfolio
from strategy import Strategy


class MovingAverageCrossStrategy(Strategy):
    """
    Requires:
    symbol - A stock symbol on which to form a strategy on.
    bars - A DataFrame of bars for the above symbol.
    short_window - Lookback period for short moving average.
    long_window - Lookback period for long moving average."""

    def __init__(self, symbol, bars, short_window, long_window):
        self.symbol = symbol
        self.bars = bars

        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        """Returns the DataFrame of symbols containing the signals
        to go long, short or hold (1, -1 or 0)."""
        signals = pd.DataFrame(index=self.bars.index)
        signals['signal'] = 0.0

        short_key = 'short_mavg_%sd' % self.short_window
        long_key = 'long_mavg_%sd' % self.long_window

        # Create the set of short and long simple moving averages over the
        # respective periods
        signals[short_key] = self.bars['Close'].rolling(window=self.short_window, min_periods=1).mean()
        signals[long_key] = self.bars['Close'].rolling(window=self.long_window, min_periods=1).mean()

        # Create a 'signal' (invested or not invested) when the short moving average crosses the long
        # moving average, but only for the period greater than the shortest moving average window
        signals['signal'][self.short_window:] = np.where(
            signals[short_key][self.short_window:] > signals[long_key][self.short_window:], 1.0, 0.0)

        # Take the difference of the signals in order to generate actual trading orders
        signals['positions'] = signals['signal'].diff().fillna(0.0)

        return signals


class MarketOnClosePortfolio(Portfolio):
    """Encapsulates the notion of a portfolio of positions based
    on a set of signals as provided by a Strategy.

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, symbol, bars, signals, shares=1, initial_capital=100000.0):
        self.symbol = symbol
        self.bars = bars
        self.signals = signals
        self.shares = shares
        self.initial_capital = float(initial_capital)
        self.positions = self.generate_positions()

    def generate_positions(self):
        positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
        positions[self.symbol] = self.shares * self.signals['signal']  # Pick how many shares to buy
        return positions

    def backtest_portfolio(self):
        portfolio = self.positions[self.symbol] * self.bars['Close']
        pos_diff = self.positions.diff()

        portfolio['holdings'] = self.positions[self.symbol] * self.bars['Close']
        portfolio['cash'] = self.initial_capital - (pos_diff[self.symbol] * self.bars['Close']).cumsum()

        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change().fillna(0.0)
        return portfolio


def backtest_plot(symbol, shares, start_date, end_date, short_win, long_win, init_capital):
    bars = pdr.DataReader(symbol, "yahoo", start_date, end_date)
    # Create a Moving Average Cross Strategy with 8 and 36, short/long MA windows
    mac = MovingAverageCrossStrategy(symbol, bars, short_window=short_win, long_window=long_win)
    signals = mac.generate_signals()

    # Create a portfolio, with $10,000 initial capital
    portfolio = MarketOnClosePortfolio(symbol, bars, signals, shares, init_capital)
    returns = portfolio.backtest_portfolio()

    # Plot two charts to assess trades and equity curve
    fig = plt.figure()
    fig.patch.set_facecolor('white')  # Set the outer colour to white
    ax1 = fig.add_subplot(211, ylabel='BTC-USD Price and MA crosses')

    short_key = 'short_mavg_%sd' % short_win
    long_key = 'long_mavg_%sd' % long_win

    # Plot the AAPL closing price overlaid with the moving averages
    bars['Close'].plot(ax=ax1, color='0.75', lw=2.)
    signals[[short_key, long_key]].plot(ax=ax1, lw=1.)


    # Plot the "buy" trades
    ax1.plot(signals.index[signals.positions == 1.0],
             signals[short_key][signals.positions == 1.0],
             '^', markersize=10, color='g')

    ax1.set_title('Buy %s %s when %s day crosses %s day, starting $%s' %
                  (shares, symbol, short_win, long_win, init_capital))

    # Plot the "sell" trades
    ax1.plot(signals.index[signals.positions == -1.0],
             signals[short_key][signals.positions == -1.0],
             'v', markersize=10, color='r')

    # Plot the equity curve in dollars
    ax2 = fig.add_subplot(212, ylabel='Total USD Value')
    returns['total'].plot(ax=ax2, lw=2.)

    # Plot the "buy" and "sell" trades against the equity curve
    ax2.plot(returns['returns'].index[signals.positions == 1.0],
             returns['total'][signals.positions == 1.0],
             '^', markersize=10, color='g')
    ax2.plot(returns['returns'].index[signals.positions == -1.0],
             returns['total'][signals.positions == -1.0],
             'v', markersize=10, color='r')

    mplcursors.cursor(hover=True)

    # Plot the figure
    fig.show()


if __name__ == "__main__":
    start = datetime.datetime(2020, 1, 1)
    end = datetime.datetime(2020, 4, 1)
    backtest_plot('BTC-USD', 1, start, end, 6, 23, 10000)
    backtest_plot('ETH-USD', 5, start, end, 6, 23, 10000)

    backtest_plot('BTC-USD', 1, start, end, 8, 21, 10000)
    backtest_plot('AMZN', 100, start, end, 8, 21, 10000)
    input('Press any key to exit..')
