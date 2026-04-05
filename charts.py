import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from indicators import (sma, ema, rsi, macd, bollinger_bands, atr,
                                 vwap, obv, stochastic_rsi, williams_r, roc,
                                 rolling_volatility, heikin_ashi, donchian,
                                 keltner, chaikin_mf, accum_dist, hull_ma,
                                 wma, zscore, drawdown)

DARK_BG = "#050A14"
CARD_BG = "#0A1628"
NEON_BLUE = "#00D4FF"
NEON_GREEN = "#00FF88"
NEON_RED = "#FF3366"
NEON_YELLOW = "#FFD700"
NEON_PURPLE = "#BF5AF2"
GRID_COLOR = "#1A2744"

CHART_LAYOUT = dict(
    paper_bgcolor=DARK_BG,
    plot_bgcolor=CARD_BG,
    font=dict(color="#C8D8F0", family="JetBrains Mono, monospace", size=11),
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, showgrid=True),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, showgrid=True),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(10,22,40,0.8)", bordercolor=NEON_BLUE, borderwidth=1),
)

def apply_layout(fig, title=""):
    fig.update_layout(**CHART_LAYOUT, title=dict(text=title, font=dict(color=NEON_BLUE, size=14)))
    return fig

def _no_data_figure(title: str, message: str = "No data to display", height: int = 450) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(color="#6B8BB0", size=14),
    )
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text=title, font=dict(color=NEON_BLUE, size=14)),
        height=height,
    )
    fig.update_xaxes(visible=False, showgrid=False, zeroline=False)
    fig.update_yaxes(visible=False, showgrid=False, zeroline=False)
    return fig

# ── CANDLESTICK ──────────────────────────────────────────────────────────────
def candlestick_chart(df, show_sma=True, show_ema=True, show_vwap=True,
                       show_bb=True, show_volume=True, title="Candlestick"):
    if df.empty:
        return _no_data_figure(title, "Candle data unavailable.")
    rows = 3 if show_volume else 2
    row_heights = [0.6, 0.2, 0.2] if show_volume else [0.7, 0.3]
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        row_heights=row_heights, vertical_spacing=0.02)
    # Candles
    fig.add_trace(go.Candlestick(
        x=df["time"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        increasing_line_color=NEON_GREEN, decreasing_line_color=NEON_RED,
        increasing_fillcolor=NEON_GREEN, decreasing_fillcolor=NEON_RED,
        name="Price", line_width=1), row=1, col=1)
    if show_sma:
        fig.add_trace(go.Scatter(x=df["time"], y=sma(df["close"], 20),
            line=dict(color=NEON_YELLOW, width=1.2), name="SMA20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["time"], y=sma(df["close"], 50),
            line=dict(color=NEON_PURPLE, width=1.2), name="SMA50"), row=1, col=1)
    if show_ema:
        fig.add_trace(go.Scatter(x=df["time"], y=ema(df["close"], 12),
            line=dict(color=NEON_BLUE, width=1, dash="dot"), name="EMA12"), row=1, col=1)
    if show_vwap:
        v = vwap(df)
        fig.add_trace(go.Scatter(x=df["time"], y=v,
            line=dict(color="#FF9F43", width=1.5), name="VWAP"), row=1, col=1)
    if show_bb:
        upper, mid, lower, _ = bollinger_bands(df["close"])
        fig.add_trace(go.Scatter(x=df["time"], y=upper, line=dict(color="#4ECDC4", width=0.8, dash="dash"), name="BB Upper"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["time"], y=lower, line=dict(color="#4ECDC4", width=0.8, dash="dash"),
            fill="tonexty", fillcolor="rgba(78,205,196,0.05)", name="BB Lower"), row=1, col=1)
    # RSI
    rsi_vals = rsi(df["close"])
    fig.add_trace(go.Scatter(x=df["time"], y=rsi_vals, line=dict(color=NEON_BLUE, width=1.5), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color=NEON_RED, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color=NEON_GREEN, row=2, col=1)
    # Volume
    if show_volume:
        colors = [NEON_GREEN if c >= o else NEON_RED for c, o in zip(df["close"], df["open"])]
        fig.add_trace(go.Bar(x=df["time"], y=df["volume"], marker_color=colors,
            name="Volume", opacity=0.7), row=3, col=1)
    fig.update_layout(**CHART_LAYOUT, title=dict(text=title, font=dict(color=NEON_BLUE, size=14)), height=700)
    return fig

# ── HEIKIN ASHI ───────────────────────────────────────────────────────────────
def heikin_ashi_chart(df):
    if df.empty:
        return _no_data_figure("Heikin Ashi Chart", "Candle data unavailable.")
    ha = heikin_ashi(df)
    if ha.empty:
        return _no_data_figure("Heikin Ashi Chart", "Not enough candles to compute Heikin Ashi.")
    fig = go.Figure(go.Candlestick(
        x=ha["time"], open=ha["open"], high=ha["high"], low=ha["low"], close=ha["close"],
        increasing_line_color=NEON_GREEN, decreasing_line_color=NEON_RED,
        name="Heikin Ashi"))
    return apply_layout(fig, "Heikin Ashi Chart")

# ── MACD ──────────────────────────────────────────────────────────────────────
def macd_chart(df):
    if df.empty:
        return _no_data_figure("MACD Analysis", "Candle data unavailable.")
    ml, sl, hist = macd(df["close"])
    if ml.dropna().empty and sl.dropna().empty and hist.dropna().empty:
        return _no_data_figure("MACD Analysis", "Not enough candles to compute MACD.")
    fig = make_subplots(rows=2, cols=1, row_heights=[0.6, 0.4], shared_xaxes=True)
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=ml, line=dict(color=NEON_GREEN, width=1.5), name="MACD"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=sl, line=dict(color=NEON_RED, width=1.5), name="Signal"), row=2, col=1)
    colors = [NEON_GREEN if v >= 0 else NEON_RED for v in hist.fillna(0)]
    fig.add_trace(go.Bar(x=df["time"], y=hist, marker_color=colors, name="Histogram", opacity=0.7), row=2, col=1)
    fig.update_layout(**CHART_LAYOUT, title=dict(text="MACD Analysis", font=dict(color=NEON_BLUE, size=14)), height=600)
    return fig

# ── VOLUME PROFILE ─────────────────────────────────────────────────────────────
def volume_profile_chart(df):
    if df.empty:
        return _no_data_figure("Volume Profile (VPVR)", "Candle data unavailable.")
    if "volume" not in df.columns or df["volume"].fillna(0).sum() == 0:
        return _no_data_figure("Volume Profile (VPVR)", "Volume data unavailable for this interval.")
    bins = pd.cut(df["close"], bins=30)
    vol_profile = df.groupby(bins, observed=True)["volume"].sum()
    centers = [interval.mid for interval in vol_profile.index]
    fig = go.Figure(go.Bar(x=vol_profile.values, y=centers, orientation="h",
        marker_color=NEON_BLUE, marker_opacity=0.7, name="Volume Profile"))
    return apply_layout(fig, "Volume Profile (VPVR)")

