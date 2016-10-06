"""Example
1. Configure "config.json"
2. Implementing trading.TradingEnvironment
3. run
"""


import pytrade
from matplotlib import pyplot


class Example(pytrade.TradingEnvironment):
    def __init__(self):
        pytrade.TradingEnvironment.__init__(self)
        self.holding = 0

    def on_init(self):
        pass

    def on_deinit(self):
        pass

    def on_bar(self):
        identifier = self.OrderSend(pytrade.Ticket.Operation.op_b, None, 1)
        self.OrderClose(identifier)
        pass

    def on_events(self, reason):
        pass


trd = Example()
trd.run()
pyplot.plot(trd.balance)
pyplot.show()
