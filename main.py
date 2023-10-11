import backtrader as bt
from atreyu_backtrader_api import IBData
from strategies.TestPrinter import TestPrinter

import logging

# The following line sets the root logger level as well.
# It's equivalent to both previous statements combined:
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig()

cerebro = bt.Cerebro()

data = IBData(host='127.0.0.1', port=7497, clientId=35,
               name="GOOG",     # Data name
               dataname='GOOG', # Symbol name
               secType='STK',   # SecurityType is STOCK
               exchange='NYSE',# Trading exchange IB's SMART exchange
               currency='USD',  # Currency of SecurityType,  # Currency of SecurityType
                rtbar=True,      # Request Realtime bars
               _debug=True      # Set to True to print out debug messagess from IB TWS API
              # fromdate=dt.datetime(2022, 12, 1),
              # todate=dt.datetime(2023, 1, 5),
              # historical=True,
              # what='BID_ASK',
              )
cerebro.adddata(data)
# Add the printer as a strategy
cerebro.addstrategy(TestPrinter)
logging.info("added")
print("added")
cerebro.run()
print("done")