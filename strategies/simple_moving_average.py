import backtrader as bt


class SMA(bt.Strategy):

    def __init__(self):
        self.bt_sma = bt.indicators.MovingAverageSimple(self.data, period=24)
        self.buy_sell_signal = bt.indicators.CrossOver(self.data.close, self.bt_sma)

    def start(self):
        print("the world call me!")

    def prenext(self):
        print("Not mature")
        if len(self) >= 14:
            self.data_ready = True
        else:
            print("Not mature")

    def nexstart(self):
        print("Rites of passage")

    def next(self):
        print("A new bar")
        print(f'check here {self.datas[0].close[0]}')

        # ma_value = sum([self.data.close[-cnt] for cnt in range(0, 24)]) / 24
        # ma_value = self.bt_sma[-1]
        #
        # if self.data.close[0] > ma_value and self.data.close[-1] < ma_value:
        #     print("long", self.data.datetime.date(0))
        #     self.order = self.buy()
        #
        # if self.data.close[0] < ma_value and self.data.close[-1] > ma_value:
        #     print("short", self.data.datetime.date(0))
        #     self.order = self.sell()


        ## 空仓且上穿
        if not self.position and self.buy_sell_signal[0] == 1:
            print("long", self.data.datetime.date(0))
            self.order = self.buy()
        ## 空仓且下穿
        if not self.position and self.buy_sell_signal[-1] == -1:
            print("short", self.data.datetime.date(0))
            self.order = self.sell()

        if self.position and self.buy_sell_signal[0] == 1:
            print("close long", self.data.datetime.date(0))
            self.order = self.close()
            self.order = self.buy()

        if self.position and self.buy_sell_signal[0] == -1:
            print("close short", self.data.datetime.date(0))
            self.order = self.close()
            self.order = self.sell()




    def stop(self):
        print("I should have leave the world!")
