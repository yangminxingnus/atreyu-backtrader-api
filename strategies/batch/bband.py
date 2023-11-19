import pandas as pd
import numpy as np
import backtrader as bt
import datetime

class RBreak(bt.Strategy):
    # 策略的参数
    # 策略的参数
    params = (("k1", 0.5),
              ("k2", 0.5),
              )

    # log相应的信息
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or bt.num2date(self.datas[0].datetime[0])
        print('{}, {}'.format(dt.isoformat(), txt))

    # 初始化策略的数据
    def __init__(self):
        # 基本上常用的部分属性变量
        self.bar_num = 0  # next运行了多少个bar
        self.pre_date = None  # 保存上个交易日的日期
        # 使用未来数据，分析下个交易日是否存在夜盘
        self.has_night_trading = False
        # 保存当前交易日的最高价、最低价，收盘价
        self.now_high = 0
        self.now_low = 999999999
        self.now_close = None
        self.now_open = None
        # 保存历史上的每日的最高价、最低价与收盘价
        self.day_high_list = []
        self.day_low_list = []
        self.day_close_list = []
        # 保存交易状态
        self.marketposition = 0

    ## 053.md
    def next(self):
        # 每次运行一次，bar_num自然加1,并更新交易日
        self.current_datetime = bt.num2date(self.datas[0].datetime[0])
        self.current_hour = self.current_datetime.hour
        self.current_minute = self.current_datetime.minute
        self.bar_num += 1
        # 数据
        data = self.datas[0]

        # 更新最高价、最低价、收盘价
        self.now_high = max(self.now_high, data.high[0])
        self.now_low = min(self.now_low, data.low[0])
        if self.now_close is None:
            self.now_open = data.open[0]
        self.now_close = data.close[0]
        # 如果是新的交易日的最后一分钟的数据
        if self.current_hour == 15:
            # 保存当前的三个价格
            self.day_high_list.append(self.now_high)
            self.day_low_list.append(self.now_low)
            self.day_close_list.append(self.now_close)
            # 初始化四个价格
            self.now_high = 0
            self.now_low = 999999999
            self.now_close = None
            # 长度足够，开始计算指标、交易信号
        if len(self.day_high_list) > 1:
            # 计算range
            pre_high = self.day_high_list[-1]
            pre_low = self.day_low_list[-1]
            pre_close = self.day_close_list[-1]
            pivot = (pre_high + pre_low + pre_close) / 3
            # r1 = 2*pivot - pre_low
            # r2 = pivot+pre_high-pre_low
            # r3 = pre_high + 2*(pivot - pre_low)
            # s1 = 2*pivot - pre_high
            # s2 = pivot - (pre_high  - pre_low)
            # s3 = pre_low  - 2*(pre_high-pivot)
            # 六个价格等价于
            # r1 = 2/3*pre_high+2/3*pre_close-1/3*pre_low
            # r3 = 5/3*pre_high+2/3*pre_close-4/3*pre_low
            # s1 = -1/3*pre_high+2/3*pre_close+1/3*pre_low
            # S3 = -4/3*pre_high+2/3*pre_close+5/3*pre_low
            # r1 = self.p.percent_value*pre_high+self.p.percent_value*pre_close-(1-self.p.percent_value)*pre_low
            # r3 = (1+self.p.percent_value)*pre_high+self.p.percent_value*pre_close-2*self.p.percent_value*pre_low
            # s1 = (self.p.percent_value-1)*pre_high+self.p.percent_value*pre_close+(1-self.p.percent_value)*pre_low
            # s3 = -2*self.p.percent_value*pre_high+self.p.percent_value*pre_close+(1+self.p.percent_value)*pre_low
            # 这样设置参数还有一些绕，接下来简化下，设置两个参数，k1和k2，分别代表s1,s2,r1,r2
            r1 = pivot + (self.p.k1) * (pre_high - pre_low)
            r3 = pivot + (self.p.k1 + self.p.k2) * (pre_high - pre_low)
            s1 = pivot - (self.p.k1) * (pre_high - pre_low)
            s3 = pivot - (self.p.k1 + self.p.k2) * (pre_high - pre_low)

            # 开始交易
            open_time_1 = self.current_hour >= 21 and self.current_hour <= 23
            open_time_2 = self.current_hour >= 9 and self.current_hour <= 11
            close = data.close[0]
            if open_time_1 or open_time_2:
                # 开多
                if self.marketposition == 0 and close > r3:
                    self.buy(data, size=1)
                    self.marketposition = 1

                # 开空
                if self.marketposition == 0 and close < s3:
                    self.sell(data, size=1)
                    self.marketposition = -1

                # 平多开空
                if self.marketposition == 1 and close < r1:
                    # 使用target_order也可以，不同的下单方法，本质一样
                    self.close(data)
                    self.sell(data, size=1)
                    self.marketposition = -1

                # 平空开多
                if self.marketposition == -1 and close > s1:
                    # 使用target_order也可以，不同的下单方法，本质一样
                    self.close(data)
                    self.buy(data, size=1)
                    self.marketposition = 1

        # 收盘前平仓
        # self.log(f"{self.current_hour},{self.current_minute}")
        if self.marketposition != 0 and self.current_hour == 14 and self.current_minute == 55:
            self.close(data)
            self.marketposition = 0

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