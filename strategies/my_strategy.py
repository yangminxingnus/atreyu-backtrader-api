import backtrader as bt


class MyStrategy(bt.Strategy):

    def __init__(self):
        pass

    def start(self):
        print("the world call me!")

    def prenext(self):
        print("Not mature")

    def nexstart(self):
        print("Rites of passage")

    def next(self):
        print("A new bar")

    def stop(self):
        print("I should have leave the world!")
