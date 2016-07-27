#!/usr/bin/python3

import oandatrade as ot

oreq = ot.OrderRequest()
treq = ot.TradeRequest()

r = treq.get_list()
print(r)

r = oreq.add_orders(unit=100000, side="sell")
print(r)

r = treq.get_list()
print(r)

import os
print (os.path.dirname(__file__))
