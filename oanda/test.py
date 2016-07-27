#!/usr/bin/python3

import oandatrade as ot

oreq = ot.OrderRequest()
treq = ot.TradeRequest()


print ("----add orders--------")
r = oreq.add_orders(unit=100000, side="sell")
print(r)

print ("---get trades list--------")
r = treq.get_list()
print(r)

trade_id = r["trades"][0]["id"]
price = r["trades"][0]["price"]

print ("----get detail--------")
r = treq.get_detail(trade_id)
print(r)

print ("----modify detail--------")
params = {
    "stopLoss": price + 1.0
}
r = treq.modify_detail(trade_id, params=params)
print(r)
r = treq.get_detail(trade_id)
print(r)

print ("----close detail--------")
r = treq.close_detail(trade_id)
print(r)
