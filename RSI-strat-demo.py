import backtrader as bt
from datetime import datetime

class RSIStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),       # RSI period
        ('overbought', 70),       # RSI value above which to sell
        ('oversold', 30),         # RSI value below which to buy
    )

    def __init__(self):
        # Initialize the RSI indicator
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

    def log(self, txt, dt=None):
        ''' Logging function for this strategy '''
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')

    def next(self):
        if self.rsi < self.params.oversold:  # RSI below oversold threshold
            if not self.position:  # If not in the market
                self.buy()  # Enter a long position
                self.log(f'BUY ORDER CREATED, Price: {self.data.close[0]:.2f}, RSI: {self.rsi[0]:.2f}')

        elif self.rsi > self.params.overbought:  # RSI above overbought threshold
            if self.position:  # If already in the market
                self.sell()  # Exit the position
                self.log(f'SELL ORDER CREATED, Price: {self.data.close[0]:.2f}, RSI: {self.rsi[0]:.2f}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(f'TRADE PROFIT, Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}')

# Backtesting the strategy
if __name__ == '__main__':
    # Initialize Cerebro engine
    cerebro = bt.Cerebro()

    # Add the strategy
    cerebro.addstrategy(RSIStrategy)

    # Load data (e.g., from Yahoo Finance)
    data = bt.feeds.YahooFinanceData(
        dataname='NIFTY.csv', 
        fromdate=datetime(2019, 8, 16), 
        todate=datetime(2024, 8, 16)
    )
    cerebro.adddata(data)

    # Set the initial cash
    cerebro.broker.set_cash(10000)

    # Set the commission (e.g., 0.1%)
    cerebro.broker.setcommission(commission=0.001)

    # Run the strategy
    cerebro.run()

    # Plot the results
    cerebro.plot()
