import pandas as pd
import numpy as np

def sma(series, period):
    return series.rolling(window=period).mean()

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def wma(series, period):
    weights = np.arange(1, period + 1)
    return series.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hull_ma(series, period):
    half = int(period / 2)
    sqrt_period = int(np.sqrt(period))
    wma_half = wma(series, half)
    wma_full = wma(series, period)
    diff = 2 * wma_half - wma_full
    return wma(diff, sqrt_period)

def vwap(df):
    q = df["volume"]
    p = (df["high"] + df["low"] + df["close"]) / 3
    return (p * q).cumsum() / q.cumsum()

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = (-delta.clip(upper=0)).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def stochastic_rsi(series, period=14, k_period=3, d_period=3):
    rsi_vals = rsi(series, period)
    rsi_min = rsi_vals.rolling(period).min()
    rsi_max = rsi_vals.rolling(period).max()
    stoch = (rsi_vals - rsi_min) / (rsi_max - rsi_min + 1e-10) * 100
    k = stoch.rolling(k_period).mean()
    d = k.rolling(d_period).mean()
    return k, d

def macd(series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def bollinger_bands(series, period=20, std_dev=2):
    mid = sma(series, period)
    std = series.rolling(period).std()
    upper = mid + std_dev * std
    lower = mid - std_dev * std
    width = (upper - lower) / mid * 100
    return upper, mid, lower, width

def atr(df, period=14):
    high = df["high"]
    low = df["low"]
    close = df["close"]
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def donchian(df, period=20):
    return df["high"].rolling(period).max(), df["low"].rolling(period).min()

def keltner(df, period=20, atr_mult=2):
    mid = ema(df["close"], period)
    atr_val = atr(df, period)
    return mid + atr_mult * atr_val, mid, mid - atr_mult * atr_val

def obv(df):
    direction = np.where(df["close"] > df["close"].shift(1), 1, -1)
    direction[0] = 0
    return pd.Series((direction * df["volume"]).cumsum(), index=df.index)

def accum_dist(df):
    clv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"] + 1e-10)
    return (clv * df["volume"]).cumsum()

def chaikin_mf(df, period=20):
    clv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"] + 1e-10)
    mfv = clv * df["volume"]
    return mfv.rolling(period).sum() / df["volume"].rolling(period).sum()

def williams_r(df, period=14):
    highest_high = df["high"].rolling(period).max()
    lowest_low = df["low"].rolling(period).min()
    return -100 * (highest_high - df["close"]) / (highest_high - lowest_low + 1e-10)

def roc(series, period=12):
    return (series - series.shift(period)) / series.shift(period) * 100

def zscore(series, period=20):
    mean = series.rolling(period).mean()
    std = series.rolling(period).std()
    return (series - mean) / (std + 1e-10)

def rolling_volatility(series, period=20):
    return series.pct_change().rolling(period).std() * np.sqrt(252) * 100

def heikin_ashi(df):
    ha = df.copy()
    ha["close"] = (df["open"] + df["high"] + df["low"] + df["close"]) / 4
    ha["open"] = (df["open"].shift(1) + df["close"].shift(1)) / 2
    ha["high"] = pd.concat([df["high"], ha["open"], ha["close"]], axis=1).max(axis=1)
    ha["low"] = pd.concat([df["low"], ha["open"], ha["close"]], axis=1).min(axis=1)
    return ha.dropna()

def drawdown(returns):
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    return (cumulative - rolling_max) / rolling_max * 100

def sharpe(returns, risk_free=0.05):
    excess = returns - risk_free / 252
    if excess.std() == 0:
        return 0
    return (excess.mean() / excess.std()) * np.sqrt(252)

def cci(df, period=20):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    sma_tp = tp.rolling(period).mean()
    mad = tp.rolling(period).apply(lambda x: np.abs(x - x.mean()).mean())
    return (tp - sma_tp) / (0.015 * mad + 1e-10)

def mfi(df, period=14):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    mf = tp * df["volume"]
    pos_mf = mf.rolling(period).apply(lambda x: x[x > 0].sum(), raw=True)
    neg_mf = mf.rolling(period).apply(lambda x: abs(x[x < 0]).sum(), raw=True)
    mfi = 100 - (100 / (1 + pos_mf / (neg_mf + 1e-10)))
    return mfi

def adx(df, period=14):
    high, low, close = df["high"], df["low"], df["close"]
    plus_dm = np.where((high - high.shift(1)) > (low.shift(1) - low), high - high.shift(1), 0)
    minus_dm = np.where((low.shift(1) - low) > (high - high.shift(1)), low.shift(1) - low, 0)
    plus_dm = pd.Series(plus_dm).rolling(period).mean()
    minus_dm = pd.Series(minus_dm).rolling(period).mean()
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    plus_di = 100 * plus_dm / (atr + 1e-10)
    minus_di = 100 * minus_dm / (atr + 1e-10)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-10)
    return dx.rolling(period).mean()

