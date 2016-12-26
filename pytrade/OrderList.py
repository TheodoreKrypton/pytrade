from Order import *
from Common import singleton


class SelectMethod:
    def __init__(self):
        pass

    by_pos = 0
    by_ticket = 1


@singleton
class OrderList:
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
    hist_orders = {}
    active_orders = {}
    active_orders_list = None
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
                   expired_time, open_reason=Order.Reason.open_at_mk, tp=None, sl=None):
        identifier = self.new_identifier
        self.active_orders[identifier] = \
            Order(op, identifier, open_time, open_price, lot, expired_time, open_reason, tp, sl)
        if op == Order.Operation.op_b:
            self.naked += lot
        elif op == Order.Operation.op_s:
            self.naked -= lot
        return identifier

    def order_close(self, identifier, close_time, close_price, close_reason):
        try:
            to_close = self.active_orders[identifier]
            if to_close.op == Order.Operation.op_b:
                self.naked -= to_close.lot
            elif to_close.op == Order.Operation.op_s:
                self.naked += to_close.lot
            self.active_orders[identifier].close(close_time, close_price, close_reason)
            self.hist_orders[identifier] = self.active_orders[identifier]
            del self.active_orders[identifier]

        except KeyError:
            raise OrderNotFoundException(identifier)

    def order_select(self, identifier, select_mode=SelectMethod.by_pos):
        if select_mode == self.SelectMethod.by_pos:
            if identifier >= len(self.active_orders):
                raise OrderNotFoundException(identifier)
            elif self.active_orders_list is None:
                self.active_orders_list = \
                    sorted(self.active_orders.keys(), lambda x, y:
                           self.active_orders[x].open_time <
                           self.active_orders[y].open_time)
            self.selected_order = self.active_orders[self.active_orders_list[identifier]]
        else:
            if identifier in self.active_orders:
                self.selected_order = self.active_orders[identifier]

            elif identifier in self.hist_orders:
                self.selected_order = self.hist_orders[identifier]
            else:
                raise OrderNotFoundException(identifier)
        return self.selected_order

    def order_modify(self, identifier=None, new_price=None, new_tp=None, new_sl=None, expired_time=None):
        if identifier is not None:
            self.order_select(identifier, self.SelectMethod.by_ticket)
        if self.selected_order.closed:
            raise SelectedOrderClosedException(self.selected_order.identifier)
        else:
            self.selected_order.modify(new_price, new_tp, new_sl, expired_time)

    def order_activate(self, price, identifier=None):
        if identifier is not None:
            self.order_select(identifier, self.SelectMethod.by_ticket)
        if self.selected_order.closed:
            raise MarketOrderActivatedException(self.selected_order.identifier)
        else:
            self.selected_order.activate(price)
            if self.selected_order.op == Order.Operation.op_b:
                self.naked += self.selected_order.lot
            else:
                self.naked -= self.selected_order.lot

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


if __name__ == '__main__':
    pass
