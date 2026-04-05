import requests
import pandas as pd
import streamlit as st
import time
import re

BASE_URL = "https://public.coindcx.com"
TICKER_URL = "https://api.coindcx.com/exchange/ticker"
MARKETS_URL = "https://api.coindcx.com/exchange/v1/markets"
MARKETS_DETAILS_URL = "https://api.coindcx.com/exchange/v1/markets_details"

def _to_datetime_safe(series: pd.Series) -> pd.Series:
    s_num = pd.to_numeric(series, errors="coerce")
    if s_num.notna().sum() >= max(1, int(0.5 * len(series))):
        med = s_num.dropna().median() if not s_num.dropna().empty else None
        if med is None:
            return pd.to_datetime(series, errors="coerce")
        unit = "ms" if med >= 1e11 else "s" if med >= 1e9 else None
        return pd.to_datetime(s_num, unit=unit, errors="coerce") if unit else pd.to_datetime(s_num, errors="coerce")
    return pd.to_datetime(series, errors="coerce")

def _normalize_ohlcv(raw) -> pd.DataFrame:
    if raw is None:
        return pd.DataFrame()

    data = raw
    if isinstance(raw, dict):
        for key in ("data", "candles", "result"):
            if key in raw and isinstance(raw[key], list):
                data = raw[key]
                break

    if not isinstance(data, list) or not data:
        return pd.DataFrame()

    first = data[0]
    if isinstance(first, (list, tuple)):
        df = pd.DataFrame(data)
        if df.shape[1] < 5:
            return pd.DataFrame()

        row0 = df.iloc[0].tolist()
        big_idxs = [i for i, v in enumerate(row0) if isinstance(v, (int, float)) and v >= 1e9]
        time_idx = None
        if big_idxs:
            if 0 in big_idxs and (len(row0) < 6 or 5 not in big_idxs):
                time_idx = 0
            elif 5 in big_idxs:
                time_idx = 5
            else:
                time_idx = big_idxs[0]

        if df.shape[1] >= 6:
            if time_idx == 0:
                cols = ["time", "open", "high", "low", "close", "volume"]
            elif time_idx == 5:
                cols = ["open", "high", "low", "close", "volume", "time"]
            else:
                cols = ["time", "open", "high", "low", "close", "volume"]
            df = df.iloc[:, :6]
            df.columns = cols
        else:
            df = df.iloc[:, :5]
            df.columns = ["time", "open", "high", "low", "close"]
    elif isinstance(first, dict):
        df = pd.DataFrame(data)
        lower = {c: str(c).lower() for c in df.columns}
        df = df.rename(columns=lower)

        key_map = {}
        def _pick(dst: str, options: list[str]):
            for opt in options:
                if opt in df.columns and dst not in df.columns:
                    key_map[opt] = dst
                    return

        _pick("time", ["time", "timestamp", "t", "ts", "date"])
        _pick("open", ["open", "o"])
        _pick("high", ["high", "h"])
        _pick("low", ["low", "l"])
        _pick("close", ["close", "c"])
        _pick("volume", ["volume", "v", "vol", "q"])
        if key_map:
            df = df.rename(columns=key_map)
    else:
        return pd.DataFrame()

    for c in ("open", "high", "low", "close", "volume"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "time" in df.columns:
        df["time"] = _to_datetime_safe(df["time"])

    if "close" not in df.columns:
        return pd.DataFrame()

    for c in ("open", "high", "low"):
        if c not in df.columns:
            df[c] = df["close"]

    if "volume" not in df.columns:
        df["volume"] = 0.0

    df = df.dropna(subset=["time", "open", "high", "low", "close"]).sort_values("time").reset_index(drop=True)
    return df[["time", "open", "high", "low", "close", "volume"]]

def _resolve_pair(pair: str, markets: list[dict] | None = None) -> str:
    if not pair:
        return pair

    pair = str(pair).strip()
    if "_" in pair and "-" in pair:
        return pair

    if markets:
        pair_l = pair.lower()
        for m in markets:
            if not isinstance(m, dict):
                continue
            for k in ("pair", "symbol", "market", "coindcx_name", "name"):
                v = m.get(k)
                if v and str(v).lower() == pair_l:
                    candidate = m.get("pair") or m.get("symbol") or m.get("market") or pair
                    candidate = str(candidate).strip()
                    if "_" in candidate and "-" in candidate:
                        return candidate

    # Heuristic for compact symbols like BTCUSDT / ETHINR etc.
    m = re.match(r"^([A-Za-z0-9]+?)(USDT|USDC|BTC|ETH|INR)$", pair)
    if m:
        base, quote = m.group(1).upper(), m.group(2).upper()
        return f"B-{base}_{quote}"

    return pair

def _normalize_orderbook_side(side_raw) -> pd.DataFrame:
    if side_raw is None:
        return pd.DataFrame(columns=["price", "quantity"])
    if isinstance(side_raw, list) and side_raw:
        first = side_raw[0]
        if isinstance(first, (list, tuple)):
            df = pd.DataFrame(side_raw, columns=["price", "quantity"])
        elif isinstance(first, dict):
            df = pd.DataFrame(side_raw)
            df = df.rename(columns={c: str(c).lower() for c in df.columns})
            rename = {}
            for k in ("price", "rate", "p"):
                if k in df.columns:
                    rename[k] = "price"
                    break
            for k in ("quantity", "qty", "q", "volume", "amount"):
                if k in df.columns:
                    rename[k] = "quantity"
                    break
            df = df.rename(columns=rename)
            df = df[["price", "quantity"]] if {"price", "quantity"}.issubset(df.columns) else pd.DataFrame(columns=["price", "quantity"])
        else:
            df = pd.DataFrame(columns=["price", "quantity"])
    else:
        df = pd.DataFrame(columns=["price", "quantity"])

    if not df.empty:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df = df.dropna(subset=["price", "quantity"])
    return df.reset_index(drop=True)

def _normalize_trades(raw) -> pd.DataFrame:
    if raw is None:
        return pd.DataFrame()

    data = raw
    if isinstance(raw, dict):
        for key in ("data", "trades", "result"):
            if key in raw and isinstance(raw[key], list):
                data = raw[key]
                break

    if not isinstance(data, list) or not data:
        return pd.DataFrame()

    if not isinstance(data[0], dict):
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df = df.rename(columns={c: str(c).lower() for c in df.columns})

    rename = {}
    for k in ("price", "p", "rate"):
        if k in df.columns:
            rename[k] = "price"
            break
    for k in ("quantity", "q", "qty", "volume", "amount"):
        if k in df.columns:
            rename[k] = "quantity"
            break
    for k in ("timestamp", "time", "t", "ts", "created_at"):
        if k in df.columns:
            rename[k] = "timestamp"
            break
    if rename:
        df = df.rename(columns=rename)

    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    if "timestamp" in df.columns:
        df["timestamp"] = _to_datetime_safe(df["timestamp"])

    if "side" in df.columns:
        df["side"] = df["side"].astype(str).str.lower().map({"buy": "buy", "b": "buy", "sell": "sell", "s": "sell"}).fillna("buy")
    elif "t" in df.columns:
        df["side"] = df["t"].astype(str).str.lower().map({"buy": "buy", "b": "buy", "sell": "sell", "s": "sell"}).fillna("buy")
    elif "m" in df.columns:
        df["side"] = df["m"].apply(lambda x: "sell" if bool(x) else "buy")
    else:
        df["side"] = "buy"

    required = [c for c in ("price", "quantity") if c in df.columns]
    if required:
        df = df.dropna(subset=required)
    if "timestamp" in df.columns:
        df = df.dropna(subset=["timestamp"]).sort_values("timestamp", ascending=False)

    return df.reset_index(drop=True)

def _fetch_json(url: str, timeout: float = 5):
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

@st.cache_data(ttl=2)
def get_ticker():
    try:
        t0 = time.time()
        df = pd.DataFrame(_fetch_json(TICKER_URL, timeout=5))
        latency = round((time.time() - t0) * 1000, 1)
        for col in ["last_price", "high", "low", "volume", "change_24_hour", "bid", "ask"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df, latency
    except Exception as e:
        return pd.DataFrame(), 0

@st.cache_data(ttl=60)
def get_markets():
    try:
        return _fetch_json(MARKETS_URL, timeout=5)
    except Exception:
        return []

@st.cache_data(ttl=3)
def get_candles(pair="B-BTC_USDT", interval="1m", limit=200):
    try:
        markets = get_markets()
        pair = _resolve_pair(pair, markets)
        url = f"{BASE_URL}/market_data/candles?pair={pair}&interval={interval}&limit={limit}"
        return _normalize_ohlcv(_fetch_json(url, timeout=5))
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=2)
def get_orderbook(pair="B-BTC_USDT"):
    try:
        markets = get_markets()
        pair = _resolve_pair(pair, markets)
        url = f"{BASE_URL}/market_data/orderbook?pair={pair}"
        data = _fetch_json(url, timeout=5)
        bids = _normalize_orderbook_side(data.get("bids", []))
        asks = _normalize_orderbook_side(data.get("asks", []))
        bids = bids.sort_values("price", ascending=False).head(30).reset_index(drop=True)
        asks = asks.sort_values("price", ascending=True).head(30).reset_index(drop=True)
        return bids, asks
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=2)
def get_trades(pair="B-BTC_USDT", limit=100):
    try:
        markets = get_markets()
        pair = _resolve_pair(pair, markets)
        url = f"{BASE_URL}/market_data/trade_history?pair={pair}&limit={limit}"
        return _normalize_trades(_fetch_json(url, timeout=5))
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_all_pairs():
    """Return list of 100+ trading pairs."""
    try:
        markets = get_markets()
        pairs: list[str] = []
        if markets:
            for m in markets:
                if not isinstance(m, dict):
                    continue
                p = m.get("pair") or m.get("symbol") or m.get("market")
                if not p:
                    continue
                p = str(p).strip()
                if "_" in p and "-" in p:
                    pairs.append(p)
        if pairs:
            return sorted(set(pairs))

        df, _ = get_ticker()
        if df.empty:
            return _default_pairs()
        raw = df["market"].dropna().astype(str).tolist() if "market" in df.columns else _default_pairs()
        # Keep only plausible public-api pairs if possible; otherwise return raw.
        resolved = [_resolve_pair(p, markets=None) for p in raw]
        resolved_valid = [p for p in resolved if "_" in p and "-" in p]
        return sorted(set(resolved_valid)) if resolved_valid else sorted(set(raw))
    except Exception:
        return _default_pairs()