def stochastic(df, period=14, k_period=3):
    lowest_low = df["low"].rolling(period).min()
    highest_high = df["high"].rolling(period).max()
    k = 100 * (df["close"] - lowest_low) / (highest_high - lowest_low + 1e-10)
    d = k.rolling(k_period).mean()
    return k, d

def ichimoku(df, tenkan=9, kijun=26, senkou_b=52):
    tenkan_sen = (df["high"].rolling(tenkan).max() + df["low"].rolling(tenkan).min()) / 2
    kijun_sen = (df["high"].rolling(kijun).max() + df["low"].rolling(kijun).min()) / 2
    senkou_a = (tenkan_sen + kijun_sen) / 2
    senkou_b_val = (df["high"].rolling(senkou_b).max() + df["low"].rolling(senkou_b).min()) / 2
    chikou = df["close"].shift(-kijun)
    return tenkan_sen, kijun_sen, senkou_a, senkou_b_val, chikou

def vwap_bands(df, period=20, mult=2):
    v = vwap(df)
    std = df["close"].rolling(period).std()
    return v + mult * std, v, v - mult * std

def pivot_points(df):
    pivot = (df["high"] + df["low"] + df["close"]) / 3
    r1 = 2 * pivot - df["low"]
    r2 = pivot + (df["high"] - df["low"])
    r3 = df["high"] + 2 * (pivot - df["low"])
    s1 = 2 * pivot - df["high"]
    s2 = pivot - (df["high"] - df["low"])
    s3 = df["low"] - 2 * (df["high"] - pivot)
    return pivot, r1, r2, r3, s1, s2, s3

def fibonacci_retracement(df):
    max_price = df["high"].max()
    min_price = df["low"].min()
    diff = max_price - min_price
    return max_price - 0.236 * diff, max_price - 0.382 * diff, max_price - 0.5 * diff, max_price - 0.618 * diff, max_price - 0.786 * diff

def ease_of_movement(df, period=14):
    dm = (df["high"] + df["low"]) / 2 - (df["high"].shift(1) + df["low"].shift(1)) / 2
    br = df["volume"] / (df["high"] - df["low"] + 1e-10)
    eom = dm / br
    return eom.rolling(period).mean()

def force_index(df, period=13):
    return (df["close"] - df["close"].shift(1)) * df["volume"]

def mass_index(df, period=25, fast=9):
    range_ = df["high"] - df["low"]
    ema1 = range_.ewm(span=fast).mean()
    ema2 = ema1.ewm(span=fast).mean()
    return ema1.rolling(period).sum() / ema2.rolling(period).sum()

def dpo(series, period=20):
    ma = series.rolling(period).mean()
    return series.shift(int(period / 2 + 1)) - ma

def kst(series, roc1=10, roc2=15, roc3=20, roc4=30, sma1=10, sma2=10, sma3=10, sma4=15, signal=9):
    rcma1 = roc(series, roc1).rolling(sma1).mean()
    rcma2 = roc(series, roc2).rolling(sma2).mean()
    rcma3 = roc(series, roc3).rolling(sma3).mean()
    rcma4 = roc(series, roc4).rolling(sma4).mean()
    kst = rcma1 + rcma2 * 2 + rcma3 * 3 + rcma4 * 4
    signal_line = kst.rolling(signal).mean()
    return kst, signal_line

