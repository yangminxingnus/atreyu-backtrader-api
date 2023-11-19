import pandas as pd
import numpy as np
import backtrader as bt
import datetime

class PressureSupport(bt.Strategy):

    params = (('short_period', 10),
              ("middle_period", 60),
              ("long_period", 250),
              )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('{}, {}'.format(dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.bar_num = 0
        # 保存均线数据
        # self.stock_short_ma_dict={data._name:bt.talib.SMA(data.close,timeperiod=self.p.short_period) for data in self.datas}
        # self.stock_short_ma_dict={data._name:bt.talib.SMA(data.close,timeperiod=self.p.long_period) for data in self.datas}
        self.stock_ma_diff_dict = {data._name: bt.indicators.MovingAverageSimple(data.close, period=self.p.short_period) -
                                               bt.indicators.MovingAverageSimple(data.close, period=self.p.long_period) for data in
                                   self.datas}

    ## 053.md
    def next(self):
        data = self.datas[0]
        # 三条均线，保存成 line 的数据结构
        pre_high = data.high[-1]
        pre_low = data.low[-1]
        pre_close = data.close[-1]
        # c 的价格
        C_price = (pre_high + pre_low + pre_close) / 3
        # R_price
        R_price = 2 * C_price - pre_low
        # 当前的仓位
        size = self.getposition(data).size

        # 平多信号
        if size > 0:
            order = self.sell(data, size=size, exectype=bt.Order.Limit, price=R_price,
                              valid=self.datas[0].datetime.date(0) + datetime.timedelta(days=1))
            # 开多信号,设置一个 C_price 的买入止损单，当价格达到 C_price 的时候买入
        if size == 0:
            order = self.buy(data, exectype=bt.Order.Stop, price=C_price,
                             valid=self.datas[0].datetime.date(0) + datetime.timedelta(days=1))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # order 被提交和接受
            return
        if order.status == order.Rejected:
            self.log(f"order is rejected : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Margin:
            self.log(f"order need more margin : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Cancelled:
            self.log(f"order is concelled : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Partial:
            self.log(f"order is partial : order_ref:{order.ref}  order_info:{order.info}")
        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status == order.Completed:
            if order.isbuy():
                self.log("buy result : buy_price : {} , buy_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))

            else:  # Sell
                self.log("sell result : sell_price : {} , sell_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))

    def notify_trade(self, trade):
        # 一个 trade 结束的时候输出信息
        if trade.isclosed:
            self.log('closed symbol is : {} , total_profit : {} , net_profit : {}' .format(
                            trade.getdataname(),trade.pnl, trade.pnlcomm))
        if trade.isopen:
            self.log('open symbol is : {} , price : {} ' .format(
                            trade.getdataname(),trade.price))