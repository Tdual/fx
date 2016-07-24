import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
import matplotlib.finance as mpf

def get_ohlc(df, interval):
    x = df.resample(interval).ohlc()
    ret = pd.DataFrame(
        {
            'Open': x['Open']['open'],
            'High': x['High']['high'],
            'Low': x['Low']['low'],
            'Close': x['Close']['close']
        },
         columns=['Open','High','Low','Close']
    )
    return ret.dropna()

def display_chart(df, width=20, height=10):
    p = df.plot(
        figsize=(width,height)
    )
    return p

def get_csv_path(name):
    base_path =  'rateData/new/'
    path = base_path + name + "/"+name+".csv"
    return path

def read_one_csv(name):
    file_path = get_csv_path(name)
    df = pd.read_csv(
        file_path,
        names=('Time','Open','High','Low','Close', 'High(ASK)','Low(ASK)'),
        index_col='Time',
        parse_dates=['Time']
    )
    return df


def read_csv(name_list):
    if isinstance(name_list , str):
        name_list = [name_list]
    elif isinstance(name_list, list):
        pass
    else:
        return None
    df_list = []
    for name in name_list:
        print(name)
        df = read_one_csv(name)
        df_list.append(df)
    return pd.concat(df_list)


def display_candlestick(ohlc, candle_width=0.8, width=20, height=10):
    plt.figure(figsize=(width, height), dpi=80)
    ax = plt.subplot()
    return mpf.candlestick2_ohlc(
        ax,
        ohlc['Open'], ohlc['High'], ohlc['Low'], ohlc['Close'],
        width=candle_width,
        colorup='blue', colordown='red',
    )

def get_sma(ohlc, date_interval, price_type="Close"):
    selected_price = ohlc[price_type]
    ser = pd.Series(selected_price)
    sma = ser.rolling(window=date_interval,center=False).mean().dropna()
    return sma

def get_std(ohlc, date_interval,  price_type="Close"):
    di= date_interval
    selected_price = ohlc[price_type]
    ser = pd.Series(selected_price)
    std = ser.rolling(window=di,min_periods=di,center=False).std().dropna()
    return std


def get_bb(ohlc, date_interval=20, coeff=2):
    u"""
    getting Bollinger Bands
    """


    di= date_interval
    sma = get_sma(ohlc, di)
    std = get_std(ohlc, di)
    upper = sma + coeff * std
    lower = sma - coeff * std
    bb = pd.concat([upper, sma, lower], axis=1)
    upper_label = '+'+str(coeff)+'sigma'
    lower_label = '-'+str(coeff)+'sigma'
    bb.columns = [upper_label, 'SMA',lower_label]
    return bb
