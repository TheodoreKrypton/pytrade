from Common import config_info
from scipy import io
from Exception import *
import csv


class Bar:
    def __init__(self, o, h, l, c):
        self.bar_high = h
        self.bar_low = l
        self.bar_open = o
        self.bar_close = c


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
            oc = config_info["open"]
            hc = config_info["high"]
            lc = config_info["low"]
            cc = config_info["close"]

            row_begin = config_info["begin_at_row"]
            _row_begin = row_begin

            fp = open(fpath)
            f = csv.reader(fp)
            data = []
            for row in f:
                if _row_begin > 0:
                    _row_begin -= 1
                    continue
                else:
                    data.append(row)

            row_end = len(data) \
                if config_info["end_at_row"] is None else config_info["end_at_row"]
            self.total_rows = row_end - row_begin + 1

            for row in range(0, row_end):
                o = float(data[row][oc]) if oc is not None else None
                h = float(data[row][hc]) if hc is not None else None
                l = float(data[row][lc]) if lc is not None else None
                c = float(data[row][cc]) if cc is not None else None
                self.prices.append(Bar(o, h, l, c))

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
        if shift < 0:
            raise NoPriceException(shift)
        return self.prices[shift]