# ── ORDER BOOK ─────────────────────────────────────────────────────────────────
def orderbook_chart(bids, asks):
    if bids.empty or asks.empty:
        return _no_data_figure("Order Book Depth", "Order book data unavailable.", height=420)
    bids = bids.copy()
    asks = asks.copy()
    bids["cumvol"] = bids["quantity"].cumsum()
    asks["cumvol"] = asks["quantity"].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bids["price"], y=bids["cumvol"],
        fill="tozeroy", fillcolor="rgba(0,255,136,0.15)",
        line=dict(color=NEON_GREEN, width=2), name="Bids"))
    fig.add_trace(go.Scatter(x=asks["price"], y=asks["cumvol"],
        fill="tozeroy", fillcolor="rgba(255,51,102,0.15)",
        line=dict(color=NEON_RED, width=2), name="Asks"))
    return apply_layout(fig, "Order Book Depth")

def orderbook_heatmap(bids, asks):
    if bids.empty or asks.empty:
        return _no_data_figure("Bid/Ask Heatmap", "Order book data unavailable.", height=420)
    fig = make_subplots(rows=1, cols=2, subplot_titles=["Bids", "Asks"])
    fig.add_trace(go.Bar(x=bids["quantity"], y=bids["price"].astype(str),
        orientation="h", marker_color=NEON_GREEN, marker_opacity=0.8, name="Bids"), row=1, col=1)
    fig.add_trace(go.Bar(x=asks["quantity"], y=asks["price"].astype(str),
        orientation="h", marker_color=NEON_RED, marker_opacity=0.8, name="Asks"), row=1, col=2)
    fig.update_layout(**CHART_LAYOUT, title=dict(text="Bid/Ask Heatmap", font=dict(color=NEON_BLUE, size=14)), height=500)
    return fig

# ── TRADE FLOW ─────────────────────────────────────────────────────────────────
def trade_bubble_chart(trades):
    if trades.empty:
        return _no_data_figure("Trade Bubble Chart", "Trade data unavailable.")
    if not {"price", "quantity"}.issubset(trades.columns):
        return _no_data_figure("Trade Bubble Chart", "Trade payload missing price/quantity.")
    colors = [NEON_GREEN if s == "buy" else NEON_RED for s in trades.get("side", ["buy"] * len(trades))]
    sizes = trades["quantity"].fillna(1).clip(lower=1)
    sizes_scaled = (sizes / sizes.max() * 40 + 5).tolist()
    fig = go.Figure(go.Scatter(
        x=trades.get("timestamp", trades.index),
        y=trades["price"],
        mode="markers",
        marker=dict(size=sizes_scaled, color=colors, opacity=0.7, line=dict(width=1, color="rgba(255,255,255,0.3)")),
        text=[f"Side: {s}<br>Qty: {q:.4f}<br>Price: {p:.4f}"
              for s, q, p in zip(trades.get("side", []), trades["quantity"], trades["price"])],
        hovertemplate="%{text}<extra></extra>",
        name="Trades"))
    return apply_layout(fig, "Trade Bubble Chart")

def buy_sell_pressure(trades):
    if trades.empty:
        return _no_data_figure("Buy vs Sell Pressure", "Trade data unavailable.", height=380)
    if "quantity" not in trades.columns:
        return _no_data_figure("Buy vs Sell Pressure", "Trade payload missing quantity.", height=380)
    buys = trades[trades.get("side", pd.Series()) == "buy"]["quantity"].sum() if "side" in trades.columns else 0
    sells = trades[trades.get("side", pd.Series()) == "sell"]["quantity"].sum() if "side" in trades.columns else 0
    fig = go.Figure(go.Bar(x=["Buy Volume", "Sell Volume"], y=[buys, sells],
        marker_color=[NEON_GREEN, NEON_RED], marker_opacity=0.85))
    return apply_layout(fig, "Buy vs Sell Pressure")

# ── CORRELATION MATRIX ─────────────────────────────────────────────────────────
def correlation_heatmap(price_dict):
    if not price_dict:
        return _no_data_figure("Correlation Matrix", "No assets selected.", height=420)
    df = pd.DataFrame(price_dict)
    corr = df.pct_change().dropna().corr()
    if corr.empty:
        return _no_data_figure("Correlation Matrix", "Not enough data to compute correlations.", height=420)
    fig = go.Figure(go.Heatmap(z=corr.values, x=corr.columns, y=corr.index,
        colorscale=[[0, NEON_RED], [0.5, "#000000"], [1, NEON_GREEN]],
        text=corr.round(2).values, texttemplate="%{text}", zmin=-1, zmax=1,
        colorbar=dict(title="Corr")))
    return apply_layout(fig, "Correlation Matrix")

# ── MARKET HEATMAP ─────────────────────────────────────────────────────────────
def market_heatmap(df):
    if df.empty:
        return _no_data_figure("Market Heatmap (24h Change)", "Ticker data unavailable.", height=520)
    top = df.dropna(subset=["change_24_hour"]).nlargest(60, "volume")
    if top.empty:
        return _no_data_figure("Market Heatmap (24h Change)", "Not enough data to build heatmap.", height=520)
    fig = go.Figure(go.Treemap(
        labels=top["market"],
        parents=[""] * len(top),
        values=top["volume"].abs(),
        customdata=top["change_24_hour"].round(2),
        texttemplate="<b>%{label}</b><br>%{customdata}%",
        marker=dict(
            colors=top["change_24_hour"],
            colorscale=[[0, NEON_RED], [0.5, "#0A1628"], [1, NEON_GREEN]],
            cmid=0, cmin=-5, cmax=5,
            line=dict(color="#050A14", width=2)),
        hovertemplate="<b>%{label}</b><br>Change: %{customdata}%<br>Volume: %{value:,.0f}<extra></extra>"))
    return apply_layout(fig, "Market Heatmap (24h Change)")

# ── BOLLINGER BANDS ────────────────────────────────────────────────────────────
def bb_chart(df):
    if df.empty:
        return _no_data_figure("Bollinger Bands", "Candle data unavailable.")
    upper, mid, lower, width = bollinger_bands(df["close"])
    if upper.dropna().empty or lower.dropna().empty:
        return _no_data_figure("Bollinger Bands", "Need more candles to compute Bollinger Bands (period=20).")
    fig = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.3], shared_xaxes=True)
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=upper, line=dict(color="#4ECDC4", width=1, dash="dash"), name="Upper"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=mid, line=dict(color=NEON_YELLOW, width=1), name="Middle"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=lower, line=dict(color="#4ECDC4", width=1, dash="dash"),
        fill="tonexty", fillcolor="rgba(78,205,196,0.06)", name="Lower"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=width, line=dict(color=NEON_PURPLE, width=1.5), name="BB Width"), row=2, col=1)
    fig.update_layout(**CHART_LAYOUT, title=dict(text="Bollinger Bands", font=dict(color=NEON_BLUE, size=14)), height=600)
    return fig

