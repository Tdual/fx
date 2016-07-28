#!/usr/bin/python3
import oanda.oandatrade as ot

cr = ot.CandleRequest()
start_date = "2014-06-19T15:47:40.00Z"
end_date =  "2014-06-20T15:47:40.00Z"

r = cr.get_list(start_date, end_date)
print(r)
