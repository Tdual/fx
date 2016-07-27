import requests
import yaml


class BaseRequest:
    def __init__(self):
        with open("account_info.yaml") as f:
            data = yaml.load(f)
        self.access_token = data["access_token"]
        self.account_id = str(data["account_id"])
        self.instruments = "USD_JPY"

        self.account_api = "/v1/accounts/"

        #stream_domain = 'stream-fxpractice.oanda.com'
        api_domain = 'api-fxpractice.oanda.com'
        scheme = "https"
        self.base_url = scheme + "://"+api_domain

        self.headers ={
            "Authorization":  "Bearer " + self.access_token
        }

class OrderRequest(BaseRequest):
    def __init__(self):
        super().__init__()
        self.url = self.base_url + self.account_api +"/"+ self.account_id+"/"+"orders"

    def get_orders(self):
        u"""
        can not use this method
        """
        r = requests.get(self.url,headers=self.headers)
        return r.json()

    def add_orders(self, side, unit=0,):
    #side is sell or buy
        order_type = "market"
        payload = {
            'instrument': self.instruments,
            "type" : order_type,
            "units": unit,
            "side": side
        }
        r = requests.post(self.url, headers=self.headers, data=payload)
        return r.json()

class TradeRequest(BaseRequest):

    def __init__(self):
        super().__init__()
        self.url = self.base_url + self.account_api +"/"+ self.account_id+"/"+"trades"

    def get_list(self, instrument=None, limit=50):
        if instrument:
            instrument = self.instruments
        params = {
            "instrument": instrument,
            "count": limit
        }
        r = requests.get(self.url, params=params, headers=self.headers)
        return r.json()

    def get_detail(self, trade_id):
        detail_url = self.url + "/" + str(trade_id)
        r = requests.get(detail_url, headers=self.headers)
        return r.json()

    def modify_detail(self, trade_id, params):
        u"""

        params.stopLoss
        params.takeProfit
        params.trailingStop
        """
        detail_url = self.url + "/" + str(trade_id)
        r = requests.patch(detail_url, headers=self.headers, data=params)
        return r.json()

    def close_detail(self, trade_id):
        detail_url = self.url + "/" + str(trade_id)
        r = requests.delete(detail_url, headers=self.headers)
        return r.json()