# ── RSI ────────────────────────────────────────────────────────────────────────
def rsi_chart(df):
    if df.empty:
        return _no_data_figure("RSI Indicator", "Candle data unavailable.")
    r = rsi(df["close"])
    if r.dropna().empty:
        return _no_data_figure("RSI Indicator", "Need more candles to compute RSI (period=14).")
    fig = make_subplots(rows=2, cols=1, row_heights=[0.5, 0.5], shared_xaxes=True)
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=r, line=dict(color=NEON_PURPLE, width=1.5), name="RSI"), row=2, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,51,102,0.1)", line_width=0, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0,255,136,0.1)", line_width=0, row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color=NEON_RED, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color=NEON_GREEN, row=2, col=1)
    fig.update_layout(**CHART_LAYOUT, title=dict(text="RSI Indicator", font=dict(color=NEON_BLUE, size=14)), height=600)
    return fig

# ── RETURNS HISTOGRAM ──────────────────────────────────────────────────────────
def returns_histogram(df):
    if df.empty:
        return _no_data_figure("Return Distribution", "Candle data unavailable.", height=420)
    returns = df["close"].pct_change().dropna() * 100
    if returns.empty:
        return _no_data_figure("Return Distribution", "Not enough candles to compute returns.", height=420)
    fig = go.Figure(go.Histogram(x=returns, nbinsx=50, marker_color=NEON_BLUE, opacity=0.8,
        marker_line=dict(width=0.5, color=DARK_BG)))
    fig.add_vline(x=0, line_color=NEON_YELLOW, line_dash="dash")
    return apply_layout(fig, "Return Distribution")

# ── DRAWDOWN ───────────────────────────────────────────────────────────────────
def drawdown_chart(df):
    if df.empty:
        return _no_data_figure("Drawdown Chart", "Candle data unavailable.", height=420)
    returns = df["close"].pct_change().dropna()
    if returns.empty:
        return _no_data_figure("Drawdown Chart", "Not enough candles to compute drawdown.", height=420)
    dd = drawdown(returns)
    if pd.Series(dd).dropna().empty:
        return _no_data_figure("Drawdown Chart", "Not enough candles to compute drawdown.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"].iloc[1:], y=dd,
        fill="tozeroy", fillcolor="rgba(255,51,102,0.2)",
        line=dict(color=NEON_RED, width=1.5), name="Drawdown"))
    return apply_layout(fig, "Drawdown Chart")

# ── CUMULATIVE RETURNS ─────────────────────────────────────────────────────────
def cumulative_returns_chart(df):
    if df.empty:
        return _no_data_figure("Cumulative Returns %", "Candle data unavailable.", height=420)
    cum = ((1 + df["close"].pct_change()).cumprod() - 1) * 100
    if cum.dropna().empty:
        return _no_data_figure("Cumulative Returns %", "Not enough candles to compute cumulative returns.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=cum,
        fill="tozeroy", fillcolor="rgba(0,212,255,0.1)",
        line=dict(color=NEON_BLUE, width=2), name="Cumulative Returns"))
    return apply_layout(fig, "Cumulative Returns %")

# ── 3D CANDLESTICK SURFACE ─────────────────────────────────────────────────────
def price_surface_3d(df):
    if df.empty:
        return _no_data_figure("3D Price Surface", "Candle data unavailable.", height=520)
    n = min(len(df), 50)
    if n < 5:
        return _no_data_figure("3D Price Surface", "Need more candles for a 3D surface.", height=520)
    x = list(range(n))
    y = ["Open", "High", "Low", "Close"]
    z = [df["open"].tail(n).values, df["high"].tail(n).values,
         df["low"].tail(n).values, df["close"].tail(n).values]
    fig = go.Figure(go.Surface(x=x, y=[0,1,2,3], z=z,
        colorscale=[[0, NEON_RED], [0.5, NEON_BLUE], [1, NEON_GREEN]],
        opacity=0.85, showscale=True))
    fig.update_layout(**CHART_LAYOUT, scene=dict(
        xaxis=dict(title="Time", gridcolor=GRID_COLOR, backgroundcolor=CARD_BG),
        yaxis=dict(title="OHLC", tickvals=[0,1,2,3], ticktext=y, gridcolor=GRID_COLOR, backgroundcolor=CARD_BG),
        zaxis=dict(title="Price", gridcolor=GRID_COLOR, backgroundcolor=CARD_BG),
        bgcolor=DARK_BG),
        title=dict(text="3D Price Surface", font=dict(color=NEON_BLUE, size=14)), height=600)
    return fig

# ── 3D ORDER BOOK ──────────────────────────────────────────────────────────────
def orderbook_3d(bids, asks):
    if bids.empty or asks.empty:
        return _no_data_figure("3D Order Book", "Order book data unavailable.", height=520)
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=bids["price"], y=bids["quantity"], z=bids["quantity"].cumsum(),
        mode="lines+markers", line=dict(color=NEON_GREEN, width=3),
        marker=dict(size=3, color=NEON_GREEN), name="Bids"))
    fig.add_trace(go.Scatter3d(
        x=asks["price"], y=asks["quantity"], z=asks["quantity"].cumsum(),
        mode="lines+markers", line=dict(color=NEON_RED, width=3),
        marker=dict(size=3, color=NEON_RED), name="Asks"))
    fig.update_layout(**CHART_LAYOUT, scene=dict(
        xaxis_title="Price", yaxis_title="Qty", zaxis_title="Cumulative",
        bgcolor=DARK_BG),
        title=dict(text="3D Order Book", font=dict(color=NEON_BLUE, size=14)), height=600)
    return fig

# ── 3D VOLATILITY SURFACE ──────────────────────────────────────────────────────
def volatility_surface_3d(df):
    if df.empty:
        return _no_data_figure("3D Volatility Surface", "Candle data unavailable.", height=520)
    windows = [5, 10, 20, 30, 50]
    periods = list(range(min(len(df), 60)))
    z = []
    for w in windows:
        vol = df["close"].pct_change().rolling(w).std() * 100
        v = vol.dropna()
        z.append(v.tail(len(periods)).values if len(v) >= len(periods) else v.values)

    if not z or all(len(row) == 0 for row in z):
        return _no_data_figure("3D Volatility Surface", "Need more candles to compute rolling volatility.", height=520)
    min_len = min(len(row) for row in z)
    if min_len == 0:
        return _no_data_figure("3D Volatility Surface", "Need more candles to compute rolling volatility.", height=520)
    z = [row[:min_len] for row in z]
    fig = go.Figure(go.Surface(z=z, x=list(range(min_len)), y=windows,
        colorscale=[[0, NEON_BLUE], [0.5, NEON_YELLOW], [1, NEON_RED]],
        opacity=0.9, showscale=True))
    fig.update_layout(**CHART_LAYOUT, scene=dict(
        xaxis_title="Time", yaxis_title="Window", zaxis_title="Volatility %",
        bgcolor=DARK_BG),
        title=dict(text="3D Volatility Surface", font=dict(color=NEON_BLUE, size=14)), height=600)
    return fig

