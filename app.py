import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import io
from datetime import datetime

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuantDCX Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── IMPORTS ────────────────────────────────────────────────────────────────────
from styles import TERMINAL_CSS
from api import get_ticker, get_markets, get_candles, get_orderbook, get_trades, get_all_pairs, get_best_candles, get_valid_pairs, get_candles_safe, get_ticker_for_pair
from charts import (
    candlestick_chart, heikin_ashi_chart, macd_chart, volume_profile_chart,
    orderbook_chart, orderbook_heatmap, trade_bubble_chart, buy_sell_pressure,
    correlation_heatmap, market_heatmap, bb_chart, rsi_chart, returns_histogram,
    drawdown_chart, cumulative_returns_chart, price_surface_3d, orderbook_3d,
    volatility_surface_3d, trades_scatter_3d, multi_asset_comparison, obv_chart,
    volatility_chart, zscore_chart, williams_r_chart, stoch_rsi_chart, roc_chart,
    cci_chart, mfi_chart, adx_chart, stochastic_chart, ichimoku_chart,
    pivot_chart, fibonacci_chart, ease_of_movement_chart, force_index_chart,
    mass_index_chart, kst_chart, supertrend_chart, realized_volatility_chart,
    momentum_chart, tsi_chart, ulcer_index_chart, kama_chart, elder_ray_chart,
    vortex_chart, aroon_chart, copp_curve_chart, vwap_bandwidth_chart,
    keltner_width_chart, money_flow_volume_chart, pvt_chart, aroon_oscillator_chart,
    trend_intensity_chart, dpo_chart, log_returns_chart, Arnaud_Legaux_chart,
    keltner_filled_chart, multi_sma_chart, multi_ema_chart, hull_ma_chart,
    wma_chart, accum_dist_chart, donchian_filled_chart,
    apply_layout, DARK_BG, CARD_BG, NEON_BLUE, NEON_GREEN, NEON_RED, NEON_YELLOW, NEON_PURPLE, GRID_COLOR
)
from indicators import sma, ema, rsi, macd, bollinger_bands, atr, hull_ma, donchian, keltner, chaikin_mf

def _get_candles_with_interval_fallback(pair: str, interval: str, limit: int = 200):
    """
    CoinDCX pairs can be illiquid; use get_best_candles which tries both CoinDCX and yfinance.
    """
    df, iv = get_best_candles(pair, limit)
    tried = [iv] if iv else [interval]
    if not df.empty:
        return df, iv if iv else interval, tried
    return df, interval, tried

