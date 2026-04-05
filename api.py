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
    "APE", "LDO", "OP", "ARB", "INJ", "SUI", "TIA", "SEI", "APT"
]

YAHOO_SYMBOL_MAP = {
    "B-BTC_USDT": "BTC-USD", "B-ETH_USDT": "ETH-USD", "B-BNB_USDT": "BNB-USD",
    "B-SOL_USDT": "SOL-USD", "B-ADA_USDT": "ADA-USD", "B-XRP_USDT": "XRP-USD",
    "B-DOT_USDT": "DOT-USD", "B-AVAX_USDT": "AVAX-USD", "B-MATIC_USDT": "MATIC-USD",
    "B-LINK_USDT": "LINK-USD", "B-LTC_USDT": "LTC-USD", "B-UNI_USDT": "UNI-USD",
    "B-ATOM_USDT": "ATOM-USD", "B-ALGO_USDT": "ALGO-USD", "B-NEAR_USDT": "NEAR-USD",
    "B-FTM_USDT": "FTM-USD", "B-SAND_USDT": "SAND-USD", "B-MANA_USDT": "MANA-USD",
    "B-CRV_USDT": "CRV-USD", "B-AAVE_USDT": "AAVE-USD", "B-DOGE_USDT": "DOGE-USD",
    "B-SHIB_USDT": "SHIB-USD", "B-TRX_USDT": "TRX-USD", "B-ETC_USDT": "ETC-USD",
    "B-FIL_USDT": "FIL-USD", "B-ICP_USDT": "ICP-USD", "B-VET_USDT": "VET-USD",
    "B-THETA_USDT": "THETA-USD", "B-XLM_USDT": "XLM-USD", "B-EGLD_USDT": "EGLD-USD",
    "B-HBAR_USDT": "HBAR-USD", "B-FLOW_USDT": "FLOW-USD", "B-CAKE_USDT": "CAKE-USD",
    "B-ENJ_USDT": "ENJ-USD", "B-CHZ_USDT": "CHZ-USD", "B-GALA_USDT": "GALA-USD",
    "B-AXS_USDT": "AXS-USD", "B-COMP_USDT": "COMP-USD", "B-YFI_USDT": "YFI-USD",
    "B-SUSHI_USDT": "SUSHI-USD", "B-1INCH_USDT": "1INCH-USD", "B-GRT_USDT": "GRT-USD",
    "B-MKR_USDT": "MKR-USD", "B-SNX_USDT": "SNX-USD", "B-ZIL_USDT": "ZIL-USD",
    "B-DASH_USDT": "DASH-USD", "B-ZEC_USDT": "ZEC-USD", "B-EOS_USDT": "EOS-USD",
    "B-XTZ_USDT": "XTZ-USD", "B-IOTA_USDT": "IOTA-USD", "B-APE_USDT": "APE-USD",
    "B-LDO_USDT": "LDO-USD", "B-OP_USDT": "OP-USD", "B-ARB_USDT": "ARB-USD",
    "B-INJ_USDT": "INJ-USD", "B-SUI_USDT": "SUI-USD", "B-TIA_USDT": "TIA-USD",
    "B-SEI_USDT": "SEI-USD", "B-APT_USDT": "APT-USD",
}

def _get_yahoo_symbol(pair: str) -> str:
    if pair in YAHOO_SYMBOL_MAP:
        return YAHOO_SYMBOL_MAP[pair]
    symbol = pair.replace("B-", "").replace("-USD", "").replace("_USDT", "")
    return f"{symbol}-USD"

def _get_candle_data(symbol: str, interval: str, period: str, limit: int) -> pd.DataFrame:
    """Fetch candle data with proper error handling."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval, limit=limit)
        
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
    """Fetch candles with multiple interval fallback."""
    symbol = _get_yahoo_symbol(pair)
    
    interval_map = {
        "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "2h": "2h", "4h": "4h", "1d": "1d", "1w": "1wk"
    }
    
    intervals_to_try = [interval_map.get(interval, "1h"), "1h", "1d", "1wk"]
    
    for yf_interval in intervals_to_try:
        df = _get_candle_data(symbol, yf_interval, "1y", limit)
        if not df.empty and len(df) >= 10:
            return df
    
    df = _get_candle_data(symbol, "1d", "2y", 365)
    return df

def get_candles_safe(pair: str, interval: str = "1m", limit: int = 200) -> pd.DataFrame:
    return get_candles(pair, interval, limit)

@st.cache_data(ttl=300)
def get_yfinance_candles(symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    return get_candles(f"B-{symbol}_USDT", interval, limit)

def get_best_candles(pair: str, limit: int = 200) -> tuple[pd.DataFrame, str | None]:
    intervals = ["1h", "4h", "1d", "1wk"]
    for interval in intervals:
        df = get_candles_safe(pair, interval, limit)
        if not df.empty and len(df) >= 10:
            return df, interval
    
    df = get_candles(pair, "1d", 365)
    if not df.empty and len(df) >= 10:
        return df, "1d"
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
    df = get_candles(pair, "1h", 50)
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