import pandas_datareader as pdr
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option('display.max_colwidth', -1)  # or 199

def plot_close(bars, symbol):
    close = bars['Close']
    close.plot(title=symbol)
    plt.show()


if __name__ == "__main__":
    symbol = "AAPL"
    short_window = 100
    long_window = 400
    start_date = datetime.datetime(2010, 1, 1)
    end_date = datetime.datetime(2020, 1, 1)
    initial_capital = 50000

    bars = pdr.DataReader(symbol, "yahoo", start_date, end_date)
    # plot_close(bars, symbol)

    signal = pd.DataFrame(index=bars.index)
    signal['signal'] = 0.0
    signal['Close'] = bars['Close']
    signal['short_mavg'] = bars['Close'].rolling(window=short_window, min_periods=1).mean()
    signal['long_mavg'] = bars['Close'].rolling(window=long_window, min_periods=1).mean()

    signal['signal'][short_window:] = \
        np.where(signal['short_mavg'][short_window:] > signal['long_mavg'][short_window:], 1, 0)
    signal['positions'] = signal['signal'].diff()

    positions = pd.DataFrame(index=signal.index).fillna(0)
    positions[symbol] = 100 * signal['signal']  # how many shares do i hold now
    pos_diff = positions.diff()  # quantity of each trade

    portfolio = positions[symbol] * bars['Close']  # how much much i own now
    portfolio['holdings'] = positions[symbol] * bars['Close']
    portfolio['cash'] = initial_capital - (pos_diff[symbol] * bars['Close']).cumsum()
    portfolio['total'] = portfolio['holdings'] + portfolio['cash']
    portfolio['returns'] = portfolio['total'].pct_change().fillna(0.0)

    fig = plt.figure()
    fig.patch.set_facecolor('white')
    # ax1 = fig.add_subplot(221, ylabel='Price in $')  # first graph in a 2 x 2 grid
    # ax2 = fig.add_subplot(333, ylabel='Portfolio value in $')  # thir graph in a 3 x 3 grid

    # plot price graph
    ax1 = fig.add_subplot(311, ylabel='Price in $')
    bars['Close'].plot(legend=True, ax=ax1, color='b', lw=2)  # lw - line width
    signal[['short_mavg', 'long_mavg']].plot(ax=ax1, color=['g', 'r'], lw=2)
    # plot when "buy" trade happens
    ax1.plot(signal.index[signal['positions'] == 1.0],
             signal['short_mavg'][signal['positions'] == 1.0],
             '^', markersize=10, color='m')
    # plot when "sell" trade happens
    ax1.plot(signal.index[signal['positions'] == -1.0],
             signal['short_mavg'][signal['positions'] == -1.0],
             'v', markersize=10, color='k')

    # plot the equity curve in dollars
    ax2 = fig.add_subplot(313, ylabel='Portfolio value in $')
    portfolio['total'].plot(ax=ax2, lw=2)
    # plot "buy" and "sell" trades against equity curve
    ax2.plot(signal.index[signal['positions'] == 1.0],
             portfolio['total'][signal['positions'] == 1.0],
             '^', markersize=10, color='m')
    ax2.plot(signal.index[signal['positions'] == -1.0],
             portfolio['total'][signal['positions'] == -1.0],
             'v', markersize=10, color='k')

    fig.show()
    input("press any key to exit..")


    # print(positions)
    #
    # print(portfolio.to_string())