# ── INJECT CSS ─────────────────────────────────────────────────────────────────
st.markdown(TERMINAL_CSS, unsafe_allow_html=True)

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
INTERVALS = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
VIZ_MODES = ["2D Standard", "2D Advanced", "3D Advanced"]
ALL_PAIRS_DEFAULT = [
    "B-BTC_USDT","B-ETH_USDT","B-BNB_USDT","B-SOL_USDT","B-ADA_USDT",
    "B-XRP_USDT","B-DOT_USDT","B-AVAX_USDT","B-MATIC_USDT","B-LINK_USDT",
    "B-LTC_USDT","B-UNI_USDT","B-ATOM_USDT","B-ALGO_USDT","B-NEAR_USDT",
    "B-FTM_USDT","B-SAND_USDT","B-MANA_USDT","B-CRV_USDT","B-AAVE_USDT",
    "B-DOGE_USDT","B-SHIB_USDT","B-TRX_USDT","B-ETC_USDT","B-FIL_USDT",
    "B-ICP_USDT","B-VET_USDT","B-THETA_USDT","B-XLM_USDT","B-HBAR_USDT",
    "B-FLOW_USDT","B-CAKE_USDT","B-ENJ_USDT","B-CHZ_USDT","B-GALA_USDT",
    "B-AXS_USDT","B-COMP_USDT","B-YFI_USDT","B-SUSHI_USDT","B-GRT_USDT",
    "B-MKR_USDT","B-SNX_USDT","B-ZIL_USDT","B-DASH_USDT","B-ZEC_USDT",
    "B-EOS_USDT","B-XTZ_USDT","B-IOTA_USDT","B-BAT_USDT","B-ZRX_USDT",
    "B-OMG_USDT","B-BAND_USDT","B-KNC_USDT","B-LRC_USDT","B-REN_USDT",
    "B-SRM_USDT","B-OCEAN_USDT","B-ANKR_USDT","B-HOT_USDT","B-WIN_USDT",
    "B-CELR_USDT","B-SKL_USDT","B-COTI_USDT","B-CTSI_USDT","B-DENT_USDT",
    "B-MTL_USDT","B-OGN_USDT","B-STORJ_USDT","B-ALICE_USDT","B-TLM_USDT",
    "B-DODO_USDT","B-POLS_USDT","B-SUPER_USDT","B-QUICK_USDT","B-GHST_USDT",
    "B-MASK_USDT","B-AGLD_USDT","B-RARE_USDT","B-LAZIO_USDT","B-CHESS_USDT",
    "B-JASMY_USDT","B-BICO_USDT","B-WAXP_USDT","B-CLV_USDT","B-ARPA_USDT",
    "B-ORN_USDT","B-PUNDIX_USDT","B-PLA_USDT","B-AUCTION_USDT","B-IDEX_USDT",
    "B-DF_USDT","B-COMBO_USDT","B-HIGH_USDT","B-PEOPLE_USDT","B-XNO_USDT",
    "B-WOO_USDT","B-CFX_USDT","B-APT_USDT","B-INJ_USDT","B-STX_USDT",
    "B-LDO_USDT","B-ARB_USDT","B-OP_USDT","B-SUI_USDT","B-PEPE_USDT",
    "B-FLOKI_USDT","B-BLUR_USDT","B-ID_USDT","B-EDU_USDT","B-MAV_USDT",
]

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0 24px;">
        <div style="font-family:'Orbitron',monospace; font-size:1.3rem; font-weight:900;
             background:linear-gradient(90deg,#00D4FF,#00FF88); -webkit-background-clip:text;
             -webkit-text-fill-color:transparent; background-clip:text;">⚡ QuantDCX</div>
        <div style="color:#6B8BB0; font-size:0.65rem; letter-spacing:3px; margin-top:4px;">TERMINAL v2.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">NAVIGATION</div>', unsafe_allow_html=True)
    pages = {
        "Dashboard": "🏠",
        "Market Analysis": "📊",
        "Trade Flow": "⚡",
        "Advanced Analytics": "🔬",
        "Multi-Compare": "🔀",
        "Market Heatmap": "🌡️",
    }
    for page_name, icon in pages.items():
        active = "active" if st.session_state.page == page_name else ""
        if st.button(f"{icon}  {page_name}", key=f"nav_{page_name}", use_container_width=True):
            st.session_state.page = page_name

    st.markdown("---")
    st.markdown('<div class="section-label">SETTINGS</div>', unsafe_allow_html=True)

    all_pairs = get_all_pairs()
    if not all_pairs:
        all_pairs = ALL_PAIRS_DEFAULT
    
    valid_pairs_data = get_valid_pairs()
    if valid_pairs_data:
        valid_symbols = [p.get("symbol") or p.get("pair") for p in valid_pairs_data if p.get("symbol") or p.get("pair")]
        if valid_symbols:
            all_pairs = sorted(set(all_pairs + valid_symbols))
    
    all_pairs = sorted(set(all_pairs + ALL_PAIRS_DEFAULT))

    selected_pair = st.selectbox("Trading Pair", options=all_pairs,
        index=0 if "B-BTC_USDT" not in all_pairs else all_pairs.index("B-BTC_USDT"),
        key="selected_pair")

    interval = st.selectbox("Interval", options=list(INTERVALS.keys()), index=2)
    viz_mode = st.selectbox("Visualization Mode", options=VIZ_MODES, index=0)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col2:
        st.markdown("<span style='color:#6B8BB0;font-size:0.7rem;'>Press to refresh data</span>", unsafe_allow_html=True)

    st.markdown("---")
    ticker_df, latency = get_ticker()
    lat_class = "danger" if latency > 500 else "warn" if latency > 200 else ""
    st.markdown(f"""
    <div style="padding:8px 0;">
        <span style="color:#6B8BB0;font-size:0.7rem;">API LATENCY</span><br>
        <span class="latency-badge {lat_class}">{latency} ms</span>
        <span style="color:#6B8BB0;font-size:0.65rem; margin-left:8px;">{datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────────
def render_header():
    st.markdown(f"""
    <div class="terminal-header">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="terminal-title">QuantDCX Terminal</div>
                <div class="terminal-subtitle">Professional Crypto Market Analytics · CoinDCX Live Data</div>
            </div>
            <div style="text-align:right;">
                <div class="latency-badge">● LIVE</div>
                <div style="color:#6B8BB0;font-size:0.7rem;margin-top:4px;">{selected_pair} · {interval}</div>
                <div style="color:#6B8BB0;font-size:0.65rem;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── METRIC CARD HELPER ─────────────────────────────────────────────────────────
def metric_card(label, value, sub="", cls="neutral"):
    return f"""<div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {cls}">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>"""

# ── LIVE PRICE PANEL ───────────────────────────────────────────────────────────
def render_live_price(df, pair):
    row = None
    
    if not df.empty and pair in df["market"].values:
        row = df[df["market"] == pair].iloc[0]
    else:
        data = get_ticker_for_pair(pair)
        if data:
            row = data
    
    if row is None:
        return
    
    if isinstance(row, dict):
        last_price = row.get("last_price", 0) or 0
        chg = row.get("change_24_hour", 0) or 0
        high = row.get("high", 0) or 0
        low = row.get("low", 0) or 0
        volume = row.get("volume", 0) or 0
    else:
        last_price = float(row.get("last_price", 0) or 0)
        chg = float(row.get("change_24_hour", 0) or 0)
        high = float(row.get("high", 0) or 0)
        low = float(row.get("low", 0) or 0)
        volume = float(row.get("volume", 0) or 0)
    
    cls = "positive" if chg >= 0 else "negative"
    sign = "+" if chg >= 0 else ""
    
    cols = st.columns(6)
    metrics = [
        ("LAST PRICE", f"${last_price:,.4f}", "", "neutral"),
        ("24H CHANGE", f"{sign}{chg:.2f}%", "vs yesterday", cls),
        ("24H HIGH", f"${high:,.4f}", "Session high", "positive"),
        ("24H LOW", f"${low:,.4f}", "Session low", "negative"),
        ("VOLUME", f"{volume:,.2f}", "Base asset", "neutral"),
        ("BID/ASK", "$--", "No order book", "neutral"),
    ]
    for col, (lbl, val, sub, c) in zip(cols, metrics):
        with col:
            st.markdown(metric_card(lbl, val, sub, c), unsafe_allow_html=True)

# ── PAGE: DASHBOARD ────────────────────────────────────────────────────────────
def page_dashboard():
    render_header()
    ticker_df, _ = get_ticker()
    render_live_price(ticker_df, selected_pair)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="section-label">🟢 TOP GAINERS</div>', unsafe_allow_html=True)
        if not ticker_df.empty and "change_24_hour" in ticker_df.columns:
            gainers = ticker_df.nlargest(8, "change_24_hour")[["market","last_price","change_24_hour"]]
            gainers = gainers.rename(columns={"market":"Pair","last_price":"Price","change_24_hour":"Change%"})
            gainers["Change%"] = gainers["Change%"].apply(lambda x: f"+{x:.2f}%" if x>=0 else f"{x:.2f}%")
            st.dataframe(gainers, use_container_width=True, hide_index=True)

    with col2:
        st.markdown('<div class="section-label">🔴 TOP LOSERS</div>', unsafe_allow_html=True)
        if not ticker_df.empty and "change_24_hour" in ticker_df.columns:
            losers = ticker_df.nsmallest(8, "change_24_hour")[["market","last_price","change_24_hour"]]
            losers = losers.rename(columns={"market":"Pair","last_price":"Price","change_24_hour":"Change%"})
            losers["Change%"] = losers["Change%"].apply(lambda x: f"{x:.2f}%")
            st.dataframe(losers, use_container_width=True, hide_index=True)

    with col3:
        st.markdown('<div class="section-label">📊 HIGHEST VOLUME</div>', unsafe_allow_html=True)
        if not ticker_df.empty and "volume" in ticker_df.columns:
            high_vol = ticker_df.nlargest(8, "volume")[["market","last_price","volume"]]
            high_vol = high_vol.rename(columns={"market":"Pair","last_price":"Price","volume":"Volume"})
            high_vol["Volume"] = high_vol["Volume"].apply(lambda x: f"{x:,.2f}")
            st.dataframe(high_vol, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-label">📈 LIVE CHART</div>', unsafe_allow_html=True)
    df, interval_used, tried = _get_candles_with_interval_fallback(selected_pair, interval)

    if not df.empty:
        if interval_used != interval:
            st.success(f"Using interval: {interval_used} (fallback from {interval})")
        title_iv = interval_used if interval_used == interval else f"{interval_used} (fallback from {interval})"
        fig = candlestick_chart(df, title=f"{selected_pair} · {title_iv}")
        st.plotly_chart(fig, use_container_width=True), key="plot_1")
    else:
        st.warning("⚠️ No candle data available for this pair. Try another market.")


# ── PAGE: MARKET ANALYSIS ──────────────────────────────────────────────────────
def page_market_analysis():
    render_header()
    df, interval_used, tried = _get_candles_with_interval_fallback(selected_pair, interval)
    ticker_df, _ = get_ticker()
    render_live_price(ticker_df, selected_pair)

    if df.empty:
        st.warning("⚠️ No candle data available for this pair. Try another market.")
        with st.expander("Debug info"):
            st.code(f"pair={selected_pair}\ninterval={interval}", language="text")
        return

    st.markdown("### 📊 Panel 1: Price & Trend Indicators")
    tabs1 = st.tabs([
        "📊 Candlestick", "🕯️ Heikin Ashi", "📉 MACD", "📈 Bollinger",
        "💹 RSI", "📊 Volume", "📐 Stoch RSI", "🌀 Williams %R",
        "🔄 ROC", "📉 OBV", "🌊 Volatility", "⚡ Z-Score"
    ])
    with tabs1[0]:
        show_sma = st.checkbox("SMA (20/50)", value=True, key="sma")
        show_ema = st.checkbox("EMA", value=True, key="ema")
        show_vwap = st.checkbox("VWAP", value=True, key="vwap_")
        show_bb = st.checkbox("Bollinger Bands", value=False, key="bb_toggle")
        title_iv = interval_used if interval_used == interval else f"{interval_used} (fallback from {interval})"
        fig = candlestick_chart(df, show_sma=show_sma, show_ema=show_ema, show_vwap=show_vwap, show_bb=show_bb, title=f"Candlestick · {title_iv}")
        st.plotly_chart(fig, use_container_width=True), key="plot_2")
    with tabs1[1]:
        st.plotly_chart(heikin_ashi_chart(df), use_container_width=True), key="plot_3")
    with tabs1[2]:
        st.plotly_chart(macd_chart(df), use_container_width=True), key="plot_4")
    with tabs1[3]:
        st.plotly_chart(bb_chart(df), use_container_width=True), key="plot_5")
    with tabs1[4]:
        st.plotly_chart(rsi_chart(df), use_container_width=True), key="plot_6")
    with tabs1[5]:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(volume_profile_chart(df), use_container_width=True), key="plot_7")
        with col2:
            st.plotly_chart(obv_chart(df), use_container_width=True), key="plot_8")
    with tabs1[6]:
        st.plotly_chart(stoch_rsi_chart(df), use_container_width=True), key="plot_9")
    with tabs1[7]:
        st.plotly_chart(williams_r_chart(df), use_container_width=True), key="plot_10")
    with tabs1[8]:
        st.plotly_chart(roc_chart(df), use_container_width=True), key="plot_11")
    with tabs1[9]:
        st.plotly_chart(obv_chart(df), use_container_width=True), key="plot_12")
    with tabs1[10]:
        st.plotly_chart(volatility_chart(df), use_container_width=True), key="plot_13")
    with tabs1[11]:
        st.plotly_chart(zscore_chart(df), use_container_width=True), key="plot_14")

    st.markdown("### 📊 Panel 2: Momentum & Volume Indicators")
    tabs2 = st.tabs([
        "📉 CCI", "💰 MFI", "🌐 ADX", "🎯 Stoch", "☁️ Ichimoku",
        "📐 Pivot", "🌀 Fib", "📈 EOM", "💪 Force", "⚖️ Mass",
        "📊 KST", "🚀 Supertrend"
    ])
    with tabs2[0]:
        st.plotly_chart(cci_chart(df), use_container_width=True), key="plot_15")
    with tabs2[1]:
        st.plotly_chart(mfi_chart(df), use_container_width=True), key="plot_16")
    with tabs2[2]:
        st.plotly_chart(adx_chart(df), use_container_width=True), key="plot_17")
    with tabs2[3]:
        st.plotly_chart(stochastic_chart(df), use_container_width=True), key="plot_18")
    with tabs2[4]:
        st.plotly_chart(ichimoku_chart(df), use_container_width=True), key="plot_19")
    with tabs2[5]:
        st.plotly_chart(pivot_chart(df), use_container_width=True), key="plot_20")
    with tabs2[6]:
        st.plotly_chart(fibonacci_chart(df), use_container_width=True), key="plot_21")
    with tabs2[7]:
        st.plotly_chart(ease_of_movement_chart(df), use_container_width=True), key="plot_22")
    with tabs2[8]:
        st.plotly_chart(force_index_chart(df), use_container_width=True), key="plot_23")
    with tabs2[9]:
        st.plotly_chart(mass_index_chart(df), use_container_width=True), key="plot_24")
    with tabs2[10]:
        st.plotly_chart(kst_chart(df), use_container_width=True), key="plot_25")
    with tabs2[11]:
        st.plotly_chart(supertrend_chart(df), use_container_width=True), key="plot_26")

    st.markdown("### 📊 Panel 3: Advanced Oscillators")
    tabs3 = st.tabs([
        "📉 Real Vol", "🏃 Momentum", "📈 TSI", "😰 Ulcer", "📉 KAMA",
        "🔊 Elder-Ray", "🌀 Vortex", "🏹 Aroon", "📈 Copp", "📊 VWAP Band",
        "📐 Keltner Width", "💵 MFV"
    ])
    with tabs3[0]:
        st.plotly_chart(realized_volatility_chart(df), use_container_width=True), key="plot_27")
    with tabs3[1]:
        st.plotly_chart(momentum_chart(df), use_container_width=True), key="plot_28")
    with tabs3[2]:
        st.plotly_chart(tsi_chart(df), use_container_width=True), key="plot_29")
    with tabs3[3]:
        st.plotly_chart(ulcer_index_chart(df), use_container_width=True), key="plot_30")
    with tabs3[4]:
        st.plotly_chart(kama_chart(df), use_container_width=True), key="plot_31")
    with tabs3[5]:
        st.plotly_chart(elder_ray_chart(df), use_container_width=True), key="plot_32")
    with tabs3[6]:
        st.plotly_chart(vortex_chart(df), use_container_width=True), key="plot_33")
    with tabs3[7]:
        st.plotly_chart(aroon_chart(df), use_container_width=True), key="plot_34")
    with tabs3[8]:
        st.plotly_chart(copp_curve_chart(df), use_container_width=True), key="plot_35")
    with tabs3[9]:
        st.plotly_chart(vwap_bandwidth_chart(df), use_container_width=True), key="plot_36")
    with tabs3[10]:
        st.plotly_chart(keltner_width_chart(df), use_container_width=True), key="plot_37")
    with tabs3[11]:
        st.plotly_chart(money_flow_volume_chart(df), use_container_width=True), key="plot_38")

    st.markdown("### 📊 Panel 4: Moving Averages & Channels")
    tabs4 = st.tabs([
        "📊 PVT", "📉 Aroon Osc", "💡 Trend Int", "📉 DPO", "📈 Log Returns",
        "🧮 Arnaud", "🎨 Multi SMA", "📈 Multi EMA", "🏄 Hull MA", "⚖️ WMA",
        "📊 A/D", "📐 Donchian"
    ])
    with tabs4[0]:
        st.plotly_chart(pvt_chart(df), use_container_width=True), key="plot_39")
    with tabs4[1]:
        st.plotly_chart(aroon_oscillator_chart(df), use_container_width=True), key="plot_40")
    with tabs4[2]:
        st.plotly_chart(trend_intensity_chart(df), use_container_width=True), key="plot_41")
    with tabs4[3]:
        st.plotly_chart(dpo_chart(df), use_container_width=True), key="plot_42")
    with tabs4[4]:
        st.plotly_chart(log_returns_chart(df), use_container_width=True), key="plot_43")
    with tabs4[5]:
        st.plotly_chart(Arnaud_Legaux_chart(df), use_container_width=True), key="plot_44")
    with tabs4[6]:
        st.plotly_chart(keltner_filled_chart(df), use_container_width=True), key="plot_45")
    with tabs4[7]:
        st.plotly_chart(multi_sma_chart(df), use_container_width=True), key="plot_46")
    with tabs4[8]:
        st.plotly_chart(multi_ema_chart(df), use_container_width=True), key="plot_47")
    with tabs4[9]:
        st.plotly_chart(hull_ma_chart(df), use_container_width=True), key="plot_48")
    with tabs4[10]:
        st.plotly_chart(wma_chart(df), use_container_width=True), key="plot_49")
    with tabs4[11]:
        st.plotly_chart(donchian_filled_chart(df), use_container_width=True), key="plot_50")

    # Download CSV
    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download OHLCV Data (CSV)", data=csv,
            file_name=f"{selected_pair}_{interval}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")


