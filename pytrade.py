#!/usr/bin/env python

"""Py Trade: a python library for history data back testing
================================================================
    Author: Chen Yonghua
    Date:   10/6/2016
"""

from __future__ import print_function, unicode_literals, division, absolute_import
import json
import csv
from scipy import io
from abc import ABCMeta, abstractmethod


config_info = json.load(open("config.json"))


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


class TradingEnvException(BaseException):
    def __init__(self):
        pass


@singleton
class OrderNotFoundException(TradingEnvException):
    def __init__(self, identifier):
        self.message = "Order #" + str(identifier) + ": Not Found."


@singleton
class SelectedOrderClosedException(TradingEnvException):
    def __init__(self, identifier):
        self.message = "Order #" + str(identifier) + ": Order Is Closed."


@singleton
class NoEnoughMoneyException(TradingEnvException):
    def __init__(self, money):
        self.message = "Balance=" + str(money) + ": No Enough Money."


@singleton
class InvalidTpOrSlException(TradingEnvException):
    def __init__(self, tp, sl):
        self.message = " Stop Loss(" + str(sl) + "), " + \
                       " Take Profit(" + str(tp) + ")" + \
                       " Invalid."

@singleton
class MarketOrderOpenPriceModifiedException(TradingEnvException):
    def __init__(self, identifier):
        self.message = "Order #" + str(identifier) + \
                       ": Open Price Of Market Order Modified."


@singleton
class PriceFormFormatException(TradingEnvException):
    def __init__(self, file_name):
        self.message = "Format Of File: " + file_name + " Is Illegal."


@singleton
class MarketOrderActivatedException(TradingEnvException):
    def __init__(self, identifier):
        self.message = "Order #" + str(identifier) + \
                       ": Market Order Activated."


@singleton
class InvalidOpenPriceException(TradingEnvException):
    def __init__(self, open_price, market_price, op):
        self.message = "Operation: " + str(op) + ", " + \
                       "Market Price: " + str(market_price) + ", " + \
                       "Open Price: " + str(open_price) + " Invalid."


class Ticket:
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


@singleton
class Tickets:
    """methods:
    order_send: to create a new order
    order_close: to close a position
    order_select: to select an order to call the function order_close or order_info
    order_modify: to modify the tp, sl, execute price, expired time of an order.
            Modifications of execute price and expired time are only for pending orders.
    order_info: to get the information of an order,
                params:
                    Info.identifier
                    Info.open_price
                    Info.open_time
                    Info.operation
                    Info.lot
                    Info.expired_time
                    Info.open_reason
                    Info.close_time
                    Info.closed
                    Info.tp
                    Info.sl
                    Info.close_reason
    There are 2 ways to select an order and perform operations on it.
    1. Parse the unique order identifier to the function (order_info, order_modify and order_close).
    2. Use the select_by_pos mode in the function order_select and directly use the
    function (order_info, order_modify and order_close) with a [None] identifier parameter.
    """
    hist_tickets = {}
    active_tickets = {}
    active_tickets_list = None
    selected_order = None

    identifier = 0

    def __init__(self):
        self.naked = 0
        pass

    @property
    def new_identifier(self):
        self.identifier += 1
        return self.identifier

    @property
    def naked(self):
        return self.naked

    @naked.setter
    def naked(self, value):
        self.naked = value

    def order_send(self, op, open_time, open_price, lot,
                   expired_time, open_reason=Ticket.Reason.open_at_mk, tp=None, sl=None):
        identifier = self.new_identifier
        self.active_tickets[identifier] = \
            Ticket(op, identifier, open_time, open_price, lot, expired_time, open_reason, tp, sl)
        if op == Ticket.Operation.op_b:
            self.naked += lot
        elif op == Ticket.Operation.op_s:
            self.naked -= lot
        return identifier

    def order_close(self, identifier, close_time, close_price, close_reason):
        try:
            to_close = self.active_tickets[identifier]
            if to_close.op == Ticket.Operation.op_b:
                self.naked -= to_close.lot
            elif to_close.op == Ticket.Operation.op_s:
                self.naked += to_close.lot
            self.active_tickets[identifier].close(close_time, close_price, close_reason)
            self.hist_tickets[identifier] = self.active_tickets[identifier]
            del self.active_tickets[identifier]

        except KeyError:
            raise OrderNotFoundException(identifier)

    class Select:
        def __init__(self):
            pass
        select_by_pos = 0
        select_by_ticket = 1

    def order_select(self, identifier, select_mode=Select.select_by_pos):
        if select_mode == self.Select.select_by_pos:
            if identifier >= len(self.active_tickets):
                raise OrderNotFoundException(identifier)
            elif self.active_tickets_list is None:
                self.active_tickets_list = \
                    sorted(self.active_tickets.keys(), lambda x, y:
                           self.active_tickets[x].open_time <
                           self.active_tickets[y].open_time)
            self.selected_order = self.active_tickets[self.active_tickets_list[identifier]]
        else:
            if identifier in self.active_tickets:
                self.selected_order = self.active_tickets[identifier]

            elif identifier in self.hist_tickets:
                self.selected_order = self.hist_tickets[identifier]
            else:
                raise OrderNotFoundException(identifier)
        return self.selected_order

    def order_modify(self, identifier=None, new_price=None, new_tp=None, new_sl=None, expired_time=None):
        if identifier is not None:
            self.order_select(identifier, self.Select.select_by_ticket)
        if self.selected_order.closed:
            raise SelectedOrderClosedException(self.selected_order.identifier)
        else:
            self.selected_order.modify(new_price, new_tp, new_sl, expired_time)

    def order_activate(self, price, identifier=None):
        if identifier is not None:
            self.order_select(identifier, self.Select.select_by_ticket)
        if self.selected_order.closed:
            raise MarketOrderActivatedException(self.selected_order.identifier)
        else:
            self.selected_order.activate(price)
            if self.selected_order.op == Ticket.Operation.op_b:
                self.naked += self.selected_order.lot
            else:
                self.naked -= self.selected_order.lot

    class Info:
        def __init__(self):
            pass
        identifier = 0
        open_price = 1
        open_time = 2
        operation = 3
        lot = 4
        expired_time = 5
        open_reason = 6
        close_time = 7
        closed = 8
        tp = 9
        sl = 10
        close_reason = 11

    def order_info(self, info):
        if info == self.Info.identifier:
            return self.selected_order.identifier
        if info == self.Info.open_price:
            return self.selected_order.open_price
        if info == self.Info.open_time:
            return self.selected_order.open_time
        if info == self.Info.operation:
            return self.selected_order.op
        if info == self.Info.lot:
            return self.selected_order.lot
        if info == self.Info.expired_time:
            return self.selected_order.expired_time
        if info == self.Info.open_reason:
            return self.selected_order.open_reason
        if info == self.Info.close_time:
            return self.selected_order.close_time
        if info == self.Info.closed:
            return self.selected_order.closed
        if info == self.Info.tp:
            return self.selected_order.tp
        if info == self.Info.sl:
            return self.selected_order.sl
        if info == self.Info.close_reason:
            return self.selected_order.close_reason


