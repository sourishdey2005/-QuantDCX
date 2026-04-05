import requests
import pandas as pd
import streamlit as st
import time
import re
import yfinance as yf
import numpy as np

DEFAULT_PAIRS = [
    "BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "DOT", "AVAX", "MATIC", "LINK",
    "LTC", "UNI", "ATOM", "ALGO", "NEAR", "FTM", "SAND", "MANA", "CRV", "AAVE",
    "DOGE", "SHIB", "TRX", "ETC", "FIL", "ICP", "VET", "THETA", "XLM", "EGLD",
    "HBAR", "FLOW", "CAKE", "ENJ", "CHZ", "GALA", "AXS", "COMP", "YFI", "SUSHI",
    "1INCH", "GRT", "MKR", "SNX", "ZIL", "DASH", "ZEC", "EOS", "XTZ", "IOTA",
    "APE", "LDO", "OP", "ARB", "INJ", "SUI", "TIA", "SEI", "APT", "ARB"
]

def _get_yahoo_symbol(pair: str) -> str:
    symbol = pair.replace("B-", "").replace("-USD", "").replace("_USDT", "")
    return f"{symbol}-USD"

@st.cache_data(ttl=60)
def get_ticker():
    start = time.time()
    data = []
    
    for symbol in DEFAULT_PAIRS:
        try:
            ticker = yf.Ticker(f"{symbol}-USD")
            info = ticker.info
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            change = info.get("regularMarketChange") or 0
            change_pct = info.get("regularMarketChangePercent") or 0
            volume = info.get("volume") or 0
            high = info.get("dayHigh") or 0
            low = info.get("dayLow") or 0
            if price > 0:
                data.append({
                    "market": f"B-{symbol}_USDT",
                    "last_price": price,
                    "change_24_hour": change,
                    "change_24_hour_pct": change_pct,
                    "volume": volume,
                    "high": high,
                    "low": low
                })
        except Exception:
            continue
    
    latency = int((time.time() - start) * 1000)
    return pd.DataFrame(data), latency

@st.cache_data(ttl=60)
def get_markets():
    return [{"pair": f"B-{s}_USDT", "symbol": f"B-{s}_USDT"} for s in DEFAULT_PAIRS]

def _resolve_pair(pair: str, markets=None) -> str:
    return pair

@st.cache_data(ttl=300)
def get_candles(pair: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    try:
        symbol = _get_yahoo_symbol(pair)
        interval_map = {
            "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1h", "2h": "2h", "4h": "4h", "1d": "1d", "1w": "1wk"
        }
        yf_interval = interval_map.get(interval, "1h")
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y", interval=yf_interval, limit=limit)
        
        if df.empty:
            return pd.DataFrame()
        
        df = df.reset_index()
        df.columns = [c.lower() if c != "Datetime" else "time" for c in df.columns]
        
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"])
        elif "date" in df.columns:
            df["time"] = pd.to_datetime(df["date"])
        
        df = df.rename(columns={
            "open": "open", "high": "high", "low": "low", "close": "close", "volume": "volume"
        })
        
        required = ["time", "open", "high", "low", "close", "volume"]
        for col in required:
            if col not in df.columns:
                df[col] = 0
        
        return df[required].dropna().sort_values("time").reset_index(drop=True)
    except Exception:
        return pd.DataFrame()

def get_candles_safe(pair: str, interval: str = "1m", limit: int = 200) -> pd.DataFrame:
    return get_candles(pair, interval, limit)

@st.cache_data(ttl=300)
def get_yfinance_candles(symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    return get_candles(f"B-{symbol}_USDT", interval, limit)

def get_best_candles(pair: str, limit: int = 200) -> tuple[pd.DataFrame, str | None]:
    intervals = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d", "1w"]
    for interval in intervals:
        df = get_candles_safe(pair, interval, limit)
        if not df.empty:
            return df, interval
    return pd.DataFrame(), None

@st.cache_data(ttl=3600)
def get_all_pairs():
    return [f"B-{s}_USDT" for s in DEFAULT_PAIRS]

@st.cache_data(ttl=3600)
def get_valid_pairs():
    return [{"symbol": f"B-{s}_USDT", "pair": f"B-{s}_USDT"} for s in DEFAULT_PAIRS]

@st.cache_data(ttl=30)
def get_orderbook(pair: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=30)
def get_trades(pair: str) -> pd.DataFrame:
    df = get_candles(pair, "1m", 50)
    if not df.empty:
        df = df.rename(columns={"close": "price", "volume": "quantity"})
        df["side"] = np.where(df["close"] > df["open"], "buy", "sell")
        df["timestamp"] = df["time"]
    return df

def _normalize_trades(raw) -> pd.DataFrame:
    return get_trades("BTC")

def _normalize_ohlcv(raw) -> pd.DataFrame:
    return pd.DataFrame()

def _fetch_json(url: str, timeout: int = 5):
    return []

@st.cache_data(ttl=3600)
def compute_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    return prices_df.pct_change().dropna()

def optimize_portfolio(returns_df: pd.DataFrame, objective: str = "sharpe"):
    return [], [], []