# ── PAGE: TRADE FLOW ───────────────────────────────────────────────────────────
def page_trade_flow():
    render_header()
    trades = get_trades(selected_pair)

    if trades.empty:
        st.warning("Trade data unavailable.")
        with st.expander("Debug info"):
            st.code(f"pair={selected_pair}", language="text")
        return

    buy_count = (trades.get("side", pd.Series()) == "buy").sum() if "side" in trades.columns else 0
    sell_count = (trades.get("side", pd.Series()) == "sell").sum() if "side" in trades.columns else 0
    avg_size = trades["quantity"].mean() if "quantity" in trades.columns else 0
    max_size = trades["quantity"].max() if "quantity" in trades.columns else 0

    cols = st.columns(4)
    with cols[0]: st.markdown(metric_card("BUY TRADES", str(buy_count), "", "positive"), unsafe_allow_html=True)
    with cols[1]: st.markdown(metric_card("SELL TRADES", str(sell_count), "", "negative"), unsafe_allow_html=True)
    with cols[2]: st.markdown(metric_card("AVG SIZE", f"{avg_size:.4f}", "Units", "neutral"), unsafe_allow_html=True)
    with cols[3]: st.markdown(metric_card("MAX TRADE", f"{max_size:.4f}", "Whale size", "neutral"), unsafe_allow_html=True)

    st.markdown("### 📊 Panel 1: Trade Visualizations")
    tabs1 = st.tabs([
        "🫧 Bubble Chart", "📊 Buy/Sell Pressure", "📈 Trade Tape", "🕰️ Trade Intensity", "🌌 3D Scatter",
        "📊 Size Dist", "📈 Buy/Sell Timeline", "📉 Cumulative Vol"
    ])

    with tabs1[0]:
        st.plotly_chart(trade_bubble_chart(trades), use_container_width=True), key="plot_51")

    with tabs1[1]:
        st.plotly_chart(buy_sell_pressure(trades), use_container_width=True), key="plot_52")

    with tabs1[2]:
        st.markdown('<div class="section-label">LIVE TRADE TAPE</div>', unsafe_allow_html=True)
        if "side" in trades.columns:
            tape_html = ""
            for _, t in trades.head(30).iterrows():
                side = t.get("side","buy")
                cls = "trade-buy" if side == "buy" else "trade-sell"
                arrow = "▲" if side == "buy" else "▼"
                price = f"{t.get('price',0):,.4f}"
                qty = f"{t.get('quantity',0):.4f}"
                tape_html += f'<div class="trade-row"><span class="{cls}">{arrow} {side.upper()}</span> &nbsp; <b>{price}</b> &nbsp; <span style="color:#6B8BB0;">qty: {qty}</span></div>'
            st.markdown(f'<div style="max-height:400px;overflow-y:auto;">{tape_html}</div>', unsafe_allow_html=True)

    with tabs1[3]:
        if "timestamp" in trades.columns and "price" in trades.columns:
            intensity = trades.copy()
            intensity["count"] = 1
            fig = go.Figure(go.Scatter(x=intensity["timestamp"], y=intensity["price"],
                mode="lines", line=dict(color=NEON_BLUE, width=1.5), name="Trade Intensity"))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG,
                font=dict(color="#C8D8F0"), title="Trade Intensity Timeline")
            st.plotly_chart(fig, use_container_width=True), key="plot_53")

    with tabs1[4]:
        if viz_mode == "3D Advanced":
            st.plotly_chart(trades_scatter_3d(trades), use_container_width=True), key="plot_54")
        else:
            st.info("Switch to **3D Advanced** in the sidebar.")

    with tabs1[5]:
        if "quantity" in trades.columns:
            fig = px.histogram(trades, x="quantity", nbins=30, title="Trade Size Distribution",
                color_discrete_sequence=[NEON_BLUE])
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"))
            st.plotly_chart(fig, use_container_width=True), key="plot_55")

    with tabs1[6]:
        if "side" in trades.columns and "timestamp" in trades.columns:
            trades_ts = trades.copy()
            trades_ts["buy"] = (trades_ts["side"] == "buy").astype(int)
            trades_ts["sell"] = (trades_ts["side"] == "sell").astype(int)
            trades_ts = trades_ts.sort_values("timestamp")
            trades_ts["cum_buy"] = trades_ts["buy"].cumsum()
            trades_ts["cum_sell"] = trades_ts["sell"].cumsum()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=trades_ts["timestamp"], y=trades_ts["cum_buy"], 
                mode="lines", line=dict(color=NEON_GREEN, width=2), name="Cumulative Buys"))
            fig.add_trace(go.Scatter(x=trades_ts["timestamp"], y=trades_ts["cum_sell"], 
                mode="lines", line=dict(color=NEON_RED, width=2), name="Cumulative Sells"))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Buy/Sell Cumulative Timeline")
            st.plotly_chart(fig, use_container_width=True), key="plot_56")

    with tabs1[7]:
        if "quantity" in trades.columns and "timestamp" in trades.columns:
            trades_cv = trades.copy()
            trades_cv = trades_cv.sort_values("timestamp")
            trades_cv["cum_vol"] = trades_cv["quantity"].cumsum()
            fig = go.Figure(go.Scatter(x=trades_cv["timestamp"], y=trades_cv["cum_vol"],
                mode="lines", fill="tozeroy", fillcolor="rgba(0,212,255,0.2)",
                line=dict(color=NEON_BLUE, width=2), name="Cumulative Volume"))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Cumulative Trade Volume")
            st.plotly_chart(fig, use_container_width=True), key="plot_57")

    st.markdown("### 📊 Panel 2: Advanced Analysis")
    tabs2 = st.tabs([
        "🔥 Trade Heatmap", "⚖️ Order Imbalance", "🐋 Whale Detector", "📊 Price Impact", 
        "⏱️ TWAP Comparison", "📈 Trade Momentum", "💹 Volume Profile", "🕐 Time Analysis"
    ])

    with tabs2[0]:
        if "price" in trades.columns and "quantity" in trades.columns:
            fig = go.Figure(go.Histogram2d(x=trades["price"], y=trades["quantity"],
                colorscale=[[0, NEON_BLUE], [1, NEON_RED]]))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Trade Heatmap (Price vs Quantity)", xaxis_title="Price", yaxis_title="Quantity")
            st.plotly_chart(fig, use_container_width=True), key="plot_58")

    with tabs2[1]:
        if "side" in trades.columns and "quantity" in trades.columns and "timestamp" in trades.columns:
            trades_oi = trades.copy()
            trades_oi = trades_oi.sort_values("timestamp")
            trades_oi["vol"] = trades_oi.apply(lambda x: x["quantity"] if x["side"] == "buy" else -x["quantity"], axis=1)
            trades_oi["imbalance"] = trades_oi["vol"].cumsum()
            fig = go.Figure(go.Scatter(x=trades_oi["timestamp"], y=trades_oi["imbalance"],
                mode="lines", fill="tozeroy", 
                fillcolor="rgba(0,212,255,0.2)",
                line=dict(color=NEON_BLUE, width=2), name="Order Imbalance"))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Order Flow Imbalance")
            st.plotly_chart(fig, use_container_width=True), key="plot_59")

    with tabs2[2]:
        if "quantity" in trades.columns and "price" in trades.columns:
            threshold = trades["quantity"].quantile(0.95)
            whales = trades[trades["quantity"] >= threshold]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=trades.index, y=trades["quantity"], mode="markers",
                marker=dict(color=NEON_BLUE, size=5), name="All Trades"))
            fig.add_trace(go.Scatter(x=whales.index, y=whales["quantity"], mode="markers",
                marker=dict(color=NEON_YELLOW, size=12, symbol="star"), name="Whale Trades"))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title=f"Whale Trade Detection (Top 5%, threshold={threshold:.4f})")
            st.plotly_chart(fig, use_container_width=True), key="plot_60")

    with tabs2[3]:
        if "quantity" in trades.columns and "price" in trades.columns:
            trades_pi = trades.copy()
            trades_pi = trades_pi.sort_values("timestamp")
            trades_pi["price_change"] = trades_pi["price"].diff()
            trades_pi["price_impact"] = trades_pi["price_change"].abs() * trades_pi["quantity"]
            fig = go.Figure(go.Bar(x=trades_pi.index, y=trades_pi["price_impact"],
                marker_color=trades_pi["price_change"].apply(lambda x: NEON_GREEN if x >= 0 else NEON_RED)))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Price Impact per Trade")
            st.plotly_chart(fig, use_container_width=True), key="plot_61")

    with tabs2[4]:
        if "price" in trades.columns and "timestamp" in trades.columns:
            trades_twap = trades.copy()
            trades_twap = trades_twap.sort_values("timestamp")
            trades_twap["twap"] = trades_twap["price"].expanding().mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=trades_twap["timestamp"], y=trades_twap["price"],
                mode="lines", line=dict(color="#6B8BB0", width=1), name="Price"))
            fig.add_trace(go.Scatter(x=trades_twap["timestamp"], y=trades_twap["twap"],
                mode="lines", line=dict(color=NEON_YELLOW, width=2), name="TWAP"))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Price vs TWAP Comparison")
            st.plotly_chart(fig, use_container_width=True), key="plot_62")

    with tabs2[5]:
        if "price" in trades.columns and "quantity" in trades.columns and "timestamp" in trades.columns:
            trades_mom = trades.copy()
            trades_mom = trades_mom.sort_values("timestamp")
            trades_mom["vwap"] = (trades_mom["price"] * trades_mom["quantity"]).cumsum() / trades_mom["quantity"].cumsum()
            trades_mom["momentum"] = trades_mom["price"] - trades_mom["vwap"]
            fig = go.Figure(go.Scatter(x=trades_mom["timestamp"], y=trades_mom["momentum"],
                mode="lines", line=dict(color=NEON_PURPLE, width=2), name="Trade Momentum"))
            fig.add_hline(y=0, line_dash="dash", line_color="#6B8BB0")
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Trade Momentum (Price - VWAP)")
            st.plotly_chart(fig, use_container_width=True), key="plot_63")

    with tabs2[6]:
        if "price" in trades.columns and "quantity" in trades.columns:
            bins = np.linspace(trades["price"].min(), trades["price"].max(), 20)
            trades["price_bin"] = pd.cut(trades["price"], bins=bins)
            vol_profile = trades.groupby("price_bin")["quantity"].sum()
            fig = go.Figure(go.Bar(x=vol_profile.index.astype(str), y=vol_profile.values,
                marker_color=NEON_GREEN, name="Volume at Price"))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Volume Profile by Price Level", xaxis_title="Price Range", yaxis_title="Volume")
            st.plotly_chart(fig, use_container_width=True), key="plot_64")

    with tabs2[7]:
        if "timestamp" in trades.columns:
            trades_time = trades.copy()
            trades_time["hour"] = pd.to_datetime(trades_time["timestamp"]).dt.hour
            hourly_vol = trades_time.groupby("hour")["quantity"].sum() if "quantity" in trades.columns else trades_time.groupby("hour").size()
            fig = go.Figure(go.Bar(x=hourly_vol.index, y=hourly_vol.values,
                marker_color=NEON_BLUE, name="Trade Volume"))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Trade Activity by Hour of Day", xaxis_title="Hour", yaxis_title="Volume/Count")
            st.plotly_chart(fig, use_container_width=True), key="plot_65")


