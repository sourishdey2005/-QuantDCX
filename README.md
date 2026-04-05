# ⚡ QuantDCX Terminal

A **production-grade Bloomberg Terminal / TradingView hybrid** for real-time cryptocurrency market analytics, powered by CoinDCX public APIs.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
cd quantdcx
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## 📁 Project Structure

```
quantdcx/
├── app.py                  # Main Streamlit application
├── requirements.txt
├── modules/
│   ├── __init__.py
│   ├── api.py              # CoinDCX API functions
│   ├── indicators.py       # Technical indicators (RSI, MACD, BB, etc.)
│   ├── charts.py           # All 2D + 3D Plotly charts
│   ├── portfolio.py        # Portfolio optimizer + efficient frontier
│   └── styles.py           # Terminal dark theme CSS
```

---

## 🧩 Features

### 📊 9 Navigation Sections
| Page | Description |
|------|-------------|
| **Dashboard** | Live overview, top gainers/losers, candlestick |
| **Market Analysis** | 12 chart types: Candle, HA, MACD, BB, RSI, Stoch, OBV... |
| **Order Book** | Depth chart, bid/ask heatmap, 3D order book |
| **Trade Flow** | Bubble chart, buy/sell pressure, live tape |
| **Portfolio** | Simulator with PnL, allocation pie, efficient frontier |
| **Advanced Analytics** | Drawdown, cumulative returns, 3D surfaces |
| **Multi-Compare** | Up to 6 assets, correlation matrix, 3D correlation |
| **Market Heatmap** | Treemap of entire market by 24h change |
| **Alert System** | Price threshold alerts with visual triggers |

### 📈 Visualizations Included
- Candlestick, Heikin Ashi, OHLC, Area charts
- SMA (20/50/200), EMA, Hull MA, VWAP, WMA
- RSI, Stochastic RSI, MACD, Williams %R, ROC
- Bollinger Bands, Keltner Channels, Donchian Channels
- Volume Profile (VPVR), OBV, Chaikin Money Flow
- Returns Histogram, Drawdown, Cumulative Returns, Z-Score
- Rolling Volatility, ATR
- **3D:** Price Surface, Volatility Surface, Order Book, Trade Scatter, Correlation
- Correlation Matrix Heatmap, Market Treemap

### 🔌 APIs Used
- `GET /exchange/ticker` — Live ticker data
- `GET /exchange/v1/markets` — All trading pairs  
- `GET /market_data/candles` — OHLCV candle data
- `GET /market_data/orderbook` — Order book
- `GET /market_data/trade_history` — Recent trades

---

## ⚙️ Configuration

In the sidebar:
- **Trading Pair**: 100+ pairs available
- **Interval**: 1m, 5m, 15m, 1h, 4h, 1d
- **Visualization Mode**: 2D Standard | 2D Advanced | 3D Advanced
- **Refresh Rate**: 2–30 seconds
- **Auto Refresh**: Toggle live updates

---

## 🎨 Design

- **Theme**: Neon-on-black terminal aesthetic
- **Fonts**: Orbitron (headers) + JetBrains Mono (body)
- **Colors**: Deep black background + neon blue/green accents
- **Effects**: Glassmorphism cards, gradient shimmer header, hover glows
- **Inspired by**: Bloomberg Terminal × TradingView

---

## 🧮 Portfolio Optimizer

Uses `scipy.optimize.minimize` with:
- **Max Sharpe Ratio** optimization
- **Min Variance** optimization  
- **Efficient Frontier** curve generation

---

Made with ❤️ by **Sourish Dey**

[![GitHub](https://img.shields.io/badge/GitHub-sourishdey-blue)](https://github.com/sourishdey)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-sourishdey-blue)](https://linkedin.com/in/sourishdey)