# ── 3D SCATTER TRADES ──────────────────────────────────────────────────────────
def trades_scatter_3d(trades):
    if trades.empty:
        return _no_data_figure("3D Trade Scatter", "Trade data unavailable.", height=520)
    if not {"price", "quantity"}.issubset(trades.columns):
        return _no_data_figure("3D Trade Scatter", "Trade payload missing price/quantity.", height=520)
    ts = trades.get("timestamp", pd.Series(range(len(trades))))
    ts_num = pd.to_numeric(ts, errors="coerce").fillna(0)
    colors = [NEON_GREEN if s == "buy" else NEON_RED for s in trades.get("side", ["buy"]*len(trades))]
    fig = go.Figure(go.Scatter3d(
        x=ts_num, y=trades["price"], z=trades["quantity"].fillna(0),
        mode="markers",
        marker=dict(size=4, color=colors, opacity=0.8, line=dict(width=0.5, color="white")),
        name="Trades"))
    fig.update_layout(**CHART_LAYOUT, scene=dict(
        xaxis_title="Time", yaxis_title="Price", zaxis_title="Quantity",
        bgcolor=DARK_BG),
        title=dict(text="3D Trade Scatter", font=dict(color=NEON_BLUE, size=14)), height=600)
    return fig

# ── MULTI-ASSET COMPARISON ─────────────────────────────────────────────────────
def multi_asset_comparison(price_dict):
    if not price_dict:
        return _no_data_figure("Multi-Asset Comparison (Normalized %)", "No assets selected.", height=420)
    fig = go.Figure()
    colors_pool = [NEON_BLUE, NEON_GREEN, NEON_RED, NEON_YELLOW, NEON_PURPLE, "#FF9F43"]
    for i, (name, prices) in enumerate(price_dict.items()):
        if hasattr(prices, "values"):
            normalized = (prices / prices.iloc[0] - 1) * 100
            fig.add_trace(go.Scatter(y=normalized, mode="lines",
                line=dict(color=colors_pool[i % len(colors_pool)], width=2), name=name))
    fig.update_layout(**CHART_LAYOUT, title=dict(text="Multi-Asset Comparison (Normalized %)", font=dict(color=NEON_BLUE, size=14)))
    return fig

# ── OBV ────────────────────────────────────────────────────────────────────────
def obv_chart(df):
    if df.empty:
        return _no_data_figure("On-Balance Volume", "Candle data unavailable.", height=420)
    if "volume" not in df.columns or df["volume"].fillna(0).sum() == 0:
        return _no_data_figure("On-Balance Volume", "Volume data unavailable for this interval.", height=420)
    from indicators import obv
    o = obv(df)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.5, 0.5])
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=o, line=dict(color=NEON_GREEN, width=1.5), name="OBV"), row=2, col=1)
    fig.update_layout(**CHART_LAYOUT, title=dict(text="On-Balance Volume", font=dict(color=NEON_BLUE, size=14)), height=500)
    return fig

# ── ROLLING VOLATILITY ─────────────────────────────────────────────────────────
def volatility_chart(df):
    if df.empty:
        return _no_data_figure("Rolling Volatility (Annualized %)", "Candle data unavailable.", height=420)
    vol = rolling_volatility(df["close"])
    if vol.dropna().empty:
        return _no_data_figure("Rolling Volatility (Annualized %)", "Need more candles to compute rolling volatility (period=20).", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=vol,
        fill="tozeroy", fillcolor="rgba(191,90,242,0.15)",
        line=dict(color=NEON_PURPLE, width=2), name="Volatility"))
    return apply_layout(fig, "Rolling Volatility (Annualized %)")

# ── Z-SCORE ────────────────────────────────────────────────────────────────────
def zscore_chart(df):
    if df.empty:
        return _no_data_figure("Z-Score Signal", "Candle data unavailable.", height=420)
    z = zscore(df["close"])
    if z.dropna().empty:
        return _no_data_figure("Z-Score Signal", "Need more candles to compute Z-Score (period=20).", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=z, line=dict(color=NEON_BLUE, width=1.5), name="Z-Score"))
    fig.add_hline(y=2, line_dash="dash", line_color=NEON_RED)
    fig.add_hline(y=-2, line_dash="dash", line_color=NEON_GREEN)
    fig.add_hrect(y0=-2, y1=2, fillcolor="rgba(0,212,255,0.05)", line_width=0)
    return apply_layout(fig, "Z-Score Signal")

# ── WILLIAMS %R ────────────────────────────────────────────────────────────────
def williams_r_chart(df):
    if df.empty:
        return _no_data_figure("Williams %R", "Candle data unavailable.", height=420)
    wr = williams_r(df)
    if wr.dropna().empty:
        return _no_data_figure("Williams %R", "Need more candles to compute Williams %R (period=14).", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=wr, line=dict(color=NEON_YELLOW, width=1.5), name="Williams %R"))
    fig.add_hline(y=-20, line_dash="dash", line_color=NEON_RED)
    fig.add_hline(y=-80, line_dash="dash", line_color=NEON_GREEN)
    return apply_layout(fig, "Williams %R")

