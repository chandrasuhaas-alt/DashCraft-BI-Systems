import io
import time
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.rule_engine import apply_rules, profile_dataframe

st.set_page_config(
    page_title="DashCraft BI",
    page_icon="🛰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═════════════════════════════════════════════════════════════════════════════
# DESIGN TOKENS
# ═════════════════════════════════════════════════════════════════════════════
BG1  = "#020617"   # primary background
BG2  = "#0B132B"   # secondary background
CA   = "#00C2FF"   # main accent
CLB  = "#38BDF8"   # light blue
CMB  = "#0EA5E9"   # medium blue
CDB  = "#1D4ED8"   # deep blue
CAQ  = "#22D3EE"   # aqua
CSU  = "#10B981"   # success
CHL  = "#6366F1"   # highlight
CT   = "#E2E8F0"   # primary text
CTD  = "#94A3B8"   # secondary text
CBR  = "#1E3A5F"   # border
CHART_COLORS = [CA, CSU, CAQ, CHL, CLB, CMB, "#F472B6"]

# ═════════════════════════════════════════════════════════════════════════════
# CSS
# ═════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"],
.main .block-container,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: {BG1} !important;
    color: {CT} !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}

[data-testid="stSidebar"],
[data-testid="collapsedControl"] {{ display: none !important; }}

.block-container {{
    padding-top: 0 !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1180px !important;
}}

::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background:{BG1}; }}
::-webkit-scrollbar-thumb {{ background:{CDB}; border-radius:100px; }}
::-webkit-scrollbar-thumb:hover {{ background:{CA}; }}

h1,h2,h3,h4,h5 {{
    font-family:'Space Grotesk',sans-serif !important;
    color:{CT} !important; font-weight:700 !important;
}}
p, li, span, div, label {{
    font-family:'Space Grotesk',sans-serif !important;
    color:{CT} !important;
}}

/* Buttons */
.stButton > button {{
    background:transparent !important;
    color:{CA} !important;
    border:1.5px solid {CA} !important;
    border-radius:6px !important;
    font-family:'Space Grotesk',sans-serif !important;
    font-weight:600 !important;
    font-size:14px !important;
    padding:10px 28px !important;
    transition:all 0.25s !important;
    box-shadow:0 0 12px rgba(0,194,255,0.15) !important;
}}
.stButton > button:hover {{
    background:rgba(0,194,255,0.1) !important;
    box-shadow:0 0 24px rgba(0,194,255,0.35) !important;
    transform:translateY(-1px) !important;
}}
.stButton > button[kind="primary"] {{
    background:linear-gradient(135deg,{CDB},{CA}) !important;
    color:#fff !important; border:none !important;
    box-shadow:0 0 20px rgba(0,194,255,0.4) !important;
}}
.stButton > button[kind="primary"]:hover {{
    box-shadow:0 0 32px rgba(0,194,255,0.6) !important;
}}

/* Metrics */
[data-testid="stMetric"] {{
    background:{BG2} !important;
    border:1px solid {CBR} !important;
    border-top:2px solid {CA} !important;
    border-radius:10px !important;
    padding:18px !important;
    box-shadow:0 0 16px rgba(0,194,255,0.07) !important;
}}
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] p {{
    color:{CTD} !important; font-size:11px !important;
    font-weight:600 !important; text-transform:uppercase !important;
    letter-spacing:1.2px !important;
}}
[data-testid="stMetricValue"] > div {{
    color:{CA} !important; font-size:26px !important;
    font-weight:700 !important; font-family:'JetBrains Mono',monospace !important;
}}
[data-testid="stMetricDelta"] > div {{
    color:{CSU} !important; font-size:12px !important;
    font-family:'JetBrains Mono',monospace !important;
}}

hr {{ border-color:{CBR} !important; margin:2rem 0 !important; opacity:0.5 !important; }}

/* Progress */
.stProgress > div > div > div {{
    background:linear-gradient(90deg,{CDB},{CA}) !important;
    border-radius:100px !important;
    box-shadow:0 0 8px rgba(0,194,255,0.5) !important;
}}
.stProgress > div > div {{
    background:rgba(30,58,95,0.35) !important;
    border-radius:100px !important;
}}

/* Alerts */
[data-testid="stAlert"] {{
    background:rgba(11,19,43,0.9) !important;
    border-radius:8px !important; border-left-width:3px !important;
}}
[data-testid="stAlert"] p {{ color:{CT} !important; }}

/* Expander */
[data-testid="stExpander"] {{
    background:{BG2} !important;
    border:1px solid {CBR} !important;
    border-radius:10px !important;
}}
[data-testid="stExpander"] summary {{ color:{CT} !important; font-weight:600 !important; }}
[data-testid="stExpander"] summary:hover {{ color:{CA} !important; }}
[data-testid="stExpander"] > div > div {{ background:{BG2} !important; }}

/* Select */
[data-baseweb="select"] > div {{
    background:{BG2} !important; border:1px solid {CBR} !important;
    border-radius:8px !important; color:{CT} !important;
}}
[data-baseweb="select"] > div:hover {{ border-color:{CA} !important; }}
[data-baseweb="select"] span {{ color:{CT} !important; }}
[data-baseweb="menu"] {{
    background:{BG2} !important; border:1px solid {CBR} !important;
}}
[data-baseweb="option"] {{ background:{BG2} !important; color:{CT} !important; }}
[data-baseweb="option"]:hover {{
    background:rgba(0,194,255,0.1) !important; color:{CA} !important;
}}

