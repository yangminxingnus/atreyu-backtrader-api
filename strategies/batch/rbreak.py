import pandas as pd
import numpy as np
import backtrader as bt
import datetime

class Bband(bt.Strategy):
    # 策略的参数
    # 策略的参数
    # 策略的参数
    params = (("boll_period", 20),
              ("boll_mult", 2),
              )

    # log相应的信息
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or bt.num2date(self.datas[0].datetime[0])
        print('{}, {}'.format(dt.isoformat(), txt))

    # 初始化策略的数据
    def __init__(self):
        # 计算布林带指标，大名鼎鼎的布林带策略
        self.boll_indicator = bt.indicators.BollingerBands(self.datas[0], period=self.p.boll_period,
                                                           devfactor=self.p.boll_mult)

        # 保存交易状态
        self.marketposition = 0

    ## 053.md
    def next(self):
        # 每次运行一次，bar_num 自然加 1,并更新交易日
        self.current_datetime = bt.num2date(self.datas[0].datetime[0])
        self.current_hour = self.current_datetime.hour
        self.current_minute = self.current_datetime.minute
        # 数据
        data = self.datas[0]
        # 指标值
        # 布林带上轨
        top = self.boll_indicator.top
        # 布林带下轨
        bot = self.boll_indicator.bot
        # 布林带中轨
        mid = self.boll_indicator.mid

        # 开多
        if self.marketposition == 0 and data.close[0] > top[0] and data.close[-1] < top[-1]:
            # 获取一倍杠杆下单的手数
            info = self.broker.getcommissioninfo(data)
            symbol_multi = info.p.mult
            close = data.close[0]
            self.buy(data, 1)
            self.marketposition = 1

        # 开空
        # if self.marketposition == 0 and data.close[0] < bot[0] and data.close[-1] > bot[-1]:
        #     # 获取一倍杠杆下单的手数
        #     info = self.broker.getcommissioninfo(data)
        #     symbol_multi = info.p.mult
        #     close = data.close[0]
        #     total_value = self.broker.getvalue()
        #     lots = total_value / (symbol_multi * close)
        #     self.sell(data, size=lots)
        #     self.marketposition = -1

        # 平多
        if self.marketposition == 1 and data.close[0] < mid[0] and data.close[-1] > mid[-1]:
            self.close()
            self.marketposition = 0

        # 平空
        # if self.marketposition == -1 and data.close[0] > mid[0] and data.close[-1] < mid[-1]:
        #     self.close()
        #     self.marketposition = 0

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