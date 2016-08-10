#!/usr/bin/python3
import unittest
import trade

class TestTrade(unittest.TestCase):
    def setUp(self):
        self.candle_list_1 = [
            {
                "SMA": 0,
                "+2sigma": 2,
                "time": 0,
                "closeBid": 3,
                "-2sigma": 0
            },
            {
                "SMA": 0,
                "+2sigma": 2,
                "time": 0,
                "closeBid": 3,
                "-2sigma": 1
            }
        ]
        self.candle_list_2 = [
            {
                "SMA": 0,
                "+2sigma": 1,
                "time": 0,
                "closeBid": 0,
                "-2sigma": 1
            },
            {
                "SMA": 0,
                "+2sigma": 0,
                "time": 0,
                "closeBid": 0,
                "-2sigma": 1
            }
        ]
        self.outer_trade_1 = {
            "instrument" : "USD_JPY",
            "time" : "2013-12-06T20:36:06Z",
            "price" : 1.37041,
            "tradeOpened" : {
                "id" : 175517237,
                "units" : 2,
                "side" : "buy",
                "takeProfit" : 0,
                "stopLoss" : 0,
                "trailingStop" : 0
            },
            "tradesClosed" : [],
            "tradeReduced" : {}
        }
        self.outer_trade_2 = {
            "instrument" : "USD_JPY",
            "time" : "2013-12-06T20:36:06Z",
            "price" : 1.37041,
            "tradeOpened" : {
                "id" : 175517237,
                "units" : 2,
                "side" : "sell",
                "takeProfit" : 0,
                "stopLoss" : 0,
                "trailingStop" : 0
            },
            "tradesClosed" : [],
            "tradeReduced" : {}
        }

    def test_get_out_condition(self):
        res_1 = trade.get_out_condition(self.candle_list_1)
        res_2 = trade.get_out_condition(self.candle_list_2)
        self.assertTrue(res_1["upper"])
        self.assertFalse(res_1["lower"])
        self.assertTrue(res_2["lower"])
        self.assertFalse(res_2["upper"])


    def test_is_limit_opposite_bb(self):
        ilob = trade.is_limit_opposite_bb
        res_1_1 = ilob(self.candle_list_1, self.outer_trade_1)
        res_1_2 = ilob(self.candle_list_1, self.outer_trade_2)
        res_2_1 = ilob(self.candle_list_2, self.outer_trade_1)
        res_2_2 = ilob(self.candle_list_2, self.outer_trade_2)
        self.assertTrue(res_1_1)
        self.assertFalse(res_1_2)
        self.assertFalse(res_2_1)
        self.assertTrue(res_2_2)



if __name__ == '__main__':
    unittest.main(verbosity=2)
