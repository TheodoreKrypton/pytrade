import pytrade as pt


@pt.singleton
class MyTrade(pt.TradingEnvironment):
    def __init__(self):
        pt.TradingEnvironment.__init__(self)

    def on_init(self):
        pass

    def on_deinit(self):
        pass

    def on_bar(self):
        if self.Time <= 1:
            return
        try:
            if self.Close(1) > self.Close(2):
                self.OrderSend(pt.Operation.op_b, self.Close(0), 1)

            else:
                while self.OrdersTotal():
                    self.OrderSelect(0)
                    self.OrderClose(self.OrderInfo(pt.Info.identifier))
        except pt.TradingEnvException, ex:
            print ex.message

    def on_events(self, reason):
        pass

if __name__ == '__main__':
    mytrade = MyTrade()
    mytrade.run()
