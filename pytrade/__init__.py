from Common import singleton
from Trade import *
from Order import *
from Exception import *
import OrderList


class Operation:
    def __init__(self):
        pass

    op_b = 0x00000000  # buy
    op_bs = 0x10001000  # buy stop
    op_bl = 0x10010000  # buy limit
    op_s = 0x00000001  # sell
    op_ss = 0x10010001  # sell stop
    op_sl = 0x10001001  # sell limit

Info = OrderList.Info
