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
        if self.Time == 0:
            return
        try:
            if self.Close(0) > self.Close(1):
                self.OrderSend(pt.Operation.op_b, self.Close(0), 1)

            else:
                if self.OrdersTotal() != 0:
                    for i in range(0, self.OrdersTotal()):
                        self.OrderSelect(i)
                        self.OrderClose(self.OrderInfo(pt.Info.identifier))
        except pt.NoPriceException, ex:
            print ex.message

    def on_events(self, reason):
        pass

if __name__ == '__main__':
    mytrade = MyTrade()
    mytrade.run()