# ── PAGE: ADVANCED ANALYTICS ───────────────────────────────────────────────────
def page_advanced():
    render_header()
    df, interval_used, tried = _get_candles_with_interval_fallback(selected_pair, interval)

    if df.empty:
        st.warning("⚠️ No candle data available for this pair. Try another market.")
        with st.expander("Debug info"):
            st.code(f"pair={selected_pair}\ninterval={interval}", language="text")
        return

    st.markdown('<div class="section-label">🔬 ADVANCED ANALYTICS</div>', unsafe_allow_html=True)

    st.markdown("### Panel 1: Returns & Risk Analysis")
    tabs1 = st.tabs([
        "Cumulative Returns", "Drawdown", "Returns Dist",
        "Volatility", "Z-Score", "Keltner/Donchian",
        "Hull MA", "Chaikin MF", "Real Vol", "Momentum"
    ])

    with tabs1[0]:
        st.plotly_chart(cumulative_returns_chart(df), use_container_width=True), key="plot_66")

    with tabs1[1]:
        st.plotly_chart(drawdown_chart(df), use_container_width=True), key="plot_67")

    with tabs1[2]:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(returns_histogram(df), use_container_width=True), key="plot_68")
        with col2:
            if not df.empty:
                returns = df["close"].pct_change().dropna() * 100
                skew = returns.skew()
                kurt = returns.kurtosis()
                cols = st.columns(2)
                with cols[0]: st.markdown(metric_card("SKEWNESS", f"{skew:.3f}", "Distribution shape", "neutral"), unsafe_allow_html=True)
                with cols[1]: st.markdown(metric_card("KURTOSIS", f"{kurt:.3f}", "Tail heaviness", "neutral"), unsafe_allow_html=True)
                vol = returns.std() * np.sqrt(252)
                st.markdown(metric_card("ANN. VOLATILITY", f"{vol:.2f}%", "Historical", "neutral"), unsafe_allow_html=True)

    with tabs1[3]:
        st.plotly_chart(volatility_chart(df), use_container_width=True), key="plot_69")

    with tabs1[4]:
        st.plotly_chart(zscore_chart(df), use_container_width=True), key="plot_70")

    with tabs1[5]:
        if not df.empty:
            kelt_upper, kelt_mid, kelt_lower = keltner(df)
            don_upper, don_lower = donchian(df)
            if (
                pd.Series(kelt_upper).dropna().empty
                and pd.Series(kelt_lower).dropna().empty
                and pd.Series(don_upper).dropna().empty
                and pd.Series(don_lower).dropna().empty
            ):
                st.info("Need more candles to compute Keltner/Donchian channels (default period=20).")
            else:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"))
                fig.add_trace(go.Scatter(x=df["time"], y=kelt_upper, line=dict(color=NEON_YELLOW, width=1, dash="dash"), name="Keltner Upper"))
                fig.add_trace(go.Scatter(x=df["time"], y=kelt_lower, line=dict(color=NEON_YELLOW, width=1, dash="dash"), name="Keltner Lower"))
                fig.add_trace(go.Scatter(x=df["time"], y=don_upper, line=dict(color=NEON_PURPLE, width=1, dash="dot"), name="Donchian Upper"))
                fig.add_trace(go.Scatter(x=df["time"], y=don_lower, line=dict(color=NEON_PURPLE, width=1, dash="dot"), name="Donchian Lower"))
                fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                    title="Keltner + Donchian Channels", height=500)
                st.plotly_chart(fig, use_container_width=True), key="plot_71")

    with tabs1[6]:
        if not df.empty:
            hull = hull_ma(df["close"], 20)
            if pd.Series(hull).dropna().empty:
                st.info("Need more candles to compute Hull MA (period=20).")
            else:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"))
                fig.add_trace(go.Scatter(x=df["time"], y=hull, line=dict(color=NEON_GREEN, width=2), name="Hull MA(20)"))
                fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"), title="Hull Moving Average")
                st.plotly_chart(fig, use_container_width=True), key="plot_72")

    with tabs1[7]:
        if not df.empty:
            cmf = chaikin_mf(df)
            if pd.Series(cmf).dropna().empty:
                st.info("Need more candles to compute Chaikin Money Flow (period=20).")
            else:
                colors = [NEON_GREEN if v >= 0 else NEON_RED for v in cmf.fillna(0)]
                fig = go.Figure(go.Bar(x=df["time"], y=cmf, marker_color=colors, name="Chaikin MF"))
                fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                    title="Chaikin Money Flow")
                st.plotly_chart(fig, use_container_width=True), key="plot_73")

    with tabs1[8]:
        st.plotly_chart(realized_volatility_chart(df), use_container_width=True), key="plot_74")

    with tabs1[9]:
        st.plotly_chart(momentum_chart(df), use_container_width=True), key="plot_75")

    st.markdown("### Panel 2: 3D Visualization")
    tabs2 = st.tabs([
        "3D Price Surface", "3D Volatility", "Price Ribbon", "Volume Surface",
        "Time Series 3D", "Return Surface", "Heatmap 3D", "Price Velocity"
    ])

    with tabs2[0]:
        st.plotly_chart(price_surface_3d(df), use_container_width=True), key="plot_76")

    with tabs2[1]:
        st.plotly_chart(volatility_surface_3d(df), use_container_width=True), key="plot_77")

    with tabs2[2]:
        if not df.empty:
            sma20 = sma(df["close"], 20)
            sma50 = sma(df["close"], 50)
            sma200 = sma(df["close"], 200)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color="#6B8BB0", width=1), name="Price"))
            fig.add_trace(go.Scatter(x=df["time"], y=sma20, line=dict(color=NEON_GREEN, width=1.5), name="SMA 20"))
            fig.add_trace(go.Scatter(x=df["time"], y=sma50, line=dict(color=NEON_YELLOW, width=1.5), name="SMA 50"))
            fig.add_trace(go.Scatter(x=df["time"], y=sma200, line=dict(color=NEON_RED, width=1.5), name="SMA 200"))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Price Ribbon (Multiple SMAs)")
            st.plotly_chart(fig, use_container_width=True), key="plot_78")

    with tabs2[3]:
        if not df.empty and "volume" in df.columns:
            fig = go.Figure(go.Surface(
                x=df["time"], y=df["close"], z=df["volume"].values.reshape(-1, 1),
                colorscale=[[0, NEON_BLUE], [1, NEON_RED]]))
            fig.update_layout(paper_bgcolor=DARK_BG, font=dict(color="#C8D8F0"),
                title="Volume Surface", scene=dict(xaxis_title="Time", yaxis_title="Price", zaxis_title="Volume"))
            st.plotly_chart(fig, use_container_width=True), key="plot_79")

    with tabs2[4]:
        if not df.empty:
            fig = go.Figure(go.Scatter3d(
                x=df["time"], y=df["close"], z=df["volume"],
                mode="markers", marker=dict(size=3, color=df["close"], colorscale="Viridis")))
            fig.update_layout(paper_bgcolor=DARK_BG, font=dict(color="#C8D8F0"),
                title="Time-Price-Volume 3D", scene=dict(xaxis_title="Time", yaxis_title="Price", zaxis_title="Volume"))
            st.plotly_chart(fig, use_container_width=True), key="plot_80")

    with tabs2[5]:
        if not df.empty:
            returns = df["close"].pct_change().dropna() * 100
            fig = go.Figure(go.Histogram2d(x=df["time"].iloc[1:], y=returns,
                colorscale=[[0, NEON_BLUE], [1, NEON_RED]]))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Return Distribution Heatmap")
            st.plotly_chart(fig, use_container_width=True), key="plot_81")

    with tabs2[6]:
        if not df.empty:
            df_heat = df.copy()
            df_heat["hour"] = pd.to_datetime(df_heat["time"]).dt.hour
            df_heat["day"] = pd.to_datetime(df_heat["time"]).dt.dayofweek
            pivot = df_heat.pivot_table(values="volume", index="hour", columns="day", aggfunc="sum")
            fig = go.Figure(go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index,
                colorscale=[[0, NEON_BLUE], [1, NEON_RED]]))
            fig.update_layout(paper_bgcolor=DARK_BG, font=dict(color="#C8D8F0"),
                title="Volume Heatmap (Hour vs Day)")
            st.plotly_chart(fig, use_container_width=True), key="plot_82")

    with tabs2[7]:
        if not df.empty:
            df["price_diff"] = df["close"].diff()
            df["velocity"] = df["price_diff"].rolling(5).mean()
            df["accel"] = df["velocity"].diff()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["time"], y=df["velocity"], line=dict(color=NEON_BLUE, width=1.5), name="Velocity"))
            fig.add_trace(go.Scatter(x=df["time"], y=df["accel"], line=dict(color=NEON_RED, width=1), name="Acceleration"))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"),
                title="Price Velocity & Acceleration")
            st.plotly_chart(fig, use_container_width=True), key="plot_83")

    st.markdown("### Panel 3: Oscillators & Momentum")
    tabs3 = st.tabs([
        "CCI", "MFI", "ADX", "Stoch", "TSI",
        "Ulcer", "Elder-Ray", "Vortex", "KST", "Supertrend"
    ])

    with tabs3[0]:
        st.plotly_chart(cci_chart(df), use_container_width=True), key="plot_84")

    with tabs3[1]:
        st.plotly_chart(mfi_chart(df), use_container_width=True), key="plot_85")

    with tabs3[2]:
        st.plotly_chart(adx_chart(df), use_container_width=True), key="plot_86")

    with tabs3[3]:
        st.plotly_chart(stochastic_chart(df), use_container_width=True), key="plot_87")

    with tabs3[4]:
        st.plotly_chart(tsi_chart(df), use_container_width=True), key="plot_88")

    with tabs3[5]:
        st.plotly_chart(ulcer_index_chart(df), use_container_width=True), key="plot_89")

    with tabs3[6]:
        st.plotly_chart(elder_ray_chart(df), use_container_width=True), key="plot_90")

    with tabs3[7]:
        st.plotly_chart(vortex_chart(df), use_container_width=True), key="plot_91")

    with tabs3[8]:
        st.plotly_chart(kst_chart(df), use_container_width=True), key="plot_92")

    with tabs3[9]:
        st.plotly_chart(supertrend_chart(df), use_container_width=True), key="plot_93")

    st.markdown("### Panel 4: Trend & Indicators")
    tabs4 = st.tabs([
        "Ichimoku", "Pivot", "Fib", "EOM", "Force",
        "Mass", "KAMA", "Aroon", "Copp", "VWAP Band"
    ])

    with tabs4[0]:
        st.plotly_chart(ichimoku_chart(df), use_container_width=True), key="plot_94")

    with tabs4[1]:
        st.plotly_chart(pivot_chart(df), use_container_width=True), key="plot_95")

    with tabs4[2]:
        st.plotly_chart(fibonacci_chart(df), use_container_width=True), key="plot_96")

    with tabs4[3]:
        st.plotly_chart(ease_of_movement_chart(df), use_container_width=True), key="plot_97")

    with tabs4[4]:
        st.plotly_chart(force_index_chart(df), use_container_width=True), key="plot_98")

    with tabs4[5]:
        st.plotly_chart(mass_index_chart(df), use_container_width=True), key="plot_99")

    with tabs4[6]:
        st.plotly_chart(kama_chart(df), use_container_width=True), key="plot_100")

    with tabs4[7]:
        st.plotly_chart(aroon_chart(df), use_container_width=True), key="plot_101")

    with tabs4[8]:
        st.plotly_chart(copp_curve_chart(df), use_container_width=True), key="plot_102")

    with tabs4[9]:
        st.plotly_chart(vwap_bandwidth_chart(df), use_container_width=True), key="plot_103")

    st.markdown("### Panel 5: Candlestick Patterns")
    tabs5 = st.tabs([
        "Standard Candles", "Heikin Ashi", "Line Break", "Renko",
        "Kagi", "Point & Figure", "Range Bars", "Trend Bars",
        "OHLC Bars", "Hollow Candles"
    ])

    with tabs5[0]:
        show_sma = st.checkbox("Show SMA", value=True, key="sma_std")
        show_ema = st.checkbox("Show EMA", value=True, key="ema_std")
        title_iv = interval_used if interval_used == interval else f"{interval_used} (fallback from {interval})"
        fig = candlestick_chart(df, show_sma=show_sma, show_ema=show_ema, show_vwap=False, show_bb=False, title=f"Standard Candlestick - {title_iv}")
        st.plotly_chart(fig, use_container_width=True), key="plot_104")

    with tabs5[1]:
        st.plotly_chart(heikin_ashi_chart(df), use_container_width=True), key="plot_105")

    with tabs5[2]:
        if not df.empty:
            df_lb = df.copy()
            close = df_lb["close"]
            df_lb["lb_close"] = close
            df_lb["lb_open"] = df_lb["lb_close"].shift(1).fillna(close.iloc[0])
            for i in range(1, len(df_lb)):
                if close.iloc[i] >= df_lb["lb_close"].iloc[i-1]:
                    df_lb.at[df_lb.index[i], "lb_close"] = close.iloc[i]
                    df_lb.at[df_lb.index[i], "lb_open"] = df_lb["lb_close"].iloc[i-1]
                else:
                    df_lb.at[df_lb.index[i], "lb_close"] = close.iloc[i]
                    df_lb.at[df_lb.index[i], "lb_open"] = df_lb["lb_close"].iloc[i-1]
            colors = [NEON_GREEN if c >= o else NEON_RED for c, o in zip(df_lb["lb_close"], df_lb["lb_open"])]
            fig = go.Figure(go.Bar(x=df_lb["time"], y=df_lb["lb_close"] - df_lb["lb_open"], marker_color=colors))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"), title="Line Break Chart")
            st.plotly_chart(fig, use_container_width=True), key="plot_106")

    with tabs5[3]:
        if not df.empty:
            box_size = (df["high"].max() - df["low"].min()) / 20
            df_renko = df.copy()
            df_renko["renko"] = (df["close"] / box_size).round() * box_size
            fig = go.Figure(go.Scatter(x=df_renko.index, y=df_renko["renko"], mode="lines", line=dict(color=NEON_BLUE, width=2)))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"), title="Renko Chart")
            st.plotly_chart(fig, use_container_width=True), key="plot_107")

    with tabs5[4]:
        if not df.empty:
            fig = go.Figure(go.Scatter(x=df["time"], y=df["close"], mode="lines", line=dict(color=NEON_BLUE, width=2)))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"), title="Kagi Chart (Simplified)")
            st.plotly_chart(fig, use_container_width=True), key="plot_108")

    with tabs5[5]:
        if not df.empty:
            fig = go.Figure(go.Scatter(x=df["time"], y=df["close"], mode="lines", line=dict(color=NEON_YELLOW, width=2)))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"), title="Point & Figure (Simplified)")
            st.plotly_chart(fig, use_container_width=True), key="plot_109")

    with tabs5[6]:
        if not df.empty:
            bar_size = (df["high"].max() - df["low"].min()) / 10
            df_rb = df.copy()
            df_rb["range"] = (df["close"] / bar_size).round() * bar_size
            fig = go.Figure(go.Bar(x=df_rb["time"], y=df_rb["range"], marker_color=NEON_BLUE))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"), title="Range Bars")
            st.plotly_chart(fig, use_container_width=True), key="plot_110")

    with tabs5[7]:
        if not df.empty:
            df_tb = df.copy()
            ma = df_tb["close"].rolling(5).mean()
            df_tb["trend_up"] = df_tb["close"] > ma
            colors = [NEON_GREEN if t else NEON_RED for t in df_tb["trend_up"]]
            fig = go.Figure(go.Bar(x=df_tb["time"], y=df_tb["close"], marker_color=colors))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"), title="Trend Bars")
            st.plotly_chart(fig, use_container_width=True), key="plot_111")

    with tabs5[8]:
        if not df.empty:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df["time"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
                increasing_line_color=NEON_GREEN, decreasing_line_color=NEON_RED, name="OHLC"))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"), title="OHLC Bars")
            st.plotly_chart(fig, use_container_width=True), key="plot_112")

    with tabs5[9]:
        if not df.empty:
            df_hc = df.copy()
            df_hc["is_hollow"] = df_hc["close"] > df_hc["open"]
            colors_hc = ["rgba(0,255,136,0.8)" if h else "rgba(255,51,102,0.8)" for h in df_hc["is_hollow"]]
            fig = go.Figure(go.Bar(x=df_hc["time"], y=df_hc["close"] - df_hc["open"], marker_color=colors_hc))
            fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG, font=dict(color="#C8D8F0"), title="Hollow Candles")
            st.plotly_chart(fig, use_container_width=True), key="plot_113")

