from portfolio import Portfolio
import pandas as pd
import numpy as np


class MarketOnClosePortfolio(Portfolio):
    """Encapsulates the notion of a portfolio of positions based
    on a set of signals as provided by a Strategy.

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
        positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
        positions[self.symbol] = 100 * self.signals['signal']  # This strategy buys 100 shares
        return positions

    def generate_portfolio(self):
        portfolio = pd.DataFrame(index=self.signals.index,
                                 data=self.generate_portfolio_detail(),
                                 columns=['positions', 'cash'])
        portfolio.fillna(method='ffill', inplace=True)
        portfolio['holdings'] = portfolio['positions'] * self.bars['Close']
        portfolio['total'] = portfolio['holdings'] + portfolio['cash']
        portfolio['returns'] = portfolio['total'].pct_change()
        return portfolio

    def generate_portfolio_detail(self):
        portfolio = self.signals[self.signals['positions'] != 0].fillna(0.0)
        portfolio['Close'] = self.bars['Close']
        portfolio['cash'] = np.nan

        current_position = 0.0
        current_capital = self.initial_capital
        for index, row in portfolio.iterrows():
            if row['positions'] == 1:
                shares_to_buy = np.floor(current_capital / row['Close'])
                current_capital -= shares_to_buy * row['Close']
                current_position = shares_to_buy
            elif row['positions'] == -1:
                shares_to_sell = current_position  # sell all of shares
                current_position = 0
                current_capital += shares_to_sell * row['Close']
            row['positions'] = current_position
            row['cash'] = current_capital
        print(portfolio)
        return portfolio
