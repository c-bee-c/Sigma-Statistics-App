import numpy as np

import matplotlib.pyplot as plt

import streamlit as st

 

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(

    page_title="Six Sigma Process Explorer",

    page_icon="📊",

    layout="wide",

    initial_sidebar_state="expanded",

)

 

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""

<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Barlow+Condensed:wght@700;900&family=Barlow:wght@300;400;500;600&display=swap');

 

html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }

 

/* Dark background */

.stApp { background-color: #04080F; color: #F0F6FF; }

 

/* Sidebar */

[data-testid="stSidebar"] {

  background-color: #080E1A !important;

  border-right: 1px solid #1A2E48;

}

[data-testid="stSidebar"] * { color: #F0F6FF !important; }

 

/* Slider handle */

[data-testid="stSlider"] > div > div > div > div { background: #0D9488 !important; }

 

/* Radio buttons */

[data-testid="stRadio"] label { color: #94A3B8 !important; font-size: 13px !important; }

[data-testid="stRadio"] label:hover { color: #F0F6FF !important; }

 

/* Metric cards */

[data-testid="metric-container"] {

  background: #080E1A;

  border: 1px solid #1A2E48;

  border-radius: 8px;

  padding: 12px 16px !important;

}

[data-testid="stMetricValue"] { color: #F0F6FF !important; font-family: 'DM Mono', monospace !important; }

[data-testid="stMetricLabel"] { color: #64748B !important; font-size: 11px !important; }

 

/* Header */

.app-header {

  background: #080E1A;

  border-bottom: 1px solid #1A2E48;

  padding: 16px 24px;

  margin: -1rem -1rem 1.5rem -1rem;

  display: flex;

  justify-content: space-between;

  align-items: center;

}

.app-title {

  font-family: 'Barlow Condensed', sans-serif;

  font-size: 22px;

  font-weight: 900;

  letter-spacing: 0.06em;

  text-transform: uppercase;

  color: #F0F6FF;

}

.app-subtitle { font-size: 12px; color: #64748B; margin-top: 2px; letter-spacing: 0.04em; }

 

/* Badges and boxes */

.sigma-badge {

  font-family: 'DM Mono', monospace;

  font-size: 44px;

  font-weight: 500;

  line-height: 1;

  text-align: right;

}

.sigma-sub { font-size: 13px; color: #64748B; margin-top: 3px; }

 

.section-header {

  font-family: 'Barlow Condensed', sans-serif;

  font-size: 11px;

  font-weight: 700;

  letter-spacing: 0.12em;

  text-transform: uppercase;

  color: #0D9488;

  margin-bottom: 10px;

  margin-top: 4px;

}

 

.verdict-box { border-radius: 8px; padding: 14px 16px; margin-top: 8px; }

.info-box {

  background: rgba(13,148,136,0.07);

  border: 1px solid rgba(13,148,136,0.25);

  border-radius: 8px;

  padding: 14px 16px;

  margin-top: 8px;

  font-size: 12px;

  color: #5EEAD4;

}

 

.tip-box {

  background: rgba(59,130,246,0.08);             /* blue */

  border: 1px solid rgba(59,130,246,0.35);

  color: #93C5FD;

  border-radius: 8px;

  padding: 12px 14px;

  font-size: 12px;

  line-height: 1.55;

}

 

/* Utility */

#MainMenu, footer, header { visibility: hidden; }

.block-container { padding-top: 1rem; max-width: 100%; }

</style>

""", unsafe_allow_html=True)

 

# ── Data (exact values you approved) ──────────────────────────────────────────

# Treat "Reject PPM" as PPM ≈ DPMO for teaching clarity.

SIGMA_TABLES = {

    "Short-term (no shift)": [

        {"s": 1, "yield_pct": 68.27,      "dpmo": 317_300.0},

        {"s": 2, "yield_pct": 95.45,      "dpmo": 45_500.0},

        {"s": 3, "yield_pct": 99.73,      "dpmo": 2_700.0},

        {"s": 4, "yield_pct": 99.9937,    "dpmo": 63.0},

        {"s": 5, "yield_pct": 99.999943,  "dpmo": 0.53},

        {"s": 6, "yield_pct": 99.999998,  "dpmo": 0.002},

    ],

    "Long-term (+1.5σ shift)": [

        {"s": 1, "yield_pct": 30.23,      "dpmo": 697_700.0},

        {"s": 2, "yield_pct": 69.13,      "dpmo": 308_700.0},

        {"s": 3, "yield_pct": 93.32,      "dpmo": 66_810.0},

        {"s": 4, "yield_pct": 99.3790,    "dpmo": 6_210.0},

        {"s": 5, "yield_pct": 99.97670,   "dpmo": 233.0},

        {"s": 6, "yield_pct": 99.999660,  "dpmo": 3.4},

    ],

}

 

# Colors (1..6)

SIGMA_COLORS = [

    (1, (220,  38,  38)),

    (2, (234,  88,  12)),

    (3, (202, 138,   4)),

    (4, (101, 163,  13)),

    (5, ( 22, 163,  74)),

    (6, ( 13, 148, 136)),

]

 

# Verdict bands

VERDICTS = [

    (1.0, 1.8, "Highly Unpredictable", "#7f1d1d", "#fca5a5"),

    (1.8, 2.6, "Frequent Escapes",     "#7c2d12", "#fdba74"),

    (2.6, 3.4, "Industry Average",     "#78350f", "#fde68a"),

    (3.4, 4.4, "Getting Good",         "#1a2e05", "#bef264"),

    (4.4, 5.4, "Best-in-Class",        "#052e16", "#86efac"),

    (5.4, 7.0, "World-Class / TPS",    "#022c22", "#5eead4"),

]

 

PROCESSES = [

    {"name": "🚚 Lead Time",         "unit": "shipments/day", "volume": 500,  "spec": "Target ± 2 days"},

    {"name": "⚙️ Part Dimensions",   "unit": "parts/day",     "volume": 8000, "spec": "±0.5mm tolerance"},

    {"name": "📋 Order Accuracy",    "unit": "orders/day",    "volume": 1200, "spec": "All fields correct"},

    {"name": "🎨 Paint Quality",     "unit": "panels/day",    "volume": 3000, "spec": "No visible defects"},

    {"name": "📦 On-Time Delivery",  "unit": "trips/day",     "volume": 400,  "spec": "Within time window"},

    {"name": "💰 Invoice Accuracy",  "unit": "invoices/day",  "volume": 1500, "spec": "All line items correct"},

]

 

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_sigma_color(s: float) -> tuple:

    """Interpolated RGB (0–1) across 1..6 anchors."""

    lo = max(1, min(6, int(s)))

    hi = min(6, lo + 1)

    t  = s - lo

    a  = SIGMA_COLORS[lo - 1][1]

    b  = SIGMA_COLORS[hi - 1][1]

    r  = (a[0] + (b[0] - a[0]) * t) / 255

    g  = (a[1] + (b[1] - a[1]) * t) / 255

    bv = (a[2] + (b[2] - a[2]) * t) / 255

    return (r, g, bv)

 

def get_sigma_color_hex(s: float) -> str:

    r, g, b = get_sigma_color(s)

    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

 

def interpolate_between(table: list, sigma: float) -> dict:

    """

    Linear interpolation between your exact anchor values (1..6).

    Returns dict with 'yield_pct' and 'dpmo'.

    """

    if sigma <= 1: return {"yield_pct": table[0]["yield_pct"], "dpmo": table[0]["dpmo"]}

    if sigma >= 6: return {"yield_pct": table[-1]["yield_pct"], "dpmo": table[-1]["dpmo"]}

    lo = int(np.floor(sigma))

    hi = lo + 1

    frac = sigma - lo

    lo_row = next(r for r in table if r["s"] == lo)

    hi_row = next(r for r in table if r["s"] == hi)

    yield_pct = lo_row["yield_pct"] + (hi_row["yield_pct"] - lo_row["yield_pct"]) * frac

    dpmo      = lo_row["dpmo"]      + (hi_row["dpmo"]      - lo_row["dpmo"])      * frac

    return {"yield_pct": yield_pct, "dpmo": dpmo}

 

def format_dpmo(dpmo: float) -> str:

    """Pretty print PPM/DPMO with sensible precision."""

    if dpmo >= 1000: return f"{int(round(dpmo)):,}"

    if dpmo >= 1:    return f"{dpmo:.2f}"

    if dpmo >= 0.1:  return f"{dpmo:.2f}"

    return f"{dpmo:.3f}"

 

def calc_defects_per_day(volume: int, dpmo: float) -> str:

    d = (dpmo / 1e6) * volume

    if d < 0.01: return "< 0.01"

    if d < 1:    return f"{d:.2f}"

    return f"{int(round(d)):,}"

 

def get_verdict(s: float):

    for lo, hi, label, bg, fg in VERDICTS:

        if lo <= s < hi:

            return label, bg, fg

    return VERDICTS[-1][2], VERDICTS[-1][3], VERDICTS[-1][4]

 

# ── Chart ─────────────────────────────────────────────────────────────────────

def make_curve_figure(sigma: float) -> plt.Figure:

    """

    Spec limits are fixed at ±3 spec units.

    Process spread shrinks as sigma increases: proc_sigma = 3 / sigma.

    X‑axis ticks are labeled in PROCESS σ units so LSL/USL align to ±sigma.

    """

    fig, ax = plt.subplots(figsize=(10, 4.2), facecolor="#040C18")

    ax.set_facecolor("#040C18")

 

    spec_half  = 3.0

    proc_sigma = spec_half / sigma

    x_range    = max(spec_half * 2.4, sigma * 4.5)

    x = np.linspace(-x_range, x_range, 1000)

 

    y = np.exp(-0.5 * (x / proc_sigma) ** 2)

 

    lsl, usl = -spec_half, spec_half

    color_rgb = get_sigma_color(sigma)

 

    # Out-of-spec shading

    ax.fill_between(x, y, 0, where=(x < lsl), color="#3c0606", alpha=0.95, linewidth=0)

    ax.fill_between(x, y, 0, where=(x > usl), color="#3c0606", alpha=0.95, linewidth=0)

 

    # In-spec baseline tint

    ax.fill_between(x, 0, 0.02, where=((x >= lsl) & (x <= usl)), color="#0D9488", alpha=0.08, linewidth=0)

 

    # Gradient fill & outline

    for alpha_mult, y_frac in [(0.15, 1.0), (0.35, 0.75), (0.55, 0.5), (0.75, 0.25)]:

        ax.fill_between(x, y * y_frac, y, color=color_rgb, alpha=alpha_mult * 0.3, linewidth=0)

    ax.fill_between(x, 0, y, color=color_rgb, alpha=0.45, linewidth=0)

    ax.plot(x, y, color=color_rgb, linewidth=2.5, zorder=5)

 

    # Spec lines + tags

    ax.axvline(lsl, color="white", linewidth=2.5, zorder=6)

    ax.axvline(usl, color="white", linewidth=2.5, zorder=6)

    for xv, lbl in [(lsl, "LSL"), (usl, "USL")]:

        ax.text(

            xv, 1.07, lbl,

            color="#040C18", fontsize=9, fontweight="bold",

            ha="center", va="center", zorder=8,

            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="white", linewidth=0),

        )

 

    # Center dashed

    ax.axvline(0, color="white", linewidth=1, linestyle=(0, (3, 5)), alpha=0.15, zorder=4)

 

    # DEFECTS tags if spill is visible

    spill = np.exp(-0.5 * (lsl / proc_sigma) ** 2)

    if spill > 0.02:

        ax.text(lsl * 1.5, 0.08, "DEFECTS", color="#ef4444", fontsize=8, fontweight="bold",

                ha="center", alpha=0.7, fontfamily="monospace")

        ax.text(usl * 1.5, 0.08, "DEFECTS", color="#ef4444", fontsize=8, fontweight="bold",

                ha="center", alpha=0.7, fontfamily="monospace")

 

    # Empirical rule bands (±1σ, ±2σ, ±3σ of the PROCESS)

    for mult, alpha in [(1, 0.04), (2, 0.03), (3, 0.025)]:

        band_x = x[(x >= -proc_sigma * mult) & (x <= proc_sigma * mult)]

        band_y = y[(x >= -proc_sigma * mult) & (x <= proc_sigma * mult)]

        ax.fill_between(band_x, 0, band_y, color="white", alpha=alpha, linewidth=0)

 

    # Process-σ ticks (so LSL/USL sit at ±sigma)

    max_k = 6

    tick_positions = [k * proc_sigma for k in range(-max_k, max_k + 1)]

    tick_labels = [("μ" if k == 0 else f"{k}σ") for k in range(-max_k, max_k + 1)]

    ax.set_xticks(tick_positions)

    ax.set_xticklabels(tick_labels, color="#64748B", fontsize=8.5, fontfamily="monospace")

 

    # Style

    ax.set_xlim(-x_range, x_range)

    ax.set_ylim(0, 1.18)

    ax.set_yticks([])

    ax.tick_params(axis="x", colors="#475569", length=4, bottom=True)

    for spine in ax.spines.values():

        spine.set_visible(False)

    ax.axhline(0, color="#94A3B8", linewidth=1, alpha=0.3)

    fig.tight_layout(pad=0.4)

    return fig

 

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:

    st.markdown('<div class="section-header">Select Process</div>', unsafe_allow_html=True)

    process_names = [p["name"] for p in PROCESSES]

    process_choice = st.radio("process", process_names, index=2, label_visibility="collapsed")

    proc = PROCESSES[process_names.index(process_choice)]

 

    st.markdown("---")

    st.markdown('<div class="section-header">Sigma Convention</div>', unsafe_allow_html=True)

    # Default to SHORT-TERM for teaching (matches Empirical Rule)

    sigma_mode = st.radio(

        "sigma_mode",

        options=["Short-term (no shift)", "Long-term (+1.5σ shift)"],

        index=0,

        label_visibility="collapsed",

    )

 

    # Teaching-oriented Tip box (your requested explanation)

    st.markdown("""

<div class="tip-box">

  <strong>Teaching tip:</strong> Start with <strong>Short‑term (no shift)</strong> because it matches the

  Empirical Rule (68–95–99.7%) and the standard normal curve—perfect for learning variation,

  standard deviation, and capability basics. Later, introduce

  <strong>Long‑term (+1.5σ shift)</strong> to show how real processes drift over time; this is the

  business convention behind the famous <em>6σ = 3.4 PPM</em> benchmark.

  <br><br>

  <em>Rule of thumb</em>: Short‑term for statistics & teaching; Long‑term for operational benchmarks and Six Sigma program targets.

</div>

""", unsafe_allow_html=True)

 

    st.markdown("---")

    st.markdown('<div class="section-header">Empirical Rule</div>', unsafe_allow_html=True)

    st.markdown("""

<div style="font-size:12px; line-height:1.8;">

  <div style="display:flex;justify-content:space-between;">

    <span style="color:#64748B;">±1σ of mean</span>

    <span style="color:#EF4444;font-family:monospace;font-weight:600;">68.27%</span>

  </div>

  <div style="display:flex;justify-content:space-between;">

    <span style="color:#64748B;">±2σ of mean</span>

    <span style="color:#F97316;font-family:monospace;font-weight:600;">95.45%</span>

  </div>

  <div style="display:flex;justify-content:space-between;">

    <span style="color:#64748B;">±3σ of mean</span>

    <span style="color:#EAB308;font-family:monospace;font-weight:600;">99.73%</span>

  </div>

</div>

""", unsafe_allow_html=True)

 

# ── Main content ──────────────────────────────────────────────────────────────

# Header

sigma_val = float(st.session_state.get("sigma_slider", 6.0))

color_hex = get_sigma_color_hex(sigma_val)

verdict_lbl, verdict_bg, verdict_fg = get_verdict(sigma_val)

 

st.markdown(f"""

<div class="app-header">

  <div>

    <div class="app-title">Six Sigma Process Explorer</div>

    <div class="app-subtitle">Automotive Supply Chain · Drag the slider to explore sigma levels</div>

  </div>

  <div>

    <div class="sigma-badge" style="color:{color_hex};">{sigma_val:.1f}<span style="font-size:18px;color:#64748B;margin-left:6px;">σ</span></div>

    <div class="sigma-sub" style="color:{verdict_fg};">{verdict_lbl}</div>

  </div>

</div>

""", unsafe_allow_html=True)

 

# Slider (authoritative value)

sigma_val = st.slider(

    "Sigma Level",

    min_value=1.0, max_value=6.0, value=sigma_val, step=0.05,

    key="sigma_slider", label_visibility="collapsed",

)

 

# Pick the table based on selected convention (exact values + interpolation)

active_table = SIGMA_TABLES["Short-term (no shift)"] if sigma_mode.startswith("Short") else SIGMA_TABLES["Long-term (+1.5σ shift)"]

stats = interpolate_between(active_table, sigma_val)

dpmo_now = stats["dpmo"]

yield_now = stats["yield_pct"]

defects_day = calc_defects_per_day(proc["volume"], dpmo_now)

cp_index = sigma_val / 3.0

 

# Chart

fig = make_curve_figure(sigma_val)

st.pyplot(fig, use_container_width=True)

plt.close(fig)

 

# Metrics row

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric("Sigma Level", f"{sigma_val:.2f}σ")

with col2:

    st.metric("Yield", f"{yield_now:.6f}".rstrip("0").rstrip(".") + "%")

with col3:

    st.metric("Reject PPM (≈ DPMO)", format_dpmo(dpmo_now))

with col4:

    st.metric(f"Defects / Day ({proc['unit']})", defects_day)

with col5:

    st.metric("Cp Index", f"{cp_index:.2f}")

 

# Process context + verdict

left_col, right_col = st.columns([2, 1])

with left_col:

    st.markdown(f"""

<div class="info-box">

  <strong>{proc['name'].split(' ')[1]}</strong> · {proc['spec']}<br>

  At {sigma_val:.1f}σ ({'ST no-shift' if sigma_mode.startswith('Short') else 'LT +1.5σ'}) →

  <strong>{defects_day}</strong> defective {proc['unit']} out of {proc['volume']:,} total

</div>

""", unsafe_allow_html=True)

with right_col:

    verdict_lbl, verdict_bg, verdict_fg = get_verdict(sigma_val)

    st.markdown(f"""

<div class="verdict-box" style="background:{verdict_bg};border:1px solid {verdict_fg};margin-top:0;">

  <div style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:{verdict_fg};opacity:0.7;margin-bottom:4px;">Process State</div>

  <div style="font-size:14px;font-weight:700;color:{verdict_fg};">{verdict_lbl}</div>

  <div style="font-size:11px;color:{verdict_fg};opacity:0.7;margin-top:4px;">{proc['volume']:,} {proc['unit']}</div>

</div>

""", unsafe_allow_html=True)

 

# Sigma reference table (exact anchor values)

st.markdown('<div class="section-header" style="margin-top:24px;">Sigma Reference Scale</div>', unsafe_allow_html=True)

table_cols = st.columns(6)

for i, row in enumerate(active_table):

    s = row["s"]

    active = abs(sigma_val - float(s)) < 0.5

    c_hex = get_sigma_color_hex(float(s))

    bg = "rgba(13,148,136,0.15)" if active else "rgba(8,14,26,0.6)"

    border = f"1px solid {c_hex}" if active else "1px solid #1A2E48"

    with table_cols[i]:

        st.markdown(f"""

<div style="background:{bg};border:{border};border-radius:8px;padding:12px 10px;text-align:center;transition:all 0.3s;">

  <div style="font-family:monospace;font-size:22px;font-weight:700;color:{c_hex};">{s}σ</div>

  <div style="font-size:10px;font-weight:600;color:{"#F0F6FF" if active else "#64748B"};margin:4px 0;">

    {"Short-term (no shift)" if sigma_mode.startswith("Short") else "Long-term (+1.5σ)"}

  </div>

  <div style="font-family:monospace;font-size:11px;color:{c_hex};">{format_dpmo(row['dpmo'])} PPM</div>

  <div style="font-size:10px;color:#475569;margin-top:2px;">{row['yield_pct']}%</div>

</div>

""", unsafe_allow_html=True)
