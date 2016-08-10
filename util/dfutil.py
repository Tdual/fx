import pandas as pd

def get_sma(df, period):
    ser = pd.Series(df)
    sma = ser.rolling(window=period,center=False).mean()
    return sma

def get_std(df, period):
    ser = pd.Series(df)
    std = ser.rolling(window=period,min_periods=period,center=False).std()
    return std


def get_bb(df, period=50, coeff=2):
    u"""
    getting Bollinger Bands
    """

    sma = get_sma(df, period)
    std = get_std(df, period)
    upper = sma + coeff * std
    lower = sma - coeff * std
    bb = pd.concat([df, upper, sma, lower], axis=1)
    upper_label = '+'+str(coeff)+'sigma'
    lower_label = '-'+str(coeff)+'sigma'
    bb.columns = ["closeBid",upper_label, 'SMA',lower_label]
    return bb
