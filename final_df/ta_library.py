from ta.momentum import *
from ta.trend import *
from ta.volume import *

def get_ema(df):
    indicator_ema_100 = EMAIndicator(close=df["close"], window=100, fillna=True)
    indicator_ema_200 = EMAIndicator(close=df["close"], window=200, fillna=True)

    df["ema_100"] = indicator_ema_100.ema_indicator()
    df["ema_200"] = indicator_ema_200.ema_indicator()

    diff100 = (df['close'] - df['ema_100'])/df['ema_100']
    diff200 = (df['close'] - df['ema_200'])/df['ema_200']

    signal = pd.Series(0, index=df.index)
    signal[(diff100 > 0.0025) & (diff200 > 0.002)] = 1
    signal[(diff100 < -0.0025) & (diff200 < -0.002)] = -1

    df["ema_signal"] = signal

    return df

def get_vwap(df):
    indicator_vwap = VolumeWeightedAveragePrice(high=df["high"], low=df["low"], close=df["close"], volume=df["volume"], window=3, fillna=True)

    df["vwap"] = indicator_vwap.volume_weighted_average_price()

    signal = pd.Series(data=np.zeros(len(df)), index=df.index)
    signal[df['close'] > df['vwap']] = 1
    signal[df['close'] < df['vwap']] = -1

    signal = signal.astype(int)
    df['vwap_signal'] = signal

    return df

def get_stochasticrsi(df):
    indicator_stochrsi = StochRSIIndicator(close=df["close"], window=6, smooth1=3, smooth2=3, fillna=True)

    df["stochrsi"] = indicator_stochrsi.stochrsi()
    df["stochrsi_k"] = indicator_stochrsi.stochrsi_k()
    df["stochrsi_d"] = indicator_stochrsi.stochrsi_d()

    overbought = 0.80
    oversold = 0.20
    is_overbought = (df['stochrsi_k'] > overbought) & (df['stochrsi_d'] > overbought) & (df['stochrsi_k'] < df['stochrsi_d'])
    is_oversold = (df['stochrsi_k'] < oversold) & (df['stochrsi_d'] < oversold) & (df['stochrsi_k'] > df['stochrsi_d'])

    signal = pd.Series(np.zeros(len(df)), index=df.index)
    signal[is_overbought] = -1
    signal[is_oversold] = 1

    df['stochrsi_signal'] = signal.astype(int)

    return df

def get_macd(df):
    indicator_macd = MACD(close=df["close"], window_slow=26, window_fast=12, window_sign=9, fillna=True)
    df["macd"] = indicator_macd.macd()
    df["macd_s"] = indicator_macd.macd_signal()

    signal = np.zeros(len(df))
    signal[df["macd"] > df["macd_s"]] = 1
    signal[df["macd"] < df["macd_s"]] = -1

    df["macd_signal"] = signal.astype(int)

    return df

def change(df):
    df['close_change'] = df['close'] - df['close'].shift(1)
    df['close_pct_change'] = df['close_change'] / df['close'].shift(1) * 100

    df['open_change'] = df['open'] - df['open'].shift(1)
    df['open_pct_change'] = df['open_change'] / df['open'].shift(1) * 100

    df['high_change'] = df['high'] - df['high'].shift(1)
    df['high_pct_change'] = df['high_change'] / df['high'].shift(1) * 100

    df['low_change'] = df['low'] - df['low'].shift(1)
    df['low_pct_change'] = df['low_change'] / df['low'].shift(1) * 100

    df['volume_change'] = df['volume'] - df['volume'].shift(1)
    df['volume_pct_change'] = df['volume_change'] / df['volume'].shift(1) * 100
    
    return df

def get_trend(df):
    pct_change = df['close'].pct_change(periods=6)
    df["trend"] = 0

    df.loc[pct_change >= 0.00125, 'trend'] = 1
    df.loc[pct_change <= -0.00125, 'trend'] = -1

    return df