def _default_pairs():
    bases = ["BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "DOT", "AVAX", "MATIC", "LINK",
             "LTC", "UNI", "ATOM", "ALGO", "NEAR", "FTM", "SAND", "MANA", "CRV", "AAVE",
             "DOGE", "SHIB", "TRX", "ETC", "FIL", "ICP", "VET", "THETA", "XLM", "EGLD",
             "HBAR", "FLOW", "CAKE", "ENJ", "CHZ", "GALA", "AXS", "COMP", "YFI", "SUSHI",
             "1INCH", "GRT", "MKR", "SNX", "ZIL", "DASH", "ZEC", "EOS", "XTZ", "IOTA"]
    return [f"B-{b}_USDT" for b in bases]

@st.cache_data(ttl=3600)
def get_valid_pairs():
    """Get only active USDT pairs from markets_details API."""
    try:
        data = _fetch_json(MARKETS_DETAILS_URL, timeout=10)
        if not data:
            return []
        df = pd.DataFrame(data)
        if "status" not in df.columns or "base_currency_short_name" not in df.columns:
            return []
        df = df[(df["status"] == "active") & (df["base_currency_short_name"] == "USDT")]
        if "symbol" in df.columns and "pair" in df.columns:
            return df[["symbol", "pair"]].to_dict("records")
        return []
    except Exception:
        return []