# ── PAGE: MULTI-COMPARE ────────────────────────────────────────────────────────
def page_multi_compare():
    render_header()
    st.markdown('<div class="section-label">🔀 MULTI-ASSET COMPARISON</div>', unsafe_allow_html=True)
    st.info("Select up to 6 assets to compare performance side-by-side.")

    compare_pairs = st.multiselect("Select Assets (max 6)", options=ALL_PAIRS_DEFAULT,
        default=["B-BTC_USDT", "B-ETH_USDT", "B-SOL_USDT"],
        max_selections=6, key="compare_pairs")

    if not compare_pairs:
        st.warning("Select at least one asset.")
        return

    candidate_intervals = [interval] + [iv for iv in ["5m", "15m", "1h", "4h", "1d"] if iv != interval]
    chosen_interval = None
    price_dict = {}
    missing_pairs: list[str] = []

    for iv in candidate_intervals:
        tmp_prices = {}
        tmp_missing: list[str] = []
        progress = st.progress(0)
        for i, pair in enumerate(compare_pairs):
            candle_df = get_candles(pair, iv)
            if not candle_df.empty:
                tmp_prices[pair.split("-")[1].split("_")[0]] = candle_df.set_index("time")["close"]
            else:
                tmp_missing.append(pair)
            progress.progress((i + 1) / len(compare_pairs))
        progress.empty()

        if len(tmp_prices) >= 2:
            chosen_interval = iv
            price_dict = tmp_prices
            missing_pairs = tmp_missing
            break

    if not price_dict:
        st.error("Could not fetch data for selected pairs on any interval.")
        st.info("Tried intervals: " + ", ".join(candidate_intervals))
        return

    if chosen_interval and chosen_interval != interval:
        st.info(f"Using interval {chosen_interval} (fallback from {interval}) for comparison.")
    if missing_pairs:
        st.warning("No candle data for: " + ", ".join(missing_pairs))

    tabs = st.tabs(["📈 Normalized Returns", "📊 Correlation Matrix", "🌐 3D Correlation", "📉 Individual Charts"])

    with tabs[0]:
        st.plotly_chart(multi_asset_comparison(price_dict), use_container_width=True), key="plot_114")

    with tabs[1]:
        st.plotly_chart(correlation_heatmap(price_dict), use_container_width=True), key="plot_115")

    with tabs[2]:
        if len(price_dict) >= 2:
            prices_df = pd.DataFrame(price_dict).dropna()
            returns_df = prices_df.pct_change().dropna()
            corr = returns_df.corr()
            names = list(corr.columns)
            fig = go.Figure(go.Surface(z=corr.values, x=names, y=names,
                colorscale=[[0, NEON_RED], [0.5, "#000000"], [1, NEON_GREEN]],
                opacity=0.85, showscale=True))
            fig.update_layout(paper_bgcolor=DARK_BG,
                scene=dict(bgcolor=DARK_BG, xaxis_title="", yaxis_title="", zaxis_title="Correlation"),
                title="3D Correlation Surface", height=600, font=dict(color="#C8D8F0"))
            st.plotly_chart(fig, use_container_width=True), key="plot_116")

    with tabs[3]:
        for name, prices in price_dict.items():
            with st.expander(f"📊 {name}", expanded=False):
                fig = go.Figure(go.Scatter(y=prices, mode="lines",
                    line=dict(color=NEON_BLUE, width=1.5)))
                fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG,
                    font=dict(color="#C8D8F0"), title=name, height=250)
                st.plotly_chart(fig, use_container_width=True), key="plot_117")

    if len(price_dict) >= 2:
        prices_df = pd.DataFrame(price_dict).dropna()
        csv = prices_df.to_csv()
        st.download_button("⬇️ Download Comparison Data", data=csv, file_name="comparison.csv", mime="text/csv")

