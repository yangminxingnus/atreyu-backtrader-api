import backtrader as bt
import numpy as np
from datetime import timedelta

class AdvancedMAcrossoverStrategy(bt.Strategy):
    params = (
        ('short_period', 10),
        ('long_period', 50),
        ('holding_period', 14),  # 持股周期（天）
        ('tolerance', 0.1)  # 容忍度，用于比较上行和下行周期的长度
    )

    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.short_period)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.long_period)
        self.in_upward_trend = False
        self.upward_trend_start_price = None
        self.upward_trend_start_date = None
        self.downward_trend_start_date = None
        self.gains_in_upward_trend = []
        self.buy_date = None
        self.buy_price = None
        self.stop_gain_ratio = None

    def next(self):
        # 更新上行周期状态
        if not self.in_upward_trend and self.sma_short[0] > self.sma_long[0]:
            self.in_upward_trend = True
            self.upward_trend_start_price = self.data.close[0]
            self.upward_trend_start_date = self.data.datetime.date(0)
        elif self.in_upward_trend and self.sma_short[0] < self.sma_long[0]:
            self.in_upward_trend = False
            self.downward_trend_start_date = self.data.datetime.date(0)
            max_price = max([self.data.close[i] for i in range(-len(self.data.close) + 1, 1)])
            gain = (max_price - self.upward_trend_start_price) / self.upward_trend_start_price
            self.gains_in_upward_trend.append(gain)

            if self.gains_in_upward_trend:
                self.stop_gain_ratio = np.percentile(self.gains_in_upward_trend, 75)

        # 执行买入操作
        if not self.in_upward_trend and self.upward_trend_start_date and self.downward_trend_start_date:
            upward_duration = self.downward_trend_start_date - self.upward_trend_start_date
            downward_duration = self.data.datetime.date(0) - self.downward_trend_start_date
            if self.data.close[0] <= self.upward_trend_start_price and \
               abs((downward_duration - upward_duration).days) <= self.params.tolerance * upward_duration.days:
                self.buy_date = self.data.datetime.date(0)
                self.buy_price = self.data.close[0]
                self.buy()

        # 检查是否需要卖出
        if self.position:
            days_passed = self.data.datetime.date(0) - self.buy_date
            if days_passed > timedelta(days=self.params.holding_period):
                self.sell()
            elif self.stop_gain_ratio and (self.data.close[0] - self.buy_price) / self.buy_price >= self.stop_gain_ratio:
                self.sell()

    def log(self, txt, dt=None):
        ''' Logging function '''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def stop(self):
        print('Final Portfolio Value: %.2f' % self.broker.getvalue())