# ── STOCHASTIC RSI ─────────────────────────────────────────────────────────────
def stoch_rsi_chart(df):
    if df.empty:
        return _no_data_figure("Stochastic RSI", "Candle data unavailable.", height=420)
    k, d = stochastic_rsi(df["close"])
    if k.dropna().empty and d.dropna().empty:
        return _no_data_figure("Stochastic RSI", "Need more candles to compute Stoch RSI.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=k, line=dict(color=NEON_BLUE, width=1.5), name="%K"))
    fig.add_trace(go.Scatter(x=df["time"], y=d, line=dict(color=NEON_RED, width=1.5), name="%D"))
    fig.add_hrect(y0=80, y1=100, fillcolor="rgba(255,51,102,0.1)", line_width=0)
    fig.add_hrect(y0=0, y1=20, fillcolor="rgba(0,255,136,0.1)", line_width=0)
    return apply_layout(fig, "Stochastic RSI")

# ── ROC ────────────────────────────────────────────────────────────────────────
def roc_chart(df):
    if df.empty:
        return _no_data_figure("Rate of Change", "Candle data unavailable.", height=420)
    r = roc(df["close"])
    if r.dropna().empty:
        return _no_data_figure("Rate of Change", "Need more candles to compute ROC (period=12).", height=420)
    colors = [NEON_GREEN if v >= 0 else NEON_RED for v in r.fillna(0)]
    fig = go.Figure(go.Bar(x=df["time"], y=r, marker_color=colors, name="ROC"))
    return apply_layout(fig, "Rate of Change")

# ── CCI ────────────────────────────────────────────────────────────────────────
def cci_chart(df):
    if df.empty:
        return _no_data_figure("CCI", "Candle data unavailable.", height=420)
    from indicators import cci
    c = cci(df)
    if c.dropna().empty:
        return _no_data_figure("CCI", "Need more candles to compute CCI.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=c, line=dict(color=NEON_BLUE, width=1.5), name="CCI"))
    fig.add_hline(y=100, line_dash="dash", line_color=NEON_RED)
    fig.add_hline(y=-100, line_dash="dash", line_color=NEON_GREEN)
    fig.add_hrect(y0=-100, y1=100, fillcolor="rgba(0,212,255,0.05)", line_width=0)
    return apply_layout(fig, "Commodity Channel Index (CCI)")

# ── MFI ────────────────────────────────────────────────────────────────────────
def mfi_chart(df):
    if df.empty:
        return _no_data_figure("MFI", "Candle data unavailable.", height=420)
    from indicators import mfi
    m = mfi(df)
    if m.dropna().empty:
        return _no_data_figure("MFI", "Need more candles to compute MFI.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=m, fill="tozeroy", fillcolor="rgba(191,90,242,0.15)",
        line=dict(color=NEON_PURPLE, width=1.5), name="MFI"))
    fig.add_hline(y=80, line_dash="dash", line_color=NEON_RED)
    fig.add_hline(y=20, line_dash="dash", line_color=NEON_GREEN)
    return apply_layout(fig, "Money Flow Index (MFI)")

# ── ADX ────────────────────────────────────────────────────────────────────────
def adx_chart(df):
    if df.empty:
        return _no_data_figure("ADX", "Candle data unavailable.", height=420)
    from indicators import adx
    a = adx(df)
    if a.dropna().empty:
        return _no_data_figure("ADX", "Need more candles to compute ADX.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=a, line=dict(color=NEON_YELLOW, width=1.5), name="ADX"))
    fig.add_hline(y=25, line_dash="dash", line_color=NEON_GREEN)
    fig.add_hline(y=50, line_dash="dash", line_color=NEON_RED)
    return apply_layout(fig, "Average Directional Index (ADX)")

# ── STOCHASTIC OSCILLATOR ───────────────────────────────────────────────────────
def stochastic_chart(df):
    if df.empty:
        return _no_data_figure("Stochastic Oscillator", "Candle data unavailable.", height=420)
    from indicators import stochastic
    k, d = stochastic(df)
    if k.dropna().empty:
        return _no_data_figure("Stochastic Oscillator", "Need more candles to compute Stochastic.", height=420)
    fig = make_subplots(rows=2, cols=1, row_heights=[0.6, 0.4], shared_xaxes=True)
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=k, line=dict(color=NEON_GREEN, width=1.5), name="%K"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=d, line=dict(color=NEON_RED, width=1.5), name="%D"), row=2, col=1)
    fig.add_hrect(y0=80, y1=100, fillcolor="rgba(255,51,102,0.1)", line_width=0, row=2, col=1)
    fig.add_hrect(y0=0, y1=20, fillcolor="rgba(0,255,136,0.1)", line_width=0, row=2, col=1)
    fig.update_layout(**CHART_LAYOUT, title=dict(text="Stochastic Oscillator", font=dict(color=NEON_BLUE, size=14)), height=550)
    return fig

# ── ICHIMOKU ────────────────────────────────────────────────────────────────────
def ichimoku_chart(df):
    if df.empty:
        return _no_data_figure("Ichimoku Cloud", "Candle data unavailable.", height=500)
    from indicators import ichimoku
    try:
        tenkan, kijun, senkou_a, senkou_b, chikou = ichimoku(df)
        if tenkan.dropna().empty:
            return _no_data_figure("Ichimoku Cloud", "Need more candles to compute Ichimoku.", height=500)
    except:
        return _no_data_figure("Ichimoku Cloud", "Not enough data.", height=500)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"))
    fig.add_trace(go.Scatter(x=df["time"], y=tenkan, line=dict(color=NEON_GREEN, width=1), name="Tenkan-Sen"))
    fig.add_trace(go.Scatter(x=df["time"], y=kijun, line=dict(color=NEON_RED, width=1), name="Kijun-Sen"))
    fig.add_trace(go.Scatter(x=df["time"], y=senkou_a, fill="tonexty", fillcolor="rgba(0,255,136,0.1)",
        line=dict(width=0), name="Senkou A", opacity=0.7))
    fig.add_trace(go.Scatter(x=df["time"], y=senkou_b, fill="tonexty", fillcolor="rgba(255,51,102,0.1)",
        line=dict(width=0), name="Senkou B", opacity=0.7))
    return apply_layout(fig, "Ichimoku Cloud")

# ── PIVOT POINTS ────────────────────────────────────────────────────────────────
def pivot_chart(df):
    if df.empty:
        return _no_data_figure("Pivot Points", "Candle data unavailable.", height=420)
    from indicators import pivot_points
    try:
        pivot, r1, r2, r3, s1, s2, s3 = pivot_points(df)
        if pivot.dropna().empty:
            return _no_data_figure("Pivot Points", "Need more candles.", height=420)
    except:
        return _no_data_figure("Pivot Points", "Not enough data.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"))
    fig.add_trace(go.Scatter(x=df["time"], y=r1, line=dict(color=NEON_RED, width=1, dash="dot"), name="R1"))
    fig.add_trace(go.Scatter(x=df["time"], y=r2, line=dict(color=NEON_RED, width=1, dash="dot"), name="R2"))
    fig.add_trace(go.Scatter(x=df["time"], y=s1, line=dict(color=NEON_GREEN, width=1, dash="dot"), name="S1"))
    fig.add_trace(go.Scatter(x=df["time"], y=s2, line=dict(color=NEON_GREEN, width=1, dash="dot"), name="S2"))
    return apply_layout(fig, "Pivot Points")

# ── FIBONACCI RETRACEMENT ──────────────────────────────────────────────────────
def fibonacci_chart(df):
    if df.empty:
        return _no_data_figure("Fibonacci Retracement", "Candle data unavailable.", height=420)
    from indicators import fibonacci_retracement
    try:
        levels = fibonacci_retracement(df)
    except:
        return _no_data_figure("Fibonacci Retracement", "Not enough data.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"))
    colors = ["#FF9F43", "#F39C12", "#F1C40F", "#2ECC71", "#E74C3C"]
    names = ["23.6%", "38.2%", "50%", "61.8%", "78.6%"]
    for i, (level, color, name) in enumerate(zip(levels, colors, names)):
        fig.add_hline(y=level, line_dash="dash", line_color=color, name=name)
    return apply_layout(fig, "Fibonacci Retracements")

