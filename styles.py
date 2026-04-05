TERMINAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');

:root {
    --bg: #050A14;
    --card: #0A1628;
    --card2: #0D1F3C;
    --blue: #00D4FF;
    --green: #00FF88;
    --red: #FF3366;
    --yellow: #FFD700;
    --purple: #BF5AF2;
    --orange: #FF9F43;
    --text: #C8D8F0;
    --text-muted: #6B8BB0;
    --border: rgba(0,212,255,0.15);
    --glow: 0 0 20px rgba(0,212,255,0.3);
}

html, body, [data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08111F 0%, #050A14 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* Headers */
h1, h2, h3 { font-family: 'Orbitron', monospace !important; }

/* Glass Cards */
.glass-card {
    background: rgba(10,22,40,0.85);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 16px;
    transition: all 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(0,212,255,0.35);
    box-shadow: var(--glow), 0 4px 24px rgba(0,0,0,0.4);
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(135deg, rgba(10,22,40,0.95) 0%, rgba(13,31,60,0.95) 100%);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--blue), transparent);
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--glow);
}
.metric-label { color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.metric-value { font-size: 1.4rem; font-weight: 700; font-family: 'Orbitron', monospace; }
.metric-sub { font-size: 0.75rem; color: var(--text-muted); margin-top: 4px; }
.positive { color: var(--green) !important; }
.negative { color: var(--red) !important; }
.neutral { color: var(--blue) !important; }

/* Header Banner */
.terminal-header {
    background: linear-gradient(135deg, #050A14 0%, #0A1628 50%, #050A14 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.terminal-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--blue), var(--green), var(--purple), var(--blue));
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
}
@keyframes shimmer {
    0% { background-position: 0% 0%; }
    100% { background-position: 200% 0%; }
}
.terminal-title {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 900;
    background: linear-gradient(90deg, var(--blue), var(--green));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.terminal-subtitle {
    color: var(--text-muted);
    font-size: 0.8rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* Latency badge */
.latency-badge {
    display: inline-block;
    padding: 3px 10px;
    background: rgba(0,255,136,0.1);
    border: 1px solid rgba(0,255,136,0.3);
    border-radius: 20px;
    color: var(--green);
    font-size: 0.7rem;
    font-weight: 600;
}
.latency-badge.warn { background: rgba(255,163,51,0.1); border-color: rgba(255,163,51,0.3); color: var(--orange); }
.latency-badge.danger { background: rgba(255,51,102,0.1); border-color: rgba(255,51,102,0.3); color: var(--red); }

/* Alert cards */
.alert-triggered {
    background: rgba(255,51,102,0.1);
    border: 1px solid rgba(255,51,102,0.5);
    border-radius: 8px;
    padding: 12px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,51,102,0.4); }
    50% { box-shadow: 0 0 0 8px rgba(255,51,102,0); }
}

/* Select boxes, inputs */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: var(--card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {
    border-color: var(--blue) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(0,255,136,0.1)) !important;
    border: 1px solid var(--blue) !important;
    color: var(--blue) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,212,255,0.25), rgba(0,255,136,0.25)) !important;
    box-shadow: var(--glow) !important;
    transform: translateY(-1px) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card) !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,212,255,0.15) !important;
    color: var(--blue) !important;
    box-shadow: 0 0 10px rgba(0,212,255,0.2) !important;
}

/* DataFrames */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px !important; overflow: hidden; }

/* Section labels */
.section-label {
    color: var(--blue);
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
}

/* Footer */
.terminal-footer {
    text-align: center;
    padding: 20px;
    border-top: 1px solid var(--border);
    margin-top: 40px;
    color: var(--text-muted);
    font-size: 0.8rem;
}
.footer-link {
    color: var(--blue);
    text-decoration: none;
    margin: 0 8px;
    transition: color 0.2s;
}
.footer-link:hover { color: var(--green); }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.4); }

/* Sidebar nav */
.nav-item {
    padding: 10px 16px;
    border-radius: 8px;
    margin: 2px 0;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
    font-size: 0.85rem;
}
.nav-item:hover {
    background: rgba(0,212,255,0.08);
    border-color: var(--border);
}
.nav-item.active {
    background: rgba(0,212,255,0.12);
    border-color: var(--border);
    color: var(--blue);
}

/* Trade tape */
.trade-buy { color: var(--green); }
.trade-sell { color: var(--red); }
.trade-row { padding: 3px 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.78rem; }

/* Loading */
[data-testid="stSpinner"] { color: var(--blue) !important; }

/* Expander */
.streamlit-expanderHeader {
    background: var(--card2) !important;
    border-radius: 8px !important;
}

/* Hide default Streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
"""
