#!/usr/bin/python3
import numpy
import pandas as pd
import json
import datetime
import time

from util import dfutil
import oanda.oandatrade as ot


def get_trade_data(back_days=20, candle_interval="H1", bb_period=50):
    NY_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    back_days = datetime.timedelta(days=back_days)
    start_date = (NY_time - back_days).isoformat("T") + "Z"
    cr = ot.CandleRequest()
    res = cr.get_list(start_date, end_date=None, interval=candle_interval)
    bb = dfutil.get_bb(res["closeBid"], bb_period,)
    return bb

def judge(candle_list, outer_trade):

    if not "tradeOpened" in outer_trade:
        if get_out_condition(candle_list)["upper"]:
            print("------buy------")
            oreq = ot.OrderRequest()
            res = oreq.add_orders(side="buy", unit=100000)
            if not res:
                res = {}
            return res
        elif get_out_condition(candle_list)["lower"]:
            print("------sell------")
            oreq = ot.OrderRequest()
            res = oreq.add_orders(side="sell", unit=100000)
            if not res:
                res = {}
            return res
        else:
            return {}
    else:
        if is_limit_opposite_bb(candle_list, outer_trade):
            print("-------trade----------")
            treq = ot.TradeRequest()
            res = treq.close_detail(outer_trade["tradeOpened"]["id"])
            print(res)
            print("-----------------")
            return {}
        else:
            return outer_trade


def get_out_condition(candle_list):
    upper = candle_list[-1]["+2sigma"] < candle_list[-1]["closeBid"] \
        and candle_list[-2]["+2sigma"] < candle_list[-2]["closeBid"]

    lower = candle_list[-1]["-2sigma"] > candle_list[-1]["closeBid"] \
        and candle_list[-2]["-2sigma"] > candle_list[-2]["closeBid"]
    res = {
        "upper": upper,
        "lower": lower
        }
    return res

def is_limit_opposite_bb(list_data, outer_trade):
    if not "tradeOpened" in outer_trade:
        return False
    side = outer_trade["tradeOpened"]["side"]
    if side == "buy":
        opposite_bb = "-2sigma"
        res = list_data[-1][opposite_bb] - list_data[-2][opposite_bb] > 0
    else:
        opposite_bb = "+2sigma"
        res = list_data[-1][opposite_bb] - list_data[-2][opposite_bb] < 0
    return res


def get_in_condition(list_data, outer_trade):
    if not "tradeOpened" in outer_trade:
        return False
    upper = outer_trade["tradeOpened"]["side"] == "buy"
    lower = outer_trade["tradeOpened"]["side"] == "sell"
    upper_in_bound = upper and \
        list_data[-1]["closeBid"] < list_data[-2]["closeBid"] and \
        list_data[-2]["closeBid"] < list_data[-3]["closeBid"]
    lower_in_bound = lower and \
        list_data[-1]["closeBid"] > list_data[-2]["closeBid"] and \
        list_data[-2]["closeBid"] > list_data[-3]["closeBid"]

    print("upper: " + str(upper))
    print("lower: " + str(lower))
    print("upper in bound: " + str(upper_in_bound))
    print("lower in bound: " + str(lower_in_bound))
    return upper_in_bound or lower_in_bound



def main(request_interval):
    outer_trade = {}
    while True:
        r = get_trade_data()
        data = json.loads(r.dropna().tail().to_json(orient="records"))
        print(data)
        #### test code
        #with open("order_test.json", "r") as f:
        #    data = json.loads(f.read())
        ####
        outer_trade = judge(data, outer_trade)
        print("---outer_trade---")
        print(outer_trade)
        time.sleep(request_interval)

if __name__ == "__main__":
    main(30*60)