# ── EASE OF MOVEMENT ───────────────────────────────────────────────────────────
def ease_of_movement_chart(df):
    if df.empty:
        return _no_data_figure("Ease of Movement", "Candle data unavailable.", height=420)
    from indicators import ease_of_movement
    eom = ease_of_movement(df)
    if eom.dropna().empty:
        return _no_data_figure("Ease of Movement", "Not enough candles.", height=420)
    colors = [NEON_GREEN if v >= 0 else NEON_RED for v in eom.fillna(0)]
    fig = go.Figure(go.Bar(x=df["time"], y=eom, marker_color=colors, name="EOM"))
    return apply_layout(fig, "Ease of Movement")

# ── FORCE INDEX ────────────────────────────────────────────────────────────────
def force_index_chart(df):
    if df.empty:
        return _no_data_figure("Force Index", "Candle data unavailable.", height=420)
    from indicators import force_index
    fi = force_index(df)
    if fi.dropna().empty:
        return _no_data_figure("Force Index", "Not enough candles.", height=420)
    colors = [NEON_GREEN if v >= 0 else NEON_RED for v in fi.fillna(0)]
    fig = go.Figure(go.Bar(x=df["time"], y=fi, marker_color=colors, name="Force Index"))
    return apply_layout(fig, "Force Index")

# ── MASS INDEX ────────────────────────────────────────────────────────────────
def mass_index_chart(df):
    if df.empty:
        return _no_data_figure("Mass Index", "Candle data unavailable.", height=420)
    from indicators import mass_index
    mi = mass_index(df)
    if mi.dropna().empty:
        return _no_data_figure("Mass Index", "Not enough candles.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=mi, line=dict(color=NEON_PURPLE, width=1.5), name="Mass Index"))
    fig.add_hline(y=27, line_dash="dash", line_color=NEON_RED)
    fig.add_hline(y=26.5, line_dash="dash", line_color=NEON_GREEN)
    return apply_layout(fig, "Mass Index")

# ── KST ────────────────────────────────────────────────────────────────────────
def kst_chart(df):
    if df.empty:
        return _no_data_figure("KST", "Candle data unavailable.", height=420)
    from indicators import kst
    kst_val, signal = kst(df["close"])
    if kst_val.dropna().empty:
        return _no_data_figure("KST", "Not enough candles.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=kst_val, line=dict(color=NEON_BLUE, width=1.5), name="KST"))
    fig.add_trace(go.Scatter(x=df["time"], y=signal, line=dict(color=NEON_RED, width=1), name="Signal"))
    return apply_layout(fig, "Know Sure Thing (KST)")

# ── SUPERTREND ────────────────────────────────────────────────────────────────
def supertrend_chart(df):
    if df.empty:
        return _no_data_figure("Supertrend", "Candle data unavailable.", height=450)
    from indicators import supertrend
    try:
        upper, lower, in_uptrend = supertrend(df)
        if upper.dropna().empty:
            return _no_data_figure("Supertrend", "Not enough candles.", height=450)
    except:
        return _no_data_figure("Supertrend", "Not enough data.", height=450)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"))
    fig.add_trace(go.Scatter(x=df["time"], y=upper, line=dict(color=NEON_GREEN, width=1, dash="dot"), name="Upper"))
    fig.add_trace(go.Scatter(x=df["time"], y=lower, line=dict(color=NEON_RED, width=1, dash="dot"), name="Lower"))
    return apply_layout(fig, "Supertrend")

# ── REALIZED VOLATILITY ───────────────────────────────────────────────────────
def realized_volatility_chart(df):
    if df.empty:
        return _no_data_figure("Realized Volatility", "Candle data unavailable.", height=420)
    from indicators import realized_volatility
    rv = realized_volatility(df["close"])
    if rv.dropna().empty:
        return _no_data_figure("Realized Volatility", "Not enough candles.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=rv, fill="tozeroy", fillcolor="rgba(255,215,0,0.15)",
        line=dict(color=NEON_YELLOW, width=2), name="RV"))
    return apply_layout(fig, "Realized Volatility (%)")

# ── MOMENTUM ─────────────────────────────────────────────────────────────────
def momentum_chart(df):
    if df.empty:
        return _no_data_figure("Momentum", "Candle data unavailable.", height=420)
    from indicators import momentum
    m = momentum(df["close"])
    if m.dropna().empty:
        return _no_data_figure("Momentum", "Not enough candles.", height=420)
    colors = [NEON_GREEN if v >= 0 else NEON_RED for v in m.fillna(0)]
    fig = go.Figure(go.Bar(x=df["time"], y=m, marker_color=colors, name="Momentum"))
    return apply_layout(fig, "Momentum")

# ── TSI ────────────────────────────────────────────────────────────────────────
def tsi_chart(df):
    if df.empty:
        return _no_data_figure("TSI", "Candle data unavailable.", height=420)
    from indicators import tsi
    tsi_val, signal = tsi(df["close"])
    if tsi_val.dropna().empty:
        return _no_data_figure("TSI", "Not enough candles.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=tsi_val, line=dict(color=NEON_BLUE, width=1.5), name="TSI"))
    fig.add_trace(go.Scatter(x=df["time"], y=signal, line=dict(color=NEON_RED, width=1), name="Signal"))
    return apply_layout(fig, "True Strength Index (TSI)")

# ── ULCER INDEX ───────────────────────────────────────────────────────────────
def ulcer_index_chart(df):
    if df.empty:
        return _no_data_figure("Ulcer Index", "Candle data unavailable.", height=420)
    from indicators import ulcer_index
    ui = ulcer_index(df["close"])
    if ui.dropna().empty:
        return _no_data_figure("Ulcer Index", "Not enough candles.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"].iloc[1:], y=ui, line=dict(color=NEON_PURPLE, width=1.5), name="UI"))
    return apply_layout(fig, "Ulcer Index")

# ── KAMA ────────────────────────────────────────────────────────────────────────
def kama_chart(df):
    if df.empty:
        return _no_data_figure("KAMA", "Candle data unavailable.", height=420)
    from indicators import kama
    k = kama(df["close"])
    if k.dropna().empty:
        return _no_data_figure("KAMA", "Not enough candles.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color="#6B8BB0", width=1), name="Price"))
    fig.add_trace(go.Scatter(x=df["time"], y=k, line=dict(color=NEON_GREEN, width=1.5), name="KAMA"))
    return apply_layout(fig, "Kaufman Adaptive MA")

# ── ELDER RAY ─────────────────────────────────────────────────────────────────
def elder_ray_chart(df):
    if df.empty:
        return _no_data_figure("Elder-Ray", "Candle data unavailable.", height=420)
    from indicators import elder_ray
    bull, bear = elder_ray(df)
    if bull.dropna().empty:
        return _no_data_figure("Elder-Ray", "Not enough candles.", height=420)
    fig = make_subplots(rows=2, cols=1, row_heights=[0.6, 0.4], shared_xaxes=True)
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color=NEON_BLUE, width=1.5), name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=bull, line=dict(color=NEON_GREEN, width=1.5), name="Bull Power"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=bear, line=dict(color=NEON_RED, width=1.5), name="Bear Power"), row=2, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="#6B8BB0", row=2, col=1)
    fig.update_layout(**CHART_LAYOUT, title=dict(text="Elder-Ray", font=dict(color=NEON_BLUE, size=14)), height=550)
    return fig

