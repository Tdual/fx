import numpy
import pandas as pd
import json
import datetime
import time

from util import dfutil
import oanda.oandatrade as ot


def get_trade_data(back_days=10, candle_interval="M15", bb_period=50):
    NY_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    back_days = datetime.timedelta(days=back_days)
    start_date = (NY_time - back_days).isoformat("T") + "Z"
    cr = ot.CandleRequest()
    res = cr.get_list(start_date, end_date=None, interval=candle_interval)
    bb = dfutil.get_bb(res["closeBid"], bb_period,)
    return bb

def judge(data, outer_trade):

    latest_condition = get_out_condition(data[-1])
    pre_latest_conditon = get_out_condition(data[-2])

    if not "tradeOpened" in outer_trade:
        if latest_condition["upper"] and pre_latest_conditon["upper"]:
            print("------buy------")
            oreq = ot.OrderRequest()
            res = oreq.add_orders(side="buy", unit=100000)
            if not res:
                res = {}
            return res
        elif latest_condition["lower"] and pre_latest_conditon["lower"]:
            print("------sell------")
            oreq = ot.OrderRequest()
            res = oreq.add_orders(side="sell", unit=100000)
            if not res:
                res = {}
            return res
        else:
            return {}
    else:
        if get_in_condition(data, outer_trade):
            print("-------trade----------")
            treq = ot.TradeRequest()
            res = treq.close_detail(outer_trade["tradeOpened"]["id"])
            print(res)
            print("-----------------")
            return {}
        else:
            return outer_trade


def get_out_condition(data):
    upper = data["+2sigma"] < data["closeBid"]
    lower = data["-2sigma"] > data["closeBid"]
    res = {"upper":upper,"lower":lower}
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
    main(10*60)