class Bar:
    def __init__(self, o, h, l, c):
        self.bar_high = h
        self.bar_low = l
        self.bar_open = o
        self.bar_close = c
        pass


class PriceProvider:
    def __init__(self):
        self.time = 0
        self.total_rows = 0
        fpath = config_info["data_source"]
        tokens = fpath.split('.')
        file_fmt = tokens[-1]
        self.prices = [Bar(None, None, None, None)]
        del self.prices[0]

        if file_fmt == "csv":
            fp = open(fpath)
            _file = csv.reader(fp)
            # TODO: csv file reading
            pass

        elif file_fmt == "mat":
            mat = io.loadmat(fpath)
            data = mat[config_info["matrix_name"]]
            row_begin = config_info["begin_at_row"]
            row_end = len(data) \
                if config_info["end_at_row"] is None else config_info["end_at_row"]
            self.total_rows = row_end - row_begin + 1

            oc = config_info["open"]
            hc = config_info["high"]
            lc = config_info["low"]
            cc = config_info["close"]

            for row in range(row_begin, row_end):
                o = data[row][oc] if oc is not None else None
                h = data[row][hc] if hc is not None else None
                l = data[row][lc] if lc is not None else None
                c = data[row][cc] if cc is not None else None
                self.prices.append(Bar(o, h, l, c))

        else:
            raise PriceFormFormatException(fpath)

    def get(self, shift):
        return self.prices[self.total_rows-shift]


