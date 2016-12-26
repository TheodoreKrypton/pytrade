from Exception import *
from abc import ABCMeta, abstractmethod
from OrderList import OrderList, SelectMethod
from Query import PriceProvider
from Common import config_info
from Order import Order
from matplotlib import pyplot


class TradingEnvironment:
    """ Virtual Trading Environment

    Instances of this class are forbidden from being constructed.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.Time = 0
        self.order_pool = OrderList()
        self.price = PriceProvider()
        self.MarketPrice = 0
        self.initial_balance = config_info["initial_balance"]
        self.balance = [self.initial_balance]
        self.leverage = config_info["leverage"]
        self.point = config_info["point"]
        self.nearest_sl = config_info["nearest_sl"]

    def KLine(self, shift=0):
        return self.price.get(shift)

    def Open(self, shift=0):
        return self.price.get(self.Time - shift).bar_open

    def High(self, shift=0):
        return self.price.get(self.Time - shift).bar_high

    def Low(self, shift=0):
        return self.price.get(self.Time - shift).bar_low

    def Close(self, shift=0):
        return self.price.get(self.Time - shift).bar_close

    @abstractmethod
    def on_bar(self):
        pass

    @abstractmethod
    def on_init(self):
        pass

    @abstractmethod
    def on_deinit(self):
        pass

    @abstractmethod
    def on_events(self, reason):
        pass

    def __next_day(self):
        self.Time += 1
        self.price.time += 1

    def OrderSend(self, op, open_price, lot, tp=None, sl=None, expired_time=None):
        if Order.Operation.is_market(op):
            if op == Order.Operation.op_b:
                if (tp is not None and tp < self.MarketPrice) or \
                        (sl is not None and self.MarketPrice - sl < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
            else:
                if (tp is not None and tp > self.MarketPrice) or \
                        (sl is not None and sl - self.MarketPrice < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
            identifier = self.order_pool.order_send(
                op,
                self.Time,
                self.MarketPrice,
                lot,
                expired_time,
                Order.Reason.open_at_mk,
                tp,
                sl
            )
            return identifier

        else:
            if op == Order.Operation.op_bl:
                if (tp is not None and tp < open_price) or \
                        (sl is not None and open_price - sl < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
                elif open_price > self.MarketPrice:
                    raise InvalidOpenPriceException(open_price, self.MarketPrice, op)
            elif op == Order.Operation.op_bs:
                if (tp is not None and tp < open_price) or \
                        (sl is not None and open_price - sl < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
                elif open_price < self.MarketPrice:
                    raise InvalidOpenPriceException(open_price, self.MarketPrice, op)
            elif op == Order.Operation.op_sl:
                if (tp is not None and tp > open_price) or \
                        (sl is not None and sl - open_price < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
                elif open_price < self.MarketPrice:
                    raise InvalidOpenPriceException(open_price, self.MarketPrice, op)
            elif op == Order.Operation.op_ss:
                if (tp is not None and tp > open_price)\
                        or (sl is not None and sl - open_price < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
                elif open_price > self.MarketPrice:
                    raise InvalidOpenPriceException(open_price, self.MarketPrice, op)
            identifier = self.order_pool.order_send(
                op,
                self.Time,
                open_price,
                lot,
                expired_time,
                Order.Reason.open_at_mk,
                tp,
                sl
            )
            return identifier

    def OrderClose(self, identifier):
        self.order_pool.order_close(identifier, self.Time, self.MarketPrice, Order.Reason.close_at_mk)

    def OrderSelect(self, identifier, select_mode=SelectMethod.by_pos):
        self.order_pool.order_select(identifier, select_mode)

    def OrdersTotal(self):
        return len(self.order_pool.active_orders.keys())

    def OrderInfo(self, info):
        return self.order_pool.order_info(info)

    def OrderModify(self, identifier=None, new_price=None, new_tp=None, new_sl=None, expired_time=None):
        self.OrderSelect(identifier, SelectMethod.by_ticket)
        op = self.order_pool.selected_order.op
        if op in [Order.Operation.op_b, Order.Operation.op_bl, Order.Operation.op_bs]:
            if new_tp is not None and new_tp < self.MarketPrice:
                raise InvalidTpOrSlException(new_tp, new_sl)
            elif new_sl is not None and self.MarketPrice - new_sl < self.point * self.nearest_sl:
                raise InvalidTpOrSlException(new_tp, new_sl)

        elif op in [Order.Operation.op_s, Order.Operation.op_sl, Order.Operation.op_ss]:
            if new_tp is not None and new_tp > self.MarketPrice:
                raise InvalidTpOrSlException(new_tp, new_sl)
            elif new_sl is not None and new_sl - self.MarketPrice < self.point * self.nearest_sl:
                raise InvalidTpOrSlException(new_tp, new_sl)

        if Order.Operation.is_bl_or_ss(op):
            if self.order_pool.selected_order.open_price > self.MarketPrice:
                raise InvalidOpenPriceException(new_price, self.MarketPrice, op)

        elif Order.Operation.is_bs_or_sl(op):
            if self.order_pool.selected_order.open_price < self.MarketPrice:
                raise InvalidOpenPriceException(new_price, self.MarketPrice, op)

        self.order_pool.order_modify(identifier, new_price, new_tp, new_sl, expired_time)

    def run(self):
        new_price = self.price.prices[0].bar_close
        self.MarketPrice = new_price
        self.on_init()
        while self.Time < self.price.total_rows-1:
            prev_price = new_price
            new_price = self.price.prices[self.Time].bar_close

            # calculate net
            self.balance.append(
                self.balance[-1] + (new_price - prev_price)*self.order_pool.naked
            )
            # stop loss, take profit, buy limit, buy stop, sell limit, sell stop
            if new_price > prev_price:
                # when price goes up
                for order in self.order_pool.active_orders.values():
                    if Order.Operation.is_bs_or_sl(order.op):
                        if order.open_price < new_price:
                            # buy stop or sell limit activated
                            self.order_pool.order_activate(order.identifier, new_price)
                    elif order.op == Order.Operation.op_b and order.tp is not None and order.tp < new_price:
                        self.order_pool.order_close(order.identifier, self.Time, new_price, Order.Reason.close_at_tp)
                    elif order.op == Order.Operation.op_s and order.sl is not None and order.sl < new_price:
                        self.order_pool.order_close(order.identifier, self.Time, new_price, Order.Reason.close_at_sl)
            else:
                # when price goes down
                for order in self.order_pool.active_orders.values():
                    if Order.Operation.is_bl_or_ss(order.op):
                        if order.open_price > new_price:
                            # buy limit or sell stop activated
                            self.order_pool.order_activate(order.identifier, new_price)
                    elif order.op == Order.Operation.op_b and order.sl is not None and order.sl > new_price:
                        self.order_pool.order_close(order.identifier, self.Time, new_price, Order.Reason.close_at_sl)
                    elif order.op == Order.Operation.op_s and order.tp is not None and order.tp > new_price:
                        self.order_pool.order_close(order.identifier, self.Time, new_price, Order.Reason.close_at_tp)
            # customized on bar function
            self.on_bar()
            self.__next_day()
        self.on_deinit()
        pyplot.plot(self.balance)
        pyplot.show()