# ── VORTEX ────────────────────────────────────────────────────────────────────
def vortex_chart(df):
    if df.empty:
        return _no_data_figure("Vortex", "Candle data unavailable.", height=420)
    from indicators import vortex
    vi_plus, vi_minus = vortex(df)
    if vi_plus.dropna().empty:
        return _no_data_figure("Vortex", "Not enough candles.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=vi_plus, line=dict(color=NEON_GREEN, width=1.5), name="VI+"))
    fig.add_trace(go.Scatter(x=df["time"], y=vi_minus, line=dict(color=NEON_RED, width=1.5), name="VI-"))
    return apply_layout(fig, "Vortex Indicator")

# ── AROON ─────────────────────────────────────────────────────────────────────
def aroon_chart(df):
    if df.empty:
        return _no_data_figure("Aroon", "Candle data unavailable.", height=420)
    from indicators import aroon
    aroon_up, aroon_down = aroon(df)
    if aroon_up.dropna().empty:
        return _no_data_figure("Aroon", "Not enough candles.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=aroon_up, line=dict(color=NEON_GREEN, width=1.5), name="Aroon Up"))
    fig.add_trace(go.Scatter(x=df["time"], y=aroon_down, line=dict(color=NEON_RED, width=1.5), name="Aroon Down"))
    return apply_layout(fig, "Aroon Indicator")

# ── COPP CURVE ───────────────────────────────────────────────────────────────
def copp_curve_chart(df):
    if df.empty:
        return _no_data_figure("Copp Curve", "Candle data unavailable.", height=420)
    from indicators import copp
    cp = copp(df["close"])
    if cp.dropna().empty:
        return _no_data_figure("Copp Curve", "Not enough candles.", height=420)
    colors = [NEON_GREEN if v >= 0 else NEON_RED for v in cp.fillna(0)]
    fig = go.Figure(go.Bar(x=df["time"], y=cp, marker_color=colors, name="Copp"))
    return apply_layout(fig, "Copp Curve")

# ── VWAP BANDWIDTH ───────────────────────────────────────────────────────────
def vwap_bandwidth_chart(df):
    if df.empty:
        return _no_data_figure("VWAP Bandwidth", "Candle data unavailable.", height=420)
    from indicators import vwap_bands
    try:
        upper, mid, lower = vwap_bands(df)
        if mid.dropna().empty:
            return _no_data_figure("VWAP Bandwidth", "Not enough candles.", height=420)
    except:
        return _no_data_figure("VWAP Bandwidth", "Not enough data.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color="#6B8BB0", width=1), name="Price"))
    fig.add_trace(go.Scatter(x=df["time"], y=upper, line=dict(color=NEON_RED, width=1, dash="dot"), name="Upper"))
    fig.add_trace(go.Scatter(x=df["time"], y=mid, line=dict(color=NEON_YELLOW, width=1.5), name="VWAP"))
    fig.add_trace(go.Scatter(x=df["time"], y=lower, line=dict(color=NEON_GREEN, width=1, dash="dot"), name="Lower"))
    return apply_layout(fig, "VWAP Bands")

# ── KELTNER WIDTH ────────────────────────────────────────────────────────────
def keltner_width_chart(df):
    if df.empty:
        return _no_data_figure("Keltner Width", "Candle data unavailable.", height=420)
    from indicators import keltner_width
    kw = keltner_width(df)
    if kw.dropna().empty:
        return _no_data_figure("Keltner Width", "Not enough candles.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=kw, fill="tozeroy", fillcolor="rgba(78,205,196,0.15)",
        line=dict(color="#4ECDC4", width=1.5), name="Keltner Width"))
    return apply_layout(fig, "Keltner Channel Width (%)")

# ── MONEY FLOW VOLUME ───────────────────────────────────────────────────────
def money_flow_volume_chart(df):
    if df.empty:
        return _no_data_figure("Money Flow Volume", "Candle data unavailable.", height=420)
    from indicators import money_flow_volume
    mfv = money_flow_volume(df)
    if mfv.dropna().empty:
        return _no_data_figure("Money Flow Volume", "Not enough candles.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=mfv, fill="tozeroy", fillcolor="rgba(255,159,67,0.15)",
        line=dict(color="#FF9F43", width=1.5), name="MFV"))
    return apply_layout(fig, "Money Flow Volume")

# ── PRICE VOLUME TREND ───────────────────────────────────────────────────────
def pvt_chart(df):
    if df.empty:
        return _no_data_figure("PVT", "Candle data unavailable.", height=420)
    from indicators import price_volume_trend
    pvt = price_volume_trend(df)
    if pvt.dropna().empty:
        return _no_data_figure("PVT", "Not enough candles.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=pvt, line=dict(color=NEON_BLUE, width=1.5), name="PVT"))
    return apply_layout(fig, "Price Volume Trend")

# ── AROON OSCILLATOR ────────────────────────────────────────────────────────
def aroon_oscillator_chart(df):
    if df.empty:
        return _no_data_figure("Aroon Oscillator", "Candle data unavailable.", height=420)
    from indicators import aroon
    aroon_up, aroon_down = aroon(df)
    osc = aroon_up - aroon_down
    if osc.dropna().empty:
        return _no_data_figure("Aroon Oscillator", "Not enough candles.", height=420)
    colors = [NEON_GREEN if v >= 0 else NEON_RED for v in osc.fillna(0)]
    fig = go.Figure(go.Bar(x=df["time"], y=osc, marker_color=colors, name="Aroon Osc"))
    return apply_layout(fig, "Aroon Oscillator")

# ── TREND INTENSITY ───────────────────────────────────────────────────────────
def trend_intensity_chart(df):
    if df.empty:
        return _no_data_figure("Trend Intensity", "Candle data unavailable.", height=420)
    from indicators import trend_intensity
    ti = pd.Series(trend_intensity(df["close"]))
    if ti.dropna().empty:
        return _no_data_figure("Trend Intensity", "Not enough candles.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=ti, fill="tozeroy", fillcolor="rgba(155,89,182,0.15)",
        line=dict(color=NEON_PURPLE, width=1.5), name="Trend Intensity"))
    fig.add_hline(y=50, line_dash="dash", line_color=NEON_YELLOW)
    return apply_layout(fig, "Trend Intensity (%)")

# ── DPO ───────────────────────────────────────────────────────────────────────
def dpo_chart(df):
    if df.empty:
        return _no_data_figure("DPO", "Candle data unavailable.", height=420)
    from indicators import dpo
    d = dpo(df["close"])
    if d.dropna().empty:
        return _no_data_figure("DPO", "Not enough candles.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=d, line=dict(color=NEON_BLUE, width=1.5), name="DPO"))
    return apply_layout(fig, "Detrended Price Oscillator")

# ── NATURAL LOG RETURNS ──────────────────────────────────────────────────────
def log_returns_chart(df):
    if df.empty:
        return _no_data_figure("Log Returns", "Candle data unavailable.", height=420)
    from indicators import log_returns
    lr = log_returns(df["close"])
    if lr.dropna().empty:
        return _no_data_figure("Log Returns", "Not enough candles.", height=420)
    colors = [NEON_GREEN if v >= 0 else NEON_RED for v in lr.fillna(0)]
    fig = go.Figure(go.Bar(x=df["time"], y=lr, marker_color=colors, name="Log Returns"))
    return apply_layout(fig, "Log Returns (%)")

# ── ARNUX LEGAUX ──────────────────────────────────────────────────────────────
def Arnaud_Legaux_chart(df):
    if df.empty:
        return _no_data_figure("Arnaud Legaux", "Candle data unavailable.", height=420)
    from indicators import Arnaud_Legaux
    al = Arnaud_Legaux(df)
    if al.dropna().empty:
        return _no_data_figure("Arnaud Legaux", "Not enough candles.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=al, line=dict(color=NEON_YELLOW, width=1.5), name="AL"))
    return apply_layout(fig, "Arnaud Legaux")

# ── KELTNER CHANNEL WITH FILLED AREA ────────────────────────────────────────
def keltner_filled_chart(df):
    if df.empty:
        return _no_data_figure("Keltner Channel", "Candle data unavailable.", height=450)
    from indicators import keltner
    try:
        upper, mid, lower = keltner(df)
        if mid.dropna().empty:
            return _no_data_figure("Keltner Channel", "Not enough candles.", height=450)
    except:
        return _no_data_figure("Keltner Channel", "Not enough data.", height=450)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color="#6B8BB0", width=1), name="Price"))
    fig.add_trace(go.Scatter(x=df["time"], y=upper, fill="tonexty", fillcolor="rgba(255,51,102,0.08)",
        line=dict(color=NEON_RED, width=1), name="Upper"))
    fig.add_trace(go.Scatter(x=df["time"], y=lower, fill="tonexty", fillcolor="rgba(0,255,136,0.08)",
        line=dict(color=NEON_GREEN, width=1), name="Lower"))
    fig.add_trace(go.Scatter(x=df["time"], y=mid, line=dict(color=NEON_BLUE, width=1.5, dash="dot"), name="Mid"))
    return apply_layout(fig, "Keltner Channel (Filled)")

