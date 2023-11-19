import backtrader as bt

from strategies.strategy import Strategy


class Aberration(Strategy):
    """Bollinger Bands Strategy
    """

    params = (
        ('period', 20),
        ('devfactor', 2),
    )

    def __init__(self):
        # Add a BBand indicator
        self.bband = bt.indicators.BBands(self.datas[0],
                                          period=self.params.period,
                                          devfactor=self.params.devfactor)
        super(Aberration, self).__init__()
        self.addminperiod(self.params.period)

    def next(self):
        super(Aberration, self).next()

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        if self.orefs:
            return
        current_datetime = self.data.datetime.datetime()
        a = self.dataclose[-1]
        b = self.bband.lines.bot[0]
        c = self.bband.lines.top[0]
        if self.dataclose[-1] < self.bband.lines.bot[0] and not self.position:
            self.buy()

        if self.dataclose[-1] > self.bband.lines.top[0] and self.position:
            self.sell()

    def stop(self):
        from settings import CONFIG
        pnl = round(self.broker.getvalue() - CONFIG['capital_base'], 2)
        print('Aberration Period: {} Final PnL: {}'.format(
            self.params.period, pnl))