/* Radio */
.stRadio > div {{ background:transparent !important; gap:8px !important; }}
.stRadio label {{
    color:{CTD} !important; font-size:14px !important;
    padding:8px 16px !important; border:1px solid {CBR} !important;
    border-radius:6px !important; transition:all 0.2s !important;
}}
.stRadio label:has(input:checked) {{
    color:{CA} !important; border-color:{CA} !important;
    background:rgba(0,194,255,0.08) !important;
    box-shadow:0 0 10px rgba(0,194,255,0.18) !important;
}}

/* Slider */
.stSlider label {{ color:{CTD} !important; font-size:13px !important; }}
[data-testid="stThumbValue"] {{
    color:{CA} !important; font-family:'JetBrains Mono',monospace !important;
}}
[data-baseweb="slider"] [role="slider"] {{
    background:{CA} !important; border-color:{CA} !important;
    box-shadow:0 0 10px rgba(0,194,255,0.6) !important;
}}

/* Checkbox */
.stCheckbox label {{ color:{CTD} !important; }}
.stCheckbox label:hover {{ color:{CA} !important; }}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {{
    background:rgba(11,19,43,0.7) !important;
    border:2px dashed {CBR} !important;
    border-radius:12px !important; transition:all 0.2s !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color:{CA} !important;
    background:rgba(0,194,255,0.04) !important;
    box-shadow:0 0 20px rgba(0,194,255,0.1) !important;
}}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {{ color:{CTD} !important; }}

/* Multiselect tags */
[data-baseweb="tag"] {{
    background:rgba(0,194,255,0.12) !important;
    border:1px solid {CA} !important; border-radius:4px !important;
}}
[data-baseweb="tag"] span {{ color:{CA} !important; }}

/* Widget labels */
.stSelectbox label, .stMultiSelect label,
.stSlider label, .stRadio > label,
.stFileUploader label, .stCheckbox > label {{
    color:{CTD} !important; font-size:13px !important;
    font-weight:500 !important;
}}

/* Dataframe */
[data-testid="stDataFrame"] {{
    border:1px solid {CBR} !important; border-radius:10px !important;
}}

/* Spinner */
.stSpinner > div {{ border-top-color:{CA} !important; }}

/* ── Custom components ── */
.dc-nav {{
    position:sticky; top:0; z-index:999;
    background:rgba(2,6,23,0.94);
    backdrop-filter:blur(16px);
    border-bottom:1px solid {CBR};
    padding:14px 0; margin-bottom:0;
    display:flex; align-items:center; justify-content:space-between;
}}
.dc-card {{
    background:{BG2};
    border:1px solid {CBR};
    border-radius:12px; padding:24px;
    box-shadow:0 4px 24px rgba(0,0,0,0.35), 0 0 0 1px rgba(0,194,255,0.03);
    margin-bottom:16px; transition:box-shadow 0.25s, border-color 0.25s;
}}
.dc-card:hover {{
    border-color:rgba(0,194,255,0.22);
    box-shadow:0 4px 32px rgba(0,0,0,0.45), 0 0 20px rgba(0,194,255,0.07);
}}
.dc-card-glow {{
    background:{BG2}; border:1px solid {CA};
    border-radius:12px; padding:16px 20px;
    box-shadow:0 0 24px rgba(0,194,255,0.18), 0 4px 24px rgba(0,0,0,0.4);
    margin-bottom:16px;
}}
.step-header {{
    border-left:3px solid {CA};
    padding:16px 20px; margin:36px 0 20px 0;
    background:linear-gradient(90deg,rgba(0,194,255,0.05) 0%,transparent 100%);
    border-radius:0 8px 8px 0;
    box-shadow:0 0 14px rgba(0,194,255,0.06);
}}
.step-num {{
    font-size:10px; font-weight:700; color:{CA};
    text-transform:uppercase; letter-spacing:2px;
    font-family:'JetBrains Mono',monospace;
}}
.step-title {{
    font-size:22px; font-weight:700; color:{CT};
    margin-top:4px; font-family:'Space Grotesk',sans-serif;
}}
.step-sub {{ font-size:13px; color:{CTD}; margin-top:6px; line-height:1.5; }}