# ── PAGE: MARKET HEATMAP ───────────────────────────────────────────────────────
def page_market_heatmap():
    render_header()
    st.markdown('<div class="section-label">🌡️ MARKET-WIDE HEATMAP</div>', unsafe_allow_html=True)
    ticker_df, _ = get_ticker()
    if ticker_df.empty:
        st.error("Cannot load ticker data.")
        return
    fig = market_heatmap(ticker_df)
    st.plotly_chart(fig, use_container_width=True), key="plot_118")

    st.markdown('<div class="section-label">📊 FULL MARKET TABLE</div>', unsafe_allow_html=True)
    if not ticker_df.empty:
        display = ticker_df[["market","last_price","change_24_hour","high","low","volume"]].copy()
        display.columns = ["Pair","Price","Change%","High","Low","Volume"]
        display = display.dropna().sort_values("Change%", ascending=False)
        search = st.text_input("🔍 Search pair...", "")
        if search:
            display = display[display["Pair"].str.contains(search.upper(), na=False)]
        st.dataframe(display.style.format({"Price":"{:,.4f}","Change%":"{:+.2f}","High":"{:,.4f}","Low":"{:,.4f}","Volume":"{:,.2f}"}),
            use_container_width=True, hide_index=True, height=400)
        csv = display.to_csv(index=False)
        st.download_button("⬇️ Download Market Data", data=csv, file_name="market_data.csv", mime="text/csv")


