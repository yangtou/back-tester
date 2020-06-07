# ma_cross.py

import datetime
import mplcursors
import matplotlib.pyplot as plt

from pandas_datareader import data
from MovingAverageCrossStrategy import MovingAverageCrossStrategy
from MarketOnClosePortfolio import MarketOnClosePortfolio


def plot(stratedgy, portfolio):
    signals = stratedgy.get_signals()
    short_mavg = stratedgy.get_short_mavg()
    long_mavg = stratedgy.get_long_mavg()
    positions = stratedgy.get_positions()

    # Plot two charts to assess trades and equity curve
    fig = plt.figure()
    fig.patch.set_facecolor('white')  # Set the outer colour to white
    ax1 = fig.add_subplot(311, ylabel='Price in $')

    # Plot the AAPL closing price overlaid with the moving averages
    bars['Close'].plot(legend=True, ax=ax1, color='b', lw=2.)
    short_mavg.plot(legend=True, ax=ax1, color='g', lw=2.)
    long_mavg.plot(legend=True, ax=ax1, color='r', lw=2.)

    # Plot the "buy" trades against AAPL
    ax1.plot(signals.index[positions == 1.0],
             short_mavg[positions == 1.0],
             '^', markersize=10, color='m')

    # Plot the "sell" trades against AAPL
    ax1.plot(signals.index[positions == -1.0],
             short_mavg[positions == -1.0],
             'v', markersize=10, color='k')

    # Plot the equity curve in dollars
    ax2 = fig.add_subplot(313, ylabel='Portfolio value in $')
    portfolio['total'].plot(ax=ax2, lw=2.)

    # Plot the "buy" and "sell" trades against the equity curve
    ax2.plot(signals.index[signals.positions == 1.0],
             portfolio['total'][positions == 1.0],
             '^', markersize=10, color='m')
    ax2.plot(signals.index[signals.positions == -1.0],
             portfolio['total'][positions == -1.0],
             'v', markersize=10, color='k')

    # Plot the figure
    mplcursors.cursor(hover=True)
    fig.show()
    input("press any key to exit..")


if __name__ == "__main__":
    # Obtain daily bars of AAPL from Yahoo Finance for the period
    # 1st Jan 1990 to 1st Jan 2002 - This is an example from ZipLine
    symbol = 'FB'
    short_window = 50
    long_window = 200
    initial_capital = 50000.0
    start_date = datetime.datetime(2010, 1, 1)
    end_date = datetime.datetime(2020, 1, 1)
    bars = data.DataReader(symbol, "yahoo", start_date, end_date)

    # Create a Moving Average Cross Strategy instance with a short moving
    # average window of 100 days and a long window of 400 days
    mac = MovingAverageCrossStrategy(symbol, bars, short_window=short_window, long_window=long_window)
    signals = mac.get_signals()

    # Create a portfolio of AAPL, with $100,000 initial capital
    mcp = MarketOnClosePortfolio(symbol, bars, signals, initial_capital=initial_capital)
    portfolio = mcp.generate_portfolio()
    print(portfolio)
    plot(mac, portfolio)