.pill {{
    display:inline-block; padding:3px 11px; border-radius:100px;
    font-size:11px; font-weight:700; letter-spacing:0.5px;
    font-family:'JetBrains Mono',monospace;
}}
.pill-cyan   {{ background:rgba(0,194,255,0.1);   color:{CA};  border:1px solid rgba(0,194,255,0.3); }}
.pill-green  {{ background:rgba(16,185,129,0.1);  color:{CSU}; border:1px solid rgba(16,185,129,0.3); }}
.pill-amber  {{ background:rgba(245,158,11,0.1);  color:#F59E0B; border:1px solid rgba(245,158,11,0.3); }}
.pill-indigo {{ background:rgba(99,102,241,0.1);  color:{CHL}; border:1px solid rgba(99,102,241,0.3); }}

.stat-item {{
    background:{BG2}; border:1px solid {CBR};
    border-radius:10px; padding:18px 14px; text-align:center;
    box-shadow:0 0 14px rgba(0,194,255,0.05); transition:all 0.2s;
}}
.stat-item:hover {{
    border-color:rgba(0,194,255,0.28);
    box-shadow:0 0 22px rgba(0,194,255,0.12);
}}
.stat-val   {{ font-size:1.8rem; font-weight:700; color:{CA}; font-family:'JetBrains Mono',monospace; }}
.stat-label {{ font-size:11px; color:{CTD}; font-weight:500; margin-top:4px; text-transform:uppercase; letter-spacing:0.8px; }}

.col-card {{
    background:{BG2}; border:1px solid {CBR};
    border-radius:8px; padding:12px 18px; margin-bottom:8px;
    display:flex; align-items:center; gap:16px; transition:border-color 0.2s;
}}
.col-card:hover {{ border-color:rgba(0,194,255,0.22); }}

.role-card {{
    background:{BG2}; border:1.5px solid {CBR};
    border-radius:12px; padding:22px; margin-top:8px; transition:all 0.2s;
}}
.role-card-active {{
    border-color:{CA} !important;
    background:rgba(0,194,255,0.05) !important;
    box-shadow:0 0 24px rgba(0,194,255,0.16) !important;
}}

@keyframes pulse-glow {{
    0%,100% {{ opacity:1; box-shadow:0 0 6px {CSU}; }}
    50%      {{ opacity:0.4; box-shadow:0 0 14px {CSU}; }}
}}
.live-dot {{
    display:inline-block; width:8px; height:8px;
    border-radius:50%; background:{CSU};
    animation:pulse-glow 1.2s infinite;
    margin-right:6px; vertical-align:middle;
}}

/* Subtle scanline overlay */
body::before {{
    content:''; position:fixed; top:0; left:0; right:0; bottom:0;
    background:repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,194,255,0.009) 2px, rgba(0,194,255,0.009) 4px
    );
    pointer-events:none; z-index:9998;
}}

.dc-footer {{
    text-align:center; padding:32px 0 24px;
    color:{CTD}; font-size:12px;
    border-top:1px solid {CBR}; margin-top:48px;
    font-family:'JetBrains Mono',monospace;
}}
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# PLOTLY THEME
# ═════════════════════════════════════════════════════════════════════════════
PT   = dict(paper_bgcolor=BG2, plot_bgcolor="#080F1F",
            font=dict(family="Space Grotesk, sans-serif", color=CT, size=12),
            colorway=CHART_COLORS)
GRD  = dict(gridcolor=CBR, showgrid=True, zeroline=False, color=CTD)
AXF  = dict(tickcolor=CTD, linecolor=CBR, showline=True)
MAR  = dict(l=16, r=16, t=48, b=16)

def theme(fig):
    fig.update_layout(**PT, margin=MAR,
        legend=dict(bgcolor="rgba(11,19,43,0.9)", bordercolor=CBR,
                    borderwidth=1, font=dict(color=CTD)))
    fig.update_xaxes(**GRD, **AXF)
    fig.update_yaxes(**GRD, **AXF)
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# SAMPLE DATA
# ═════════════════════════════════════════════════════════════════════════════
SALES_CSV = """Month,Revenue,Units,Region,Category,Profit
Jan,42000,320,North,Electronics,12000
Feb,38500,290,South,Clothing,9800
Mar,51000,410,East,Electronics,15200
Apr,47200,370,West,Furniture,11500
May,55800,450,North,Electronics,17900
Jun,62100,510,South,Clothing,19800
Jul,58400,470,East,Furniture,16300
Aug,64700,530,West,Electronics,21200
Sep,59300,480,North,Clothing,18100
Oct,71200,590,South,Electronics,24500
Nov,83400,680,East,Clothing,28900
Dec,95600,790,West,Electronics,34200"""

HR_CSV = """Department,Headcount,Attrition,AvgSalary,Satisfaction,YearsAvg
Engineering,245,12,95000,4.2,3.8
Sales,180,28,72000,3.6,2.1
Marketing,95,15,78000,3.9,3.2
HR,45,8,68000,4.1,4.5
Finance,78,6,88000,4.3,5.1
Operations,160,20,65000,3.4,2.8
Product,120,10,98000,4.5,3.6
Support,210,35,58000,3.2,1.9"""

# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════
def section(num, title, subtitle=""):
    sub = f'<div class="step-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
        <div class="step-header">
            <div class="step-num">// Step {num}</div>
            <div class="step-title">{title}</div>
            {sub}
        </div>
    """, unsafe_allow_html=True)


def render_chart(df, rule, idx):
    chart, cfg, title, rid = rule["chart"], rule["config"], rule["name"], rule["id"]
    num_c = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    cat_c = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    all_c = list(df.columns)

    # ── KPI ──────────────────────────────────────────────────────────────────
    if chart == "kpi":
        st.markdown(f'<div style="font-size:10px;color:{CTD};text-transform:uppercase;'
                    f'letter-spacing:1.5px;margin-bottom:14px;font-family:JetBrains Mono,monospace;">'
                    f'Key Performance Indicators</div>', unsafe_allow_html=True)
        sel = st.multiselect("Select columns to display as KPIs",
                             num_c, default=num_c[:4], key=f"kpi_{idx}")
        if sel:
            cols_ui = st.columns(len(sel))
            for i, col in enumerate(sel):
                tot = df[col].sum()
                avg = df[col].mean()
                cols_ui[i].metric(col,
                    f"{tot/1000:.1f}K" if tot >= 10000 else f"{tot:,.0f}",
                    f"Avg: {avg:,.0f}")
        return

    # ── Controls ──────────────────────────────────────────────────────────────
    with st.expander(f"Customize — {title}", expanded=False):
        c1, c2, c3 = st.columns(3)

        if chart == "area":
            x  = c1.selectbox("X Axis", all_c, index=all_c.index(cfg["x"]) if cfg.get("x") in all_c else 0, key=f"x_{rid}_{idx}")
            y  = c2.selectbox("Y Axis", num_c, index=num_c.index(cfg["y"]) if cfg.get("y") in num_c else 0, key=f"y_{rid}_{idx}")
            y2 = c3.selectbox("Second Y Axis (optional)", ["None"]+num_c, key=f"y2_{rid}_{idx}")
            cfg = {"x":x, "y":y, "y2": None if y2=="None" else y2}

        elif chart == "bar":
            x   = c1.selectbox("Category (X Axis)", cat_c if cat_c else all_c, key=f"x_{rid}_{idx}")
            y   = c2.selectbox("Value (Y Axis)", num_c, index=num_c.index(cfg["y"]) if cfg.get("y") in num_c else 0, key=f"y_{rid}_{idx}")
            y2  = c3.selectbox("Second Bar (optional)", ["None"]+num_c, key=f"y2_{rid}_{idx}")
            agg = c1.selectbox("Aggregation", ["sum","mean","count","max","min"], key=f"agg_{rid}_{idx}")
            cfg = {"x":x, "y":y, "y2": None if y2=="None" else y2, "agg":agg}

        elif chart == "pie":
            names  = c1.selectbox("Category Column", cat_c if cat_c else all_c, key=f"names_{rid}_{idx}")
            values = c2.selectbox("Value Column", num_c, index=num_c.index(cfg["values"]) if cfg.get("values") in num_c else 0, key=f"vals_{rid}_{idx}")
            top_n  = c3.slider("Top N Categories", 3, 20, 8, key=f"topn_{rid}_{idx}")
            cfg = {"names":names, "values":values, "top_n":top_n}

        elif chart == "scatter":
            x     = c1.selectbox("X Axis", num_c, index=num_c.index(cfg["x"]) if cfg.get("x") in num_c else 0, key=f"x_{rid}_{idx}")
            y     = c2.selectbox("Y Axis", num_c, index=num_c.index(cfg["y"]) if cfg.get("y") in num_c else (1 if len(num_c)>1 else 0), key=f"y_{rid}_{idx}")
            color = c3.selectbox("Color By", ["None"]+cat_c, key=f"col_{rid}_{idx}")
            tl    = c1.checkbox("Show Trendline", value=True, key=f"tl_{rid}_{idx}")
            cfg   = {"x":x, "y":y, "color": None if color=="None" else color, "trendline":tl}

        elif chart == "line":
            x     = c1.selectbox("X Axis", all_c, index=all_c.index(cfg["x"]) if cfg.get("x") in all_c else 0, key=f"x_{rid}_{idx}")
            y     = c2.selectbox("Y Axis", num_c, index=num_c.index(cfg["y"]) if cfg.get("y") in num_c else 0, key=f"y_{rid}_{idx}")
            color = c3.selectbox("Color By", ["None"]+cat_c, key=f"col_{rid}_{idx}")
            cfg   = {"x":x, "y":y, "color": None if color=="None" else color}

    # ── Render ────────────────────────────────────────────────────────────────
    try:
        if chart == "area":
            ys  = [cfg["y"]] + ([cfg["y2"]] if cfg.get("y2") and cfg["y2"] in df.columns else [])
            fig = px.area(df, x=cfg["x"], y=ys, title=title,
                          color_discrete_sequence=CHART_COLORS)
            for i, tr in enumerate(fig.data):
                tr.update(line=dict(width=2),
                          fillcolor=f"rgba(0,194,255,{0.10 - i*0.03})")
            st.plotly_chart(theme(fig), use_container_width=True)

        elif chart == "bar":
            ys  = [cfg["y"]] + ([cfg["y2"]] if cfg.get("y2") and cfg["y2"] in df.columns else [])
            grp = df.groupby(cfg["x"])[ys].agg(cfg.get("agg","sum")).reset_index()
            fig = px.bar(grp, x=cfg["x"], y=ys, barmode="group", title=title,
                         color_discrete_sequence=CHART_COLORS)
            fig.update_traces(marker_line_width=0, opacity=0.9)
            st.plotly_chart(theme(fig), use_container_width=True)

        elif chart == "pie":
            grp = df.groupby(cfg["names"])[cfg["values"]].sum().reset_index()
            grp = grp.nlargest(cfg.get("top_n",8), cfg["values"])
            fig = px.pie(grp, names=cfg["names"], values=cfg["values"],
                         title=title, hole=0.48,
                         color_discrete_sequence=CHART_COLORS)
            fig.update_traces(textposition="inside", textinfo="percent+label",
                              textfont=dict(color=CT, size=11))
            st.plotly_chart(theme(fig), use_container_width=True)

        elif chart == "scatter":
            fig = px.scatter(df, x=cfg["x"], y=cfg["y"],
                             color=cfg.get("color"), title=title,
                             trendline="ols" if cfg.get("trendline") else None,
                             trendline_color_override="#F59E0B",
                             opacity=0.8,
                             color_discrete_sequence=CHART_COLORS)
            st.plotly_chart(theme(fig), use_container_width=True)

        elif chart == "line":
            fig = px.line(df, x=cfg["x"], y=cfg["y"],
                          color=cfg.get("color"), title=title, markers=True,
                          color_discrete_sequence=CHART_COLORS)
            fig.update_traces(line_width=2.5, marker_size=5)
            st.plotly_chart(theme(fig), use_container_width=True)

    except Exception as e:
        st.warning(f"Could not render this chart: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# NAVBAR
# ═════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
    <div class="dc-nav">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:32px;height:32px;border-radius:8px;
                        background:linear-gradient(135deg,{CDB},{CA});
                        display:flex;align-items:center;justify-content:center;
                        box-shadow:0 0 14px rgba(0,194,255,0.5);font-size:16px;">🛰</div>
            <span style="font-size:20px;font-weight:700;color:{CT};
                         letter-spacing:-0.3px;font-family:'Space Grotesk',sans-serif;">
                Dash<span style="color:{CA};text-shadow:0 0 16px rgba(0,194,255,0.6);">Craft</span> BI
            </span>
            <span style="font-size:11px;color:{CTD};margin-left:4px;
                         font-family:'JetBrains Mono',monospace;">
                v2.0 — ANALYTICS PLATFORM
            </span>
        </div>
        <span style="font-size:11px;color:{CTD};font-family:'JetBrains Mono',monospace;">
            NEIL GOGTE INSTITUTE OF TECHNOLOGY &nbsp;·&nbsp; CSE (AIML)
        </span>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# HERO
# ═════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
    <div style="text-align:center;padding:56px 0 44px 0;">
        <div style="display:inline-block;background:rgba(0,194,255,0.07);color:{CA};
                    font-size:10px;font-weight:700;letter-spacing:2.5px;
                    text-transform:uppercase;padding:6px 20px;border-radius:100px;
                    border:1px solid rgba(0,194,255,0.22);margin-bottom:24px;
                    box-shadow:0 0 16px rgba(0,194,255,0.1);
                    font-family:'JetBrains Mono',monospace;">
            POWERED BY DMINER — 854 REAL DASHBOARDS ANALYZED
        </div>
        <h1 style="font-size:3.2rem;font-weight:700;color:{CT};letter-spacing:-1px;
                   margin-bottom:16px;line-height:1.15;font-family:'Space Grotesk',sans-serif;">
            Dashboards that don't<br>
            <span style="color:{CA};text-shadow:0 0 32px rgba(0,194,255,0.5),0 0 64px rgba(0,194,255,0.2);">
                make people fall asleep
            </span>
        </h1>
        <p style="font-size:1.05rem;color:{CTD};max-width:560px;margin:0 auto;
                  line-height:1.75;font-family:'Space Grotesk',sans-serif;">
            Upload your data, pick your role, and let DashCraft automatically recommend
            the right charts in the right places.
            No design degree required. No existential crisis either.
        </p>
    </div>
""", unsafe_allow_html=True)