def trend_intensity(series, period=30):
    ma = series.rolling(period).mean()
    above = (series > ma).rolling(period).sum()
    return (above / period) * 100

def supertrend(df, period=10, mult=3):
    atr_val = atr(df, period)
    hl_avg = (df["high"] + df["low"]) / 2
    upper = hl_avg + mult * atr_val
    lower = hl_avg - mult * atr_val
    in_uptrend = pd.Series(True, index=df.index)
    for i in range(1, len(df)):
        if df["close"].iloc[i] > upper.iloc[i-1]:
            in_uptrend.iloc[i] = True
        elif df["close"].iloc[i] < lower.iloc[i-1]:
            in_uptrend.iloc[i] = False
        else:
            in_uptrend.iloc[i] = in_uptrend.iloc[i-1]
        if in_uptrend.iloc[i]:
            lower.iloc[i] = max(lower.iloc[i], lower.iloc[i-1])
        else:
            upper.iloc[i] = min(upper.iloc[i], upper.iloc[i-1])
    return upper, lower, in_uptrend

def log_returns(series):
    return np.log(series / series.shift(1))

def realized_volatility(series, period=20):
    return log_returns(series).rolling(period).std() * np.sqrt(252) * 100

def momentum(series, period=10):
    return series - series.shift(period)

def tsi(series, long=25, short=13, signal=13):
    m = series.diff()
    abs_m = abs(m)
    ema_long = m.ewm(span=long, adjust=False).mean()
    ema_short = m.ewm(span=short, adjust=False).mean()
    abs_ema_long = abs_m.ewm(span=long, adjust=False).mean()
    abs_ema_short = abs_m.ewm(span=short, adjust=False).mean()
    tsi = 100 * (ema_short - ema_long) / (abs_ema_short - abs_ema_long + 1e-10)
    return tsi, tsi.rolling(signal).mean()

def ulcer_index(series, period=14):
    draw = drawdown(series.pct_change().dropna())
    return np.sqrt((draw ** 2).rolling(period).mean())

def Arnaud_Legaux(df, period=14):
    ml = (df["high"] + df["low"]) / 2
    ml = ml - ml.rolling(period).mean() / (df["volume"] + 1e-10)
    return ml

def kama(series, period=10, fast=2, slow=30):
    fast_alpha = 2 / (fast + 1)
    slow_alpha = 2 / (slow + 1)
    alpha = (fast_alpha * slow_alpha) ** 0.5
    return series.ewm(alpha=alpha, adjust=False).mean()

def elder_ray(df, period=14):
    ema_val = ema(df["close"], period)
    bull_power = df["high"] - ema_val
    bear_power = df["low"] - ema_val
    return bull_power, bear_power

def vortex(df, period=14):
    vm_plus = np.abs(df["high"] - df["low"].shift(1))
    vm_minus = np.abs(df["low"] - df["high"].shift(1))
    tr = atr(df, period)
    vi_plus = vm_plus.rolling(period).sum() / (tr + 1e-10)
    vi_minus = vm_minus.rolling(period).sum() / (tr + 1e-10)
    return vi_plus, vi_minus

def nrp(series, period=14):
    return 100 - (100 / (1 + series.rolling(period).apply(lambda x: (x > 0).sum() / len(x), raw=True)))

def keltner_width(df, period=20, atr_mult=2):
    upper, mid, lower = keltner(df, period, atr_mult)
    return (upper - lower) / mid * 100

def money_flow_volume(df, period=20):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    return (tp * df["volume"]).rolling(period).sum()

def price_volume_trend(df):
    pvt = (df["close"] - df["close"].shift(1)) / df["close"].shift(1) * df["volume"]
    return pvt.cumsum()

def aroon(df, period=25):
    aroon_up = df["high"].rolling(period).apply(lambda x: float(np.argmax(x)) / period * 100, raw=True)
    aroon_down = df["low"].rolling(period).apply(lambda x: float(np.argmin(x)) / period * 100, raw=True)
    return aroon_up, aroon_down

def copp(series, period=14):
    return series * (series / series.shift(period))
