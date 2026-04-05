import requests
import pandas as pd
import streamlit as st
import time
import re
import yfinance as yf
import numpy as np

ALL_PAIRS = [
    "BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "DOT", "AVAX", "MATIC", "LINK",
    "LTC", "UNI", "ATOM", "ALGO", "NEAR", "FTM", "SAND", "MANA", "CRV", "AAVE",
    "DOGE", "SHIB", "TRX", "ETC", "FIL", "ICP", "VET", "THETA", "XLM", "EGLD",
    "HBAR", "FLOW", "CAKE", "ENJ", "CHZ", "GALA", "AXS", "COMP", "YFI", "SUSHI",
    "1INCH", "GRT", "MKR", "SNX", "ZIL", "DASH", "ZEC", "EOS", "XTZ", "IOTA",
    "APE", "LDO", "OP", "ARB", "INJ", "SUI", "TIA", "SEI", "APT", "ENS",
    "ZENT", "ZEN", "ZEREBRO", "ZETA", "ZIG", "ZK", "ZORA", "ZPAY", "ZRO", "ZRX",
    "MINA", "ROSE", "KAVA", "LUNA", "STX", "RUNE", "KSM", "CELO", "FTM", "ONE",
    "QNT", "RPL", "IMX", "SXP", "KNC", "LRC", "BAT", "DNT", "ZEC", "NEO",
    "ONT", "QTUM", "ANKR", "SC", "HOT", "DGB", "DENT", "COTI", "VTHO", "BAND",
    "SCRT", "Oasis", "OAK", "NODL", "WEMIX", "GTO", "DODO", "ALICE", "PERP", "C98",
    "BICO", "WOO", "MASK", "DYDX", "GNS", "STG", "RDNT", "PENDLE", "JPEG", "HOOK",
    "MAGIC", "GMX", "LQTY", "RDNT", "VELO", "BAL", "CVX", "CRV", "FXS", "PERP",
    "RGT", "SNX", "YFI", "MIR", "UBT", "KNC", "BZR", "JASMY", "DYM", "TIA",
    "ALT", "BLUR", "IMX", "APT", "ARB", "OP", "SOL", "AVAX", "MATIC", "ETH"
]

YAHOO_SYMBOL_MAP = {}

for pair in ALL_PAIRS:
    clean = pair.upper().replace("-", "").replace("_", "")
    YAHOO_SYMBOL_MAP[f"B-{clean}_USDT"] = f"{clean}-USD"

def _get_yahoo_symbol(pair: str) -> str:
    if pair in YAHOO_SYMBOL_MAP:
        return YAHOO_SYMBOL_MAP[pair]
    symbol = pair.replace("B-", "").replace("-USD", "").replace("_USDT", "")
    return f"{symbol}-USD"

def _get_candle_data(symbol: str, interval: str, period: str) -> pd.DataFrame:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
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

@st.cache_data(ttl=120)
def get_ticker():
    start = time.time()
    data = []
    
    for symbol in ALL_PAIRS[:60]:
        try:
            ticker = yf.Ticker(f"{symbol}-USD")
            info = ticker.info
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            if price > 0:
                data.append({
                    "market": f"B-{symbol}_USDT",
                    "last_price": price,
                    "change_24_hour": info.get("regularMarketChange") or 0,
                    "change_24_hour_pct": info.get("regularMarketChangePercent") or 0,
                    "volume": info.get("volume") or 0,
                    "high": info.get("dayHigh") or 0,
                    "low": info.get("dayLow") or 0
                })
        except Exception:
            continue
    
    latency = int((time.time() - start) * 1000)
    return pd.DataFrame(data), latency

@st.cache_data(ttl=60)
def get_ticker_for_pair(pair: str):
    """Get ticker data for a specific pair."""
    symbol = _get_yahoo_symbol(pair)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        if price > 0:
            return {
                "market": pair,
                "last_price": price,
                "change_24_hour": info.get("regularMarketChange") or 0,
                "change_24_hour_pct": info.get("regularMarketChangePercent") or 0,
                "volume": info.get("volume") or 0,
                "high": info.get("dayHigh") or 0,
                "low": info.get("dayLow") or 0
            }
    except Exception:
        pass
    return None

@st.cache_data(ttl=3600)
def get_markets():
    return [{"pair": f"B-{s.upper()}_USDT", "symbol": f"B-{s.upper()}_USDT"} for s in ALL_PAIRS]

def _resolve_pair(pair: str, markets=None) -> str:
    return pair

@st.cache_data(ttl=300)
def get_candles(pair: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    symbol = _get_yahoo_symbol(pair)
    
    interval_map = {
        "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "2h": "2h", "4h": "4h", "1d": "1d", "1w": "1wk"
    }
    
    intervals_to_try = [interval_map.get(interval, "1h"), "1h", "1d", "1wk"]
    periods = ["1y", "1y", "2y", "5y"]
    
    for yf_interval, period in zip(intervals_to_try, periods):
        df = _get_candle_data(symbol, yf_interval, period)
        if not df.empty:
            if limit and len(df) > limit:
                df = df.tail(limit)
            return df
    
    df = _get_candle_data(symbol, "1d", "5y")
    if limit and len(df) > limit:
        df = df.tail(limit)
    return df

def get_candles_safe(pair: str, interval: str = "1m", limit: int = 200) -> pd.DataFrame:
    return get_candles(pair, interval, limit)

@st.cache_data(ttl=300)
def get_yfinance_candles(symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    return get_candles(f"B-{symbol.upper()}_USDT", interval, limit)

def get_best_candles(pair: str, limit: int = 200) -> tuple[pd.DataFrame, str | None]:
    intervals = ["1h", "4h", "1d", "1wk"]
    for interval in intervals:
        df = get_candles_safe(pair, interval, limit)
        if not df.empty:
            return df, interval
    
    df = get_candles(pair, "1d", 365)
    if not df.empty:
        return df, "1d"
    return pd.DataFrame(), None

@st.cache_data(ttl=3600)
def get_all_pairs():
    return [f"B-{s.upper()}_USDT" for s in ALL_PAIRS]

@st.cache_data(ttl=3600)
def get_valid_pairs():
    return [{"symbol": f"B-{s.upper()}_USDT", "pair": f"B-{s.upper()}_USDT"} for s in ALL_PAIRS]

@st.cache_data(ttl=30)
def get_orderbook(pair: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=30)
def get_trades(pair: str) -> pd.DataFrame:
    df = get_candles(pair, "1h", 50)
    if df.empty:
        return pd.DataFrame()
    
    if "close" not in df.columns or "open" not in df.columns:
        return pd.DataFrame()
    
    df = df.copy()
    df["side"] = np.where(df["close"] > df["open"], "buy", "sell")
    df["timestamp"] = df["time"]
    df["price"] = df["close"]
    df["quantity"] = df["volume"]
    df = df[["timestamp", "price", "quantity", "side"]].copy()
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