# Stats strip
s1,s2,s3,s4,s5 = st.columns(5)
for col,val,lbl in zip([s1,s2,s3,s4,s5],
    ["854","208","624","73%","6"],
    ["Dashboards Analyzed","Models Trained","Design Rules","Model Accuracy","Rule Categories"]):
    with col:
        st.markdown(f'<div class="stat-item"><div class="stat-val">{val}</div>'
                    f'<div class="stat-label">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 01 — UPLOAD
# ═════════════════════════════════════════════════════════════════════════════
section("01","Upload Your Data",
        "Upload any CSV file or pick one of the sample datasets. DashCraft will analyze it automatically.")

source = st.radio("Data source",["Use a sample dataset","Upload my own CSV"],
                  horizontal=True, key="src")
df, dataset_name = None, ""

if source == "Use a sample dataset":
    choice = st.selectbox("Choose a sample dataset",
                          ["Quarterly Sales Data","HR Analytics"], key="sample")
    df = pd.read_csv(io.StringIO(SALES_CSV if choice=="Quarterly Sales Data" else HR_CSV))
    dataset_name = choice
    st.markdown(f'<div class="dc-card" style="border-color:rgba(16,185,129,0.35);'
                f'background:rgba(16,185,129,0.04);padding:12px 18px;">'
                f'<span style="color:{CSU};font-weight:600;">Sample loaded</span>'
                f'<span style="color:{CTD};font-size:13px;margin-left:8px;">'
                f'{choice} — {len(df):,} rows · {len(df.columns)} columns</span>'
                f'</div>', unsafe_allow_html=True)
else:
    up = st.file_uploader("Drop your CSV here — any CSV works", type=["csv"], key="up")
    if up:
        for enc in ["utf-8","latin-1","cp1252"]:
            try:
                df = pd.read_csv(up, encoding=enc); up.seek(0); break
            except UnicodeDecodeError:
                up.seek(0)
        if df is not None:
            dataset_name = up.name
            st.markdown(f'<div class="dc-card" style="border-color:rgba(16,185,129,0.35);'
                        f'background:rgba(16,185,129,0.04);padding:12px 18px;">'
                        f'<span style="color:{CSU};font-weight:600;">File loaded</span>'
                        f'<span style="color:{CTD};font-size:13px;margin-left:8px;">'
                        f'{up.name} — {len(df):,} rows · {len(df.columns)} columns</span>'
                        f'</div>', unsafe_allow_html=True)
        else:
            st.error("Could not read this file. Please make sure it is a valid CSV.")

if df is None:
    st.info("Select a data source above to continue.")
    st.stop()

with st.expander("Preview raw data (first 10 rows)", expanded=True):
    st.dataframe(df.head(10), use_container_width=True)

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 02 — PROFILE
# ═════════════════════════════════════════════════════════════════════════════
section("02","Data Profile","Every column decoded — types inferred, statistics computed, nulls counted.")

profile   = profile_dataframe(df)
num_all   = [c for c,p in profile.items() if p["type"]=="numerical"]
cat_all   = [c for c,p in profile.items() if p["type"]=="categorical"]
tmp_all   = [c for c,p in profile.items() if p["type"]=="temporal"]

p1,p2,p3,p4 = st.columns(4)
p1.metric("Total Rows",          f"{len(df):,}")
p2.metric("Numerical Columns",   len(num_all))
p3.metric("Categorical Columns", len(cat_all))
p4.metric("Temporal Columns",    len(tmp_all))

st.markdown("<br>", unsafe_allow_html=True)

TPILL = {"numerical":("pill-green","Numerical"),
         "categorical":("pill-cyan","Categorical"),
         "temporal":("pill-amber","Temporal")}

for col, p in profile.items():
    pc, pl = TPILL.get(p["type"],("pill-indigo","Unknown"))
    ext = ""
    if p["type"] == "numerical":
        ext = (f'<span style="font-family:JetBrains Mono,monospace;font-size:12px;color:{CTD};">'
               f'Min <strong style="color:{CT};">{p["min"]:,}</strong> &nbsp;'
               f'Avg <strong style="color:{CA};">{p["mean"]:,}</strong> &nbsp;'
               f'Max <strong style="color:{CT};">{p["max"]:,}</strong> &nbsp;'
               f'Std <strong style="color:{CTD};">{p["std"]:,}</strong></span>')
    st.markdown(f'<div class="col-card">'
                f'<div style="font-size:14px;font-weight:600;color:{CT};min-width:150px;">{col}</div>'
                f'<span class="pill {pc}">{pl}</span>'
                f'<div style="font-size:12px;color:{CTD};min-width:100px;">{p["n_unique"]} unique</div>'
                f'<div style="flex:1;">{ext}</div>'
                f'<div style="font-size:11px;color:{CBR};font-family:JetBrains Mono,monospace;">'
                f'null {p["null_pct"]}%</div>'
                f'</div>', unsafe_allow_html=True)

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 03 — ROLE
# ═════════════════════════════════════════════════════════════════════════════
section("03","Select Your Role","This determines which charts and layout rules get applied to your data.")

role = st.session_state.get("user_role")
rc1, rc2 = st.columns(2)

def role_items(items, color):
    return "".join(f'<div style="font-size:12px;color:{CTD};padding:3px 0;">'
                   f'<span style="color:{color};margin-right:8px;">›</span>{it}</div>'
                   for it in items)

with rc1:
    is_e = role == "executive"
    st.markdown(f'<div class="role-card {"role-card-active" if is_e else ""}">'
                f'<div style="font-size:16px;font-weight:700;color:{CA if is_e else CT};margin-bottom:8px;">Executive</div>'
                f'<div style="font-size:13px;color:{CTD};line-height:1.65;margin-bottom:14px;">'
                f'KPI cards up top, summary charts, clean layout. '
                f'Perfect for people with four back-to-back meetings after this.</div>'
                + role_items(["KPI summary cards (Rule R2)","Area trend chart (Rule R1)","Bar and donut charts","High-level overview only"], CA)
                + '</div>', unsafe_allow_html=True)
    if st.button("Select Executive", use_container_width=True, key="btn_e"):
        st.session_state.user_role = "executive"; st.rerun()

with rc2:
    is_a = role == "analyst"
    st.markdown(f'<div class="role-card {"role-card-active" if is_a else ""}">'
                f'<div style="font-size:16px;font-weight:700;color:{CA if is_a else CT};margin-bottom:8px;">Data Analyst</div>'
                f'<div style="font-size:13px;color:{CTD};line-height:1.65;margin-bottom:14px;">'
                f'Scatter plots, drill-downs, correlation analysis. '
                f'For the person who opens Excel for fun on weekends.</div>'
                + role_items(["Scatter plot with trendline (Rule R5)","Full chart suite","Detailed column mappings","All pairwise relationships shown"], CSU)
                + '</div>', unsafe_allow_html=True)
    if st.button("Select Analyst", use_container_width=True, key="btn_a"):
        st.session_state.user_role = "analyst"; st.rerun()

role = st.session_state.get("user_role")
if role:
    c = CA if role == "executive" else CSU
    st.markdown(f'<p style="font-size:13px;font-weight:600;color:{c};margin-top:10px;'
                f'font-family:JetBrains Mono,monospace;">// Role selected: {role.upper()}</p>',
                unsafe_allow_html=True)
else:
    st.info("Please select a role above to continue.")
    st.stop()

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 04 — MINING
# ═════════════════════════════════════════════════════════════════════════════
section("04","Rule Mining Engine",
        "DashCraft runs 208 models against patterns from 854 real dashboards. It is doing more work than it looks.")

with st.spinner("Running pattern mining engine..."):
    phases = [
        "Extracting single-view features — 33 features per column...",
        "Computing pairwise-view relationships — 41 cross-column features...",
        "Fitting RuleFit Binary Classifiers — all 208 of them...",
        "Filtering rules by confidence threshold...",
        "Generating layout recommendations...",
    ]
    pb = st.progress(0); st_txt = st.empty()
    for i, phase in enumerate(phases):
        pb.progress(int((i+1)/len(phases)*100), text=phase)
        st_txt.markdown(f'<p style="font-family:JetBrains Mono,monospace;font-size:12px;'
                        f'color:{CTD};">$ {phase}</p>', unsafe_allow_html=True)
        time.sleep(0.4)
    pb.progress(100, text="Mining complete — faster than your last standup meeting.")
    st_txt.empty()

rules = apply_rules(df, profile, role)
if not rules:
    st.warning("No rules could be applied to this dataset. Try a different role or a richer dataset.")
    st.stop()

avg_conf = sum(r["confidence"] for r in rules) / len(rules) * 100
st.markdown(f'<div class="dc-card-glow">'
            f'<span style="color:{CSU};font-weight:700;">{len(rules)} design rules applied</span>'
            f'<span style="color:{CTD};font-size:13px;margin-left:8px;">'
            f'for the <strong style="color:{CT};">{role.title()}</strong> role &nbsp;·&nbsp; '
            f'Average confidence: <strong style="color:{CA};font-family:JetBrains Mono,monospace;">'
            f'{avg_conf:.0f}%</strong></span></div>', unsafe_allow_html=True)

m1,m2,m3,m4 = st.columns(4)
m1.metric("Rules Applied",  len(rules))
m2.metric("Avg Confidence", f"{avg_conf:.0f}%")
m3.metric("Models Run",     "208")
m4.metric("User Role",      role.title())

st.markdown("<br>", unsafe_allow_html=True)
for rule in rules:
    conf = int(rule["confidence"]*100)
    with st.expander(f"{rule['id']}  —  {rule['name']}   ·   {conf}% confidence"):
        e1,e2,e3 = st.columns(3)
        e1.markdown(f"**Chart Type:** `{rule['chart']}`")
        e2.markdown(f"**Position:** `{rule['position']}`")
        e3.markdown(f"**Size:** `{rule['size']}`")
        st.markdown(f'<div style="background:rgba(0,194,255,0.03);border:1px solid {CBR};'
                    f'border-left:3px solid {CA};border-radius:0 6px 6px 0;'
                    f'padding:12px 16px;font-size:13px;color:{CTD};margin:10px 0;">'
                    f'{rule["description"]}</div>', unsafe_allow_html=True)
        cfg = rule.get("config",{})
        if cfg:
            st.markdown("**Column Mapping:** " + "  ·  ".join(
                f"`{k}` → `{v}`" for k,v in cfg.items() if v))
        st.progress(rule["confidence"])

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 05 — DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
section("05","Auto-Generated Dashboard",
        "Every chart placement is backed by a rule — not a vibe. Use the controls to customize any chart.")

dh1, dh2 = st.columns([3,1])
dh1.markdown(f'<div style="font-size:1.1rem;font-weight:700;color:{CT};">{dataset_name}</div>'
             f'<div style="font-size:12px;color:{CTD};margin-top:4px;font-family:JetBrains Mono,monospace;">'
             f'{len(rules)} rules applied &nbsp;·&nbsp; Role: {role.upper()} &nbsp;·&nbsp; {len(df):,} rows</div>',
             unsafe_allow_html=True)
with dh2:
    st.markdown(f'<div class="dc-card" style="text-align:center;padding:14px;">'
                f'<div style="font-size:10px;color:{CTD};font-weight:600;text-transform:uppercase;letter-spacing:1px;">Layout by</div>'
                f'<div style="font-size:17px;font-weight:700;color:{CA};text-shadow:0 0 12px rgba(0,194,255,0.5);">DashCraft BI</div>'
                f'<div style="font-size:10px;color:{CTD};font-family:JetBrains Mono,monospace;">Rule-based engine</div>'
                f'</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

kpi_r  = [r for r in rules if r["chart"]=="kpi"]
area_r = [r for r in rules if r["chart"]=="area"]
pair_r = [r for r in rules if r["chart"] not in ("kpi","area")]
idx = 0

for r in kpi_r:
    st.markdown('<div class="dc-card">', unsafe_allow_html=True)
    render_chart(df, r, idx); idx += 1
    st.markdown('</div><br>', unsafe_allow_html=True)

for r in area_r:
    st.markdown('<div class="dc-card">', unsafe_allow_html=True)
    render_chart(df, r, idx); idx += 1
    st.markdown('</div><br>', unsafe_allow_html=True)

for i in range(0, len(pair_r), 2):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="dc-card">', unsafe_allow_html=True)
        render_chart(df, pair_r[i], idx); idx += 1
        st.markdown('</div>', unsafe_allow_html=True)
    if i+1 < len(pair_r):
        with c2:
            st.markdown('<div class="dc-card">', unsafe_allow_html=True)
            render_chart(df, pair_r[i+1], idx); idx += 1
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

with st.expander("View Applied Design Rules"):
    st.dataframe(pd.DataFrame([{"Rule":r["id"],"Name":r["name"],"Chart":r["chart"],
        "Position":r["position"],"Confidence":f"{r['confidence']*100:.0f}%"} for r in rules]),
        use_container_width=True, hide_index=True)

with st.expander("View Raw Data"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 06 — LIVE STREAM
# ═════════════════════════════════════════════════════════════════════════════
section("06","Live Data Stream",
        "Simulate real-time data ingestion. The numbers are made up, but the dashboard updates are real.")

lc1,lc2,lc3 = st.columns(3)
sm  = lc1.selectbox("Streaming Metric",
      ["Revenue","Units Sold","Customer Count","Satisfaction Score"], key="sm")
si  = lc2.slider("Update Interval (seconds)", 0.5, 3.0, 1.0, 0.5, key="si")
sw  = lc3.slider("Rolling Window Size", 10, 60, 30, key="sw")

if "stream_running" not in st.session_state:  st.session_state.stream_running = False
if "stream_data"    not in st.session_state:  st.session_state.stream_data    = []

bc1, bc2 = st.columns(2)
if bc1.button("Start Stream", type="primary", use_container_width=True, key="ss"):
    st.session_state.stream_running = True;  st.session_state.stream_data = []
if bc2.button("Stop Stream",  use_container_width=True, key="so"):
    st.session_state.stream_running = False; st.session_state.stream_data = []

ss_ph = st.empty(); sk_ph = st.empty()
sc_ph = st.empty(); sh_ph = st.empty(); sa_ph = st.empty()

SEEDS  = {"Revenue":55000,"Units Sold":450,"Customer Count":1200,"Satisfaction Score":72}
NOISES = {"Revenue":5000, "Units Sold":45, "Customer Count":120, "Satisfaction Score":4}
seed   = SEEDS.get(sm,1000);  noise = NOISES.get(sm,100)
fmt    = lambda v: f"{v/1000:.1f}K" if v >= 10000 else f"{v:,.1f}"

if st.session_state.stream_running:
    i = len(st.session_state.stream_data)
    while st.session_state.stream_running:
        prev  = st.session_state.stream_data[-1]["value"] if st.session_state.stream_data else seed
        val   = max(0, prev + np.random.normal(0, noise*0.3)) * 0.97 + seed * 0.03
        pt    = {"t":i, "time":datetime.now().strftime("%H:%M:%S"), "value":round(val,2)}
        st.session_state.stream_data.append(pt)
        data  = st.session_state.stream_data[-sw:]
        sdf   = pd.DataFrame(data)
        cur   = sdf["value"].iloc[-1]
        prev2 = sdf["value"].iloc[-2] if len(sdf)>1 else cur
        dlt   = cur - prev2

        with sk_ph.container():
            k1,k2,k3,k4 = st.columns(4)
            k1.metric(f"Current {sm}", fmt(cur), f"{dlt:+.1f}")
            k2.metric("Window Average", fmt(sdf["value"].mean()))
            k3.metric("Window Peak",    fmt(sdf["value"].max()))
            k4.metric("Points Received", len(st.session_state.stream_data))

        sfig = go.Figure()
        sfig.add_trace(go.Scatter(x=sdf["time"], y=sdf["value"],
            mode="lines+markers", line=dict(color=CA, width=2.5),
            fill="tozeroy", fillcolor="rgba(0,194,255,0.07)",
            name=sm, marker=dict(size=4, color=CA)))
        if len(sdf) >= 5:
            sdf["ma"] = sdf["value"].rolling(5).mean()
            sfig.add_trace(go.Scatter(x=sdf["time"], y=sdf["ma"], mode="lines",
                line=dict(color="#F59E0B", width=1.5, dash="dot"),
                name="5-Point Moving Average"))
        sfig.update_layout(**PT, title=f"Live {sm} Feed", margin=MAR,
                           xaxis=dict(**GRD,**AXF), yaxis=dict(**GRD,**AXF))
        sc_ph.plotly_chart(sfig, use_container_width=True)

        hfig = go.Figure()
        hfig.add_trace(go.Histogram(x=sdf["value"], nbinsx=15,
            marker_color=CHL, opacity=0.85,
            marker_line=dict(color=BG2, width=1)))
        hfig.update_layout(**PT, title=f"Value Distribution — Last {len(sdf)} Points",
                           margin=MAR, xaxis=dict(**GRD,**AXF), yaxis=dict(**GRD,**AXF))
        sh_ph.plotly_chart(hfig, use_container_width=True)

        if abs(dlt) > seed * 0.12:
            direction = "surge" if dlt > 0 else "drop"
            action    = "Time to take credit." if dlt > 0 else "Time to call a meeting."
            sa_ph.warning(f"Significant {direction} detected ({dlt:+.0f}). {action}")
        else:
            sa_ph.empty()

        ss_ph.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;'
            f'background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.25);'
            f'border-radius:8px;padding:10px 16px;">'
            f'<span class="live-dot"></span>'
            f'<span style="font-size:13px;font-weight:600;color:{CSU};">STREAMING LIVE</span>'
            f'<span style="font-size:12px;color:{CTD};margin-left:6px;'
            f'font-family:JetBrains Mono,monospace;">'
            f'Point #{i+1} &nbsp;·&nbsp; {pt["time"]} &nbsp;·&nbsp; {fmt(cur)}</span>'
            f'</div>', unsafe_allow_html=True)

        i += 1
        time.sleep(si)
        if i > 500:
            st.session_state.stream_running = False
            ss_ph.info("Auto-stopped after 500 points. Even live data needs a break.")
            break
else:
    ss_ph.markdown(
        f'<div class="dc-card" style="padding:14px 18px;font-size:13px;color:{CTD};">'
        f'Press <strong style="color:{CA};">Start Stream</strong> to begin live data simulation. '
        f'The numbers are simulated, but the dashboard updates are real. Philosophy is optional.'
        f'</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
    <div class="dc-footer">
        DashCraft BI &nbsp;·&nbsp; Built on DMiner (Lin et al., HKUST 2023)
        &nbsp;·&nbsp; Neil Gogte Institute of Technology &nbsp;·&nbsp; CSE (AIML) 2025–26
        <br>
        <span style="font-style:italic;margin-top:6px;display:block;color:{CBR};">
            No dashboards were harmed in the making of this software.
        </span>
    </div>
""", unsafe_allow_html=True)