def render_footer():
    st.markdown("""
    <div class="terminal-footer">
        <div style="margin-bottom:8px;">
            <span style="font-family:'Orbitron',monospace; color:#00D4FF; font-size:0.85rem;">⚡ QuantDCX Terminal</span>
        </div>
        <div>Made with ❤️ by <b style="color:#00FF88;">Sourish Dey</b></div>
        <div style="margin-top:8px;">
            <a class="footer-link" href="https://github.com/sourishdey2005" target="_blank">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="vertical-align:middle;margin-right:4px;">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
                </svg>GitHub
            </a>
            <a class="footer-link" href="https://www.linkedin.com/in/sourish-dey-20b170206/" target="_blank">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="vertical-align:middle;margin-right:4px;">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>LinkedIn
            </a>
        </div>
        <div style="color:#6B8BB0;font-size:0.65rem;margin-top:8px;">
            Data provided by CoinDCX · Real-time market data · For informational purposes only
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── ROUTER ─────────────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "Dashboard":
    page_dashboard()
elif page == "Market Analysis":
    page_market_analysis()
elif page == "Trade Flow":
    page_trade_flow()
elif page == "Advanced Analytics":
    page_advanced()
elif page == "Multi-Compare":
    page_multi_compare()
elif page == "Market Heatmap":
    page_market_heatmap()

render_footer()
