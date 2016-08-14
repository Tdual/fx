#!/usr/bin/python3
import numpy
import pandas as pd
import json
import datetime
import time

from util import dfutil
import oanda.oandatrade as ot


def get_trade_data(back_days=20, candle_interval="H1", bb_period=50):
    """
    getting data for judging trade

    :param int back_days: days included in calculating Bollinger bind
    :param str candle_interval: oanda api format time
    :param int bb_period: Bolinger band's period

    :return: bolinger bind param(+2sigma,sma,-2sigma,closeBid)
    :rtype: DataFrame
    """

    NY_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    back_days = datetime.timedelta(days=back_days)
    start_date = (NY_time - back_days).isoformat("T") + "Z"
    cr = ot.CandleRequest()
    res = cr.get_list(start_date, end_date=None, interval=candle_interval)
    bb = dfutil.get_bb(res["closeBid"], bb_period,)
    return bb

def judge(candle_list, outer_trade, connect_oanda=True):
    """
    judging trade (buy or sell or close)

    :param list candle_list: list of candles
    :param dict outer_trade: reponse of ordering ticket
    :return: new outer trade or empty dict
    :rtype: dict
    """

    if not "tradeOpened" in outer_trade:
        if get_out_condition(candle_list)["upper"]:
            print("------buy------")
            if connect_oanda:
                oreq = ot.OrderRequest()
                res = oreq.add_orders(side="buy", unit=100000)
            else:
                res = _create_dummy_open_res(candle_list, "buy")
            if not res:
                res = {}
            return res
        elif get_out_condition(candle_list)["lower"]:
            print("------sell------")
            if connect_oanda:
                oreq = ot.OrderRequest()
                res = oreq.add_orders(side="sell", unit=100000)
            else:
                res = _create_dummy_open_res(candle_list, "sell")
            if not res:
                res = {}
            return res
        else:
            return {}
    else:
        if is_limit_opposite_bb(candle_list, outer_trade):
            print("-------trade----------")
            if connect_oanda:
                treq = ot.TradeRequest()
                res = treq.close_detail(outer_trade["tradeOpened"]["id"])
            else:
                res = _create_dummy_close_res(candle_list, outer_trade)
            print(res)
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

def _create_dummy_open_res(candle_list, side):
    candle = candle_list[-1]
    dummy = {
      "instrument" : "USD_JPY",
      "time" : candle["time"],
      "price" : candle["closeBid"],
      "tradeOpened" : {
        "id" : 175517237,
        "units" : 10000,
        "side" : side,
        "takeProfit" : 0,
        "stopLoss" : 0,
        "trailingStop" : 0
      },
      "tradesClosed" : [],
      "tradeReduced" : {}
    }
    return dummy

def _create_dummy_close_res(candle_list, outer_trade):
    candle = candle_list[-1]
    NY_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    now = NY_time.isoformat("T") + "Z"
    profit = outer_trade["tradeOpened"]["units"] * (candle["closeBid"] - outer_trade["price"])
    dummy = {
      "id" : outer_trade["tradeOpened"]["id"],
      "price" : candle["closeBid"],
      "instrument" : outer_trade["instrument"],
      "profit" :  profit,
      "side" :  outer_trade["tradeOpened"],
      "time" : now
    }
    return dummy


def pd_to_dict(bb_df):
    data_list = []
    for i in range(0, len(bb_df)):
        new_data = {
            "+2sigma": bb_df.ix[i]["+2sigma"],
            "-2sigma": bb_df.ix[i]["-2sigma"],
            "SMA": bb_df.ix[i]["SMA"],
            "closeBid": bb_df.ix[i]["closeBid"],
            "time": str(bb_df.ix[i].name)
        }
        data_list.append(new_data)
    return data_list

def main(request_interval):
    outer_trade = {}
    while True:
        r = get_trade_data()
        latest = r.dropna().tail()
        data_list = pd_to_dict(latest)
        outer_trade = judge(data_list, outer_trade)
        print("---outer_trade---:{}".format(outer_trade))
        time.sleep(request_interval)

if __name__ == "__main__":
    main(30*60)
