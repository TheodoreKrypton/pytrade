from Exception import *


class Order:
    """properties:
    [int]identifier: function OrderSend will return a unique order identifier for each
    order opened, which can be passed to function OrderSelect to select an order.

    [int]open_time: the open time as an integer offset of the benchmark time

    [double]open_price: the recorded order open price

    [double]lot: can be integer multiple of 0.01 in foreign exchange trading,
    and only integer in stock, future trading

    [double]tp: level of take profit of an order

    [double]sl: level of stop loss of an order

    [int]expired_time: time a limit or stop order is expired as an integer offset
    of the benchmark time

    [int]close_time: time an order is closed by function OrderClose as an integer
    offset of the benchmark time

    [bool]closed: True if the order is closed or cancelled and False if the order
    is still active

    [double]close_price: the recorded order close price
    """
    def __init__(self, op, identifier, open_time, open_price, lot, expired_time,
                 open_reason, tp, sl):
        self.closed = False
        self.op = op
        self.identifier = identifier
        self.open_time = open_time
        self.open_price = open_price
        self.lot = lot
        self.expired_time = expired_time
        self.open_reason = open_reason
        self.tp = tp
        self.sl = sl

    class Operation:
        def __init__(self):
            pass

        op_b = 0x00000000   # buy
        op_bs = 0x10001000  # buy stop
        op_bl = 0x10010000  # buy limit
        op_s = 0x00000001   # sell
        op_ss = 0x10010001  # sell stop
        op_sl = 0x10001001  # sell limit

        aux_is_b = 0x00000000      # is buy
        aux_is_mkt = 0x10000000    # is market order
        aux_is_bs_sl = 0x00001000  # is buy stop or sell limit
        aux_is_bl_ss = 0x00010000  # is buy limit or sell stop

        @classmethod
        def is_buy(cls, opr):
            return opr & cls.aux_is_b

        @classmethod
        def is_market(cls, opr):
            return opr & cls.aux_is_mkt

        @classmethod
        def is_bs_or_sl(cls, opr):
            return opr & cls.aux_is_bs_sl

        @classmethod
        def is_bl_or_ss(cls, opr):
            return opr & cls.aux_is_bl_ss

    @property
    def op(self):
        return self.op

    @op.setter
    def op(self, value):
        self.op = value

    @property
    def identifier(self):
        return self.identifier

    @identifier.setter
    def identifier(self, value):
        self.identifier = value

    class Reason:
        def __init__(self):
            pass

        open_at_mk = 0    # open at market
        open_at_bs = 1    # open at buy stop
        open_at_bl = 2    # open at buy limit
        open_at_ss = 3    # open at sell stop
        open_at_sl = 4    # open at sell limit
        close_at_mk = 5   # close at market
        close_at_tp = 6   # close at take profit
        close_at_sl = 7   # close at stop loss
        close_at_end = 8  # close at data ends

    @property
    def open_reason(self):
        return self.open_reason

    @open_reason.setter
    def open_reason(self, value):
        self.open_reason = value

    @property
    def open_time(self):
        return self.open_time

    @open_time.setter
    def open_time(self, value):
        self.open_time = value

    @property
    def open_price(self):
        return self.open_price

    @open_price.setter
    def open_price(self, value):
        self.open_price = value

    @property
    def lot(self):
        return self.lot

    @lot.setter
    def lot(self, value):
        self.lot = value

    @property
    def tp(self):
        return self.tp

    @tp.setter
    def tp(self, value):
        self.tp = value

    @property
    def sl(self):
        return self.sl

    @sl.setter
    def sl(self, value):
        self.sl = value

    @property
    def expired_time(self):
        return self.expired_time

    @expired_time.setter
    def expired_time(self, value):
        self.expired_time = value

    @property
    def close_time(self):
        return self.close_time

    @close_time.setter
    def close_time(self, value):
        self.close_time = value

    @property
    def closed(self):
        return self.closed

    @closed.setter
    def closed(self, value):
        self.closed = value

    @property
    def close_price(self):
        return self.close_price

    @close_price.setter
    def close_price(self, value):
        self.close_price = value

    @property
    def close_reason(self):
        return self.close_reason

    @close_reason.setter
    def close_reason(self, value):
        self.close_price = value

    def close(self, close_time, close_price, close_reason):
        self.closed = True
        self.close_time = close_time
        self.close_price = close_price
        self.close_reason = close_reason

    def modify(self, new_price, new_tp, new_sl, expired_time):
        if new_price is not None:
            if self.Operation.is_market(self.op):
                raise MarketOrderOpenPriceModifiedException(self.identifier)
            else:
                self.open_price = new_price
        if new_tp is not None:
            self.tp = new_tp
        if new_sl is not None:
            self.sl = new_sl
        if expired_time is not None:
            self.expired_time = expired_time

    def activate(self, price):
        if self.op == self.Operation.op_bl:
            self.op = self.Operation.op_b
            self.open_price = price
            self.open_reason = self.Reason.open_at_bl
        elif self.op == self.Operation.op_bs:
            self.op = self.Operation.op_b
            self.open_price = price
            self.open_reason = self.Reason.open_at_bs
        elif self.op == self.Operation.op_sl:
            self.op = self.Operation.op_s
            self.open_price = price
            self.open_reason = self.Reason.open_at_sl
        elif self.op == self.Operation.op_ss:
            self.op = self.Operation.op_s
            self.open_price = price
            self.open_reason = self.Reason.open_at_ss
        else:
            raise MarketOrderActivatedException(self.identifier)