class TradingEnvironment:
    """ Virtual Trading Environment

    Instances of this class are forbidden from being constructed.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.Time = 1
        self.ticket_pool = Tickets()
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
        return self.ticket_pool.price.get(self.Time - shift).bar_open

    def High(self, shift=0):
        return self.ticket_pool.price.get(self.Time - shift).bar_high

    def Low(self, shift=0):
        return self.ticket_pool.price.get(self.Time - shift).bar_low

    def Close(self, shift=0):
        return self.ticket_pool.price.get(self.Time - shift).bar_close

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

    def OrderSend(self, op, open_price, lot, tp=None, sl=None, expired_time=None):
        if Ticket.Operation.is_market(op):
            if op == Ticket.Operation.op_b:
                if (tp is not None and tp < self.MarketPrice) or \
                        (sl is not None and self.MarketPrice - sl < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
            else:
                if (tp is not None and tp > self.MarketPrice) or \
                        (sl is not None and sl - self.MarketPrice < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
            identifier = self.ticket_pool.order_send(
                op,
                self.Time,
                self.MarketPrice,
                lot,
                expired_time,
                Ticket.Reason.open_at_mk,
                tp,
                sl
            )
            return identifier

        else:
            if op == Ticket.Operation.op_bl:
                if (tp is not None and tp < open_price) or \
                        (sl is not None and open_price - sl < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
                elif open_price > self.MarketPrice:
                    raise InvalidOpenPriceException(open_price, self.MarketPrice, op)
            elif op == Ticket.Operation.op_bs:
                if (tp is not None and tp < open_price) or \
                        (sl is not None and open_price - sl < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
                elif open_price < self.MarketPrice:
                    raise InvalidOpenPriceException(open_price, self.MarketPrice, op)
            elif op == Ticket.Operation.op_sl:
                if (tp is not None and tp > open_price) or \
                        (sl is not None and sl - open_price < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
                elif open_price < self.MarketPrice:
                    raise InvalidOpenPriceException(open_price, self.MarketPrice, op)
            elif op == Ticket.Operation.op_ss:
                if (tp is not None and tp > open_price)\
                        or (sl is not None and sl - open_price < self.point * self.nearest_sl):
                    raise InvalidTpOrSlException(tp, sl)
                elif open_price > self.MarketPrice:
                    raise InvalidOpenPriceException(open_price, self.MarketPrice, op)
            identifier = self.ticket_pool.order_send(
                op,
                self.Time,
                open_price,
                lot,
                expired_time,
                Ticket.Reason.open_at_mk,
                tp,
                sl
            )
            return identifier

    def OrderClose(self, identifier):
        self.ticket_pool.order_close(identifier, self.Time, self.MarketPrice, Ticket.Reason.close_at_mk)

    def OrderSelect(self, identifier, select_mode=Tickets.Select.select_by_pos):
        self.ticket_pool.order_select(identifier, select_mode)

    def OrderInfo(self, info):
        return self.ticket_pool.order_info(info)

    def OrderModify(self, identifier=None, new_price=None, new_tp=None, new_sl=None, expired_time=None):
        self.OrderSelect(identifier, Tickets.Select.select_by_ticket)
        op = self.ticket_pool.selected_order.op
        if op in [Ticket.Operation.op_b, Ticket.Operation.op_bl, Ticket.Operation.op_bs]:
            if new_tp is not None and new_tp < self.MarketPrice:
                raise InvalidTpOrSlException(new_tp, new_sl)
            elif new_sl is not None and self.MarketPrice - new_sl < self.point * self.nearest_sl:
                raise InvalidTpOrSlException(new_tp, new_sl)

        elif op in [Ticket.Operation.op_s, Ticket.Operation.op_sl, Ticket.Operation.op_ss]:
            if new_tp is not None and new_tp > self.MarketPrice:
                raise InvalidTpOrSlException(new_tp, new_sl)
            elif new_sl is not None and new_sl - self.MarketPrice < self.point * self.nearest_sl:
                raise InvalidTpOrSlException(new_tp, new_sl)

        if Ticket.Operation.is_bl_or_ss(op):
            if self.ticket_pool.selected_order.open_price > self.MarketPrice:
                raise InvalidOpenPriceException(new_price, self.MarketPrice, op)

        elif Ticket.Operation.is_bs_or_sl(op):
            if self.ticket_pool.selected_order.open_price < self.MarketPrice:
                raise InvalidOpenPriceException(new_price, self.MarketPrice, op)

        self.ticket_pool.order_modify(identifier, new_price, new_tp, new_sl, expired_time)

    def run(self):
        new_price = self.price.prices[0].bar_close
        self.MarketPrice = new_price
        self.on_init()
        while self.Time < self.price.total_rows-1:
            prev_price = new_price
            new_price = self.price.prices[self.Time].bar_close

            # calculate net
            self.balance.append(
                self.balance[-1] + (new_price - prev_price)*self.ticket_pool.naked
            )
            # stop loss, take profit, buy limit, buy stop, sell limit, sell stop
            if new_price > prev_price:
                # when price goes up
                for ticket in self.ticket_pool.active_tickets.values():
                    if Ticket.Operation.is_bs_or_sl(ticket.op):
                        if ticket.open_price < new_price:
                            # buy stop or sell limit activated
                            self.ticket_pool.order_activate(ticket.identifier, new_price)
                    elif ticket.op == Ticket.Operation.op_b and ticket.tp is not None and ticket.tp < new_price:
                        self.ticket_pool.order_close(ticket.identifier, self.Time, new_price, Ticket.Reason.close_at_tp)
                    elif ticket.op == Ticket.Operation.op_s and ticket.sl is not None and ticket.sl < new_price:
                        self.ticket_pool.order_close(ticket.identifier, self.Time, new_price, Ticket.Reason.close_at_sl)
            else:
                # when price goes down
                for ticket in self.ticket_pool.active_tickets.values():
                    if Ticket.Operation.is_bl_or_ss(ticket.op):
                        if ticket.open_price > new_price:
                            # buy limit or sell stop activated
                            self.ticket_pool.order_activate(ticket.identifier, new_price)
                    elif ticket.op == Ticket.Operation.op_b and ticket.sl is not None and ticket.sl > new_price:
                        self.ticket_pool.order_close(ticket.identifier, self.Time, new_price, Ticket.Reason.close_at_sl)
                    elif ticket.op == Ticket.Operation.op_s and ticket.tp is not None and ticket.tp > new_price:
                        self.ticket_pool.order_close(ticket.identifier, self.Time, new_price, Ticket.Reason.close_at_tp)
            # customized on bar function
            self.on_bar()
            self.Time += 1
        self.on_deinit()
