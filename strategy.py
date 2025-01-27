import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
import datetime
import yfinance as yf
import pandas as pd
import matplotlib
import company as cp


# ———————————————————— 1. Method Section ——————————————————————
class MovingAverageCrossoverStrategy(bt.Strategy):

    params = (
        ('short', 15),
        ('long', 30),
    )
       
    def __init__(self):
        # Create moving average indicators
        self.short_ma = btind.SimpleMovingAverage(self.data, period=self.params.short)
        self.long_ma = btind.SimpleMovingAverage(self.data, period=self.params.long)
        self.crossover = btind.CrossOver(self.short_ma, self.long_ma) 
        print(f"Short period: {self.params.short}, Long period: {self.params.long}")

    def next(self):
        # Buy In Condition
        if self.crossover > 0 and not self.position:
            self.buy()
        
        # Selling Condition
        elif self.crossover < 0 and self.position:
            self.sell()


# ———————————————————— 2. Param weighter ——————————————————————

def weight_short(score):
    return int(30 + (12.5 * score))

def weight_long(score):
    return int(50 + (50 * score))

# ———————————————————— 3. Section Runner ——————————————————————
a = cp.company("A", "2015-01-01", "2025-01-01")

def run(test, company, cash, percentage, sentiment_scale = 1):

    assert type(company) == type(a)

    # Fetch data
    data = yf.download(company.get_ticker(),
                       start = company.get_start_date(), 
                       end = company.get_end_date())
    data.columns = [col[0] for col in data.columns]

    # Convert data to Backtrader feed
    data_feed = bt.feeds.PandasData(dataname=data)

    # Set up Backtrader
    cerebro = bt.Cerebro()
    score = company.get_score()
    if test:
        cerebro.addstrategy(MovingAverageCrossoverStrategy)
        cerebro.addsizer(bt.sizers.PercentSizer, percents = percentage + 100 * (score * sentiment_scale))
    else:
        cerebro.addstrategy(MovingAverageCrossoverStrategy)
        cerebro.addsizer(bt.sizers.PercentSizer, percents = percentage)

    cerebro.adddata(data_feed)

    # Running & Plotting Backtesting
    cerebro.broker.setcash(cash)
    cerebro.run()
    
    cash = cerebro.broker.get_cash()  
    value = cerebro.broker.get_value()  

    return (cash, value)

# ———————————————————— 4. Client end script ——————————————————————

a = cp.company("GOOGL", "2020-01-01", "2025-01-01")
run(True, a, 10000, 50)