# ── MULTI TIMEFRAME SMA ──────────────────────────────────────────────────────
def multi_sma_chart(df):
    if df.empty:
        return _no_data_figure("Multi SMA", "Candle data unavailable.", height=450)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df["time"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color=NEON_GREEN, decreasing_line_color=NEON_RED, name="Price"))
    for period, color in [(20, NEON_YELLOW), (50, NEON_PURPLE), (100, NEON_BLUE), (200, "#FF9F43")]:
        sma_val = sma(df["close"], period)
        fig.add_trace(go.Scatter(x=df["time"], y=sma_val, line=dict(color=color, width=1), name=f"SMA{period}"))
    return apply_layout(fig, "Multiple SMA")

# ── MULTI TIMEFRAME EMA ──────────────────────────────────────────────────────
def multi_ema_chart(df):
    if df.empty:
        return _no_data_figure("Multi EMA", "Candle data unavailable.", height=450)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df["time"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color=NEON_GREEN, decreasing_line_color=NEON_RED, name="Price"))
    for period, color in [(9, NEON_GREEN), (21, NEON_BLUE), (55, NEON_RED), (100, NEON_YELLOW)]:
        ema_val = ema(df["close"], period)
        fig.add_trace(go.Scatter(x=df["time"], y=ema_val, line=dict(color=color, width=1), name=f"EMA{period}"))
    return apply_layout(fig, "Multiple EMA")

# ── HULL MA VARIANT ───────────────────────────────────────────────────────────
def hull_ma_chart(df):
    if df.empty:
        return _no_data_figure("Hull MA", "Candle data unavailable.", height=420)
    from indicators import hull_ma as hma
    h = hma(df["close"], 20)
    if h.dropna().empty:
        return _no_data_figure("Hull MA", "Not enough candles.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color="#6B8BB0", width=1), name="Price"))
    fig.add_trace(go.Scatter(x=df["time"], y=h, line=dict(color=NEON_GREEN, width=2), name="Hull MA"))
    return apply_layout(fig, "Hull Moving Average")

# ── WMA CHART ────────────────────────────────────────────────────────────────
def wma_chart(df):
    if df.empty:
        return _no_data_figure("WMA", "Candle data unavailable.", height=420)
    from indicators import wma
    w = wma(df["close"], 20)
    if w.dropna().empty:
        return _no_data_figure("WMA", "Not enough candles.", height=420)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color="#6B8BB0", width=1), name="Price"))
    fig.add_trace(go.Scatter(x=df["time"], y=w, line=dict(color=NEON_PURPLE, width=1.5), name="WMA"))
    return apply_layout(fig, "Weighted Moving Average")

# ── ACCUMULATION DISTRIBUTION ─────────────────────────────────────────────────
def accum_dist_chart(df):
    if df.empty:
        return _no_data_figure("A/D Line", "Candle data unavailable.", height=420)
    from indicators import accum_dist
    ad = accum_dist(df)
    if ad.dropna().empty:
        return _no_data_figure("A/D Line", "Not enough candles.", height=420)
    fig = go.Figure(go.Scatter(x=df["time"], y=ad, fill="tozeroy", fillcolor="rgba(0,212,255,0.15)",
        line=dict(color=NEON_BLUE, width=1.5), name="A/D"))
    return apply_layout(fig, "Accumulation/Distribution")

# ── DONCHIAN CHANNEL FILLED ──────────────────────────────────────────────────
def donchian_filled_chart(df):
    if df.empty:
        return _no_data_figure("Donchian Channel", "Candle data unavailable.", height=450)
    from indicators import donchian
    upper, lower = donchian(df, 20)
    if upper.dropna().empty:
        return _no_data_figure("Donchian Channel", "Not enough candles.", height=450)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], line=dict(color="#6B8BB0", width=1), name="Price"))
    fig.add_trace(go.Scatter(x=df["time"], y=upper, fill="tonexty", fillcolor="rgba(255,51,102,0.1)",
        line=dict(color=NEON_RED, width=1), name="Upper"))
    fig.add_trace(go.Scatter(x=df["time"], y=lower, fill="tonexty", fillcolor="rgba(0,255,136,0.1)",
        line=dict(color=NEON_GREEN, width=1), name="Lower"))
    return apply_layout(fig, "Donchian Channel (Filled)")
