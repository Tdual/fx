import pandas as pd

def get_sma(df, date_interval):
    ser = pd.Series(df)
    sma = ser.rolling(window=date_interval,center=False).mean()
    return sma

def get_std(df, date_interval):
    di= date_interval
    ser = pd.Series(df)
    std = ser.rolling(window=di,min_periods=di,center=False).std()
    return std


def get_bb(df, date_interval=20, coeff=2):
    u"""
    getting Bollinger Bands
    """

    di= date_interval
    sma = get_sma(df, di)
    std = get_std(df, di)
    upper = sma + coeff * std
    lower = sma - coeff * std
    bb = pd.concat([df, upper, sma, lower], axis=1)
    upper_label = '+'+str(coeff)+'sigma'
    lower_label = '-'+str(coeff)+'sigma'
    bb.columns = ["closeBid",upper_label, 'SMA',lower_label]
    return bb