def get_candles_safe(pair: str, interval: str = "1m", limit: int = 200) -> pd.DataFrame:
    """Safe candle fetch with timeout and error handling."""
    try:
        markets = get_markets()
        pair = _resolve_pair(pair, markets)
        url = f"{BASE_URL}/market_data/candles?pair={pair}&interval={interval}&limit={limit}"
        return _normalize_ohlcv(_fetch_json(url, timeout=5))
    except Exception:
        return pd.DataFrame()

def get_yfinance_candles(symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    """Fallback candle fetch using yfinance."""
    try:
        import yfinance as yf
        
        interval_map = {
            "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1h", "2h": "2h", "4h": "4h", "1d": "1d", "1w": "1wk"
        }
        yf_interval = interval_map.get(interval, "1h")
        
        ticker = yf.Ticker(f"{symbol}-USD" if not symbol.endswith("-USD") else symbol)
        df = ticker.history(period="1y", interval=yf_interval, limit=limit)
        
        if df.empty:
            return pd.DataFrame()
        
        df = df.reset_index()
        df.columns = [c.lower() if c != 'Datetime' else 'time' for c in df.columns]
        
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
        elif 'date' in df.columns:
            df['time'] = pd.to_datetime(df['date'])
        
        df = df.rename(columns={
            'open': 'open', 'high': 'high', 'low': 'low', 
            'close': 'close', 'volume': 'volume'
        })
        
        required_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0
        
        df = df[required_cols].dropna().sort_values("time").reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame()

def get_best_candles(pair: str, limit: int = 200) -> tuple[pd.DataFrame, str | None]:
    """Try CoinDCX first, then yfinance as fallback."""
    intervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "1d", "1w"]
    
    for interval in intervals:
        df = get_candles_safe(pair, interval, limit)
        if not df.empty:
            return df, interval
    
    symbol = pair.replace("B-", "").replace("_USDT", "").replace("-", "")
    
    for interval in intervals:
        df = get_yfinance_candles(symbol, interval, limit)
        if not df.empty:
            return df, interval
    
    return pd.DataFrame(), None
