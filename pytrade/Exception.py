class TradingEnvException(BaseException):
    def __init__(self):
        pass


class OrderNotFoundException(TradingEnvException):
    def __init__(self, identifier):
        self.message = "Order #" + str(identifier) + ": Not Found."


class SelectedOrderClosedException(TradingEnvException):
    def __init__(self, identifier):
        self.message = "Order #" + str(identifier) + ": Order Is Closed."


class NoEnoughMoneyException(TradingEnvException):
    def __init__(self, money):
        self.message = "Balance=" + str(money) + ": No Enough Money."


class InvalidTpOrSlException(TradingEnvException):
    def __init__(self, tp, sl):
        self.message = " Stop Loss(" + str(sl) + "), " + \
                       " Take Profit(" + str(tp) + ")" + \
                       " Invalid."


class MarketOrderOpenPriceModifiedException(TradingEnvException):
    def __init__(self, identifier):
        self.message = "Order #" + str(identifier) + \
                       ": Open Price Of Market Order Modified."


class PriceFormFormatException(TradingEnvException):
    def __init__(self, file_name):
        self.message = "Format Of File: " + file_name + " Is Illegal."


class MarketOrderActivatedException(TradingEnvException):
    def __init__(self, identifier):
        self.message = "Order #" + str(identifier) + \
                       ": Market Order Activated."


class InvalidOpenPriceException(TradingEnvException):
    def __init__(self, open_price, market_price, op):
        self.message = "Operation: " + str(op) + ", " + \
                       "Market Price: " + str(market_price) + ", " + \
                       "Open Price: " + str(open_price) + " Invalid."


class NoPriceException(TradingEnvException):
    def __init__(self, time):
        self.message = "No Price On Time: " + str(time)
