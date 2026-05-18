"""Page 4 — Financial Summary (Phase 2 KPIs)."""

import os
import sys

import pandas as pd
import streamlit as st

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from utils.charts import bar_chart, histogram, overlay_lines, pie_chart, trend_line  # noqa: E402
from utils.filters import render_telestroke_filters  # noqa: E402
from utils.sidebar import render_sidebar  # noqa: E402
from utils.theme import FY_MONTH_ORDER, PSH_NAVY, PSH_TEAL, get_global_css  # noqa: E402

st.set_page_config(page_title="Financial", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
st.markdown(get_global_css(), unsafe_allow_html=True)

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("app.py")

render_sidebar()

DATA_DIR = os.path.join(PROJECT_DIR, "data")


@st.cache_data
def load_patients():
    df = pd.read_csv(os.path.join(DATA_DIR, "telestroke_synthetic.csv"))
    df["ed_arrival_dt"] = pd.to_datetime(df["ed_arrival_dt"], errors="coerce")
    return df


@st.cache_data
def load_costs():
    return pd.read_csv(os.path.join(DATA_DIR, "monthly_cost_synthetic.csv"))


df_full = load_patients()
costs_full = load_costs()

st.markdown("<h1>Financial Summary <span class='badge badge-phase2'>Phase 2</span></h1>", unsafe_allow_html=True)
st.caption("Cost of delivery, downstream revenue, payer mix.")
st.caption("PoC — Synthetic data only. For illustrative purposes.")

df = render_telestroke_filters(df_full)

if not len(df):
    st.warning("No records match the current filters.")
    st.stop()

df["month_name"] = pd.Categorical(df["month_name"], categories=FY_MONTH_ORDER, ordered=True)
df = df.sort_values(["fiscal_year", "month_name"])

# Filter monthly cost data to selected fiscal years
fy_set = set(df["fiscal_year"].unique().tolist())
costs = costs_full[costs_full["fiscal_year"].isin(fy_set)].copy()

# ── Section 1: KPI tiles ──────────────────────────────────────────────────
monthly_cost = costs["total_monthly_cost"].mean() if len(costs) else 0.0
downstream_revenue = costs["downstream_revenue"].mean() if len(costs) else 0.0
net_revenue = downstream_revenue - monthly_cost
medicare_share = (df["payer_category"] == "Medicare").mean() * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg Monthly Cost", f"${monthly_cost:,.0f}", help="TS-08 · Synthetic")
c2.metric("Avg Downstream Revenue", f"${downstream_revenue:,.0f}", help="TS-09 · Synthetic")
c3.metric("Net Revenue (Rev − Cost)", f"${net_revenue:,.0f}")
c4.metric("Medicare Share", f"{medicare_share:.1f}%", help="Payer mix")

st.markdown("---")

# ── Section 2: Charts ─────────────────────────────────────────────────────
costs_sorted = costs.copy()
costs_sorted["month_name"] = pd.Categorical(costs_sorted["month_name"], categories=FY_MONTH_ORDER, ordered=True)
costs_sorted = costs_sorted.sort_values(["fiscal_year", "month_name"])
costs_sorted["month_label"] = costs_sorted["fiscal_year"].str[2:] + " " + costs_sorted["month_name"].astype(str).str[:3]

r1c1, r1c2 = st.columns(2)

with r1c1:
    st.markdown("##### Monthly cost trend (TS-08)")
    fig = trend_line(costs_sorted, x_col="month_label", y_col="total_monthly_cost",
                     title=None, color=PSH_TEAL, y_title="USD", x_title="Month")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<p class='poc-note'>PoC — Synthetic data only. For illustrative purposes.</p>", unsafe_allow_html=True)

with r1c2:
    st.markdown("##### Downstream revenue by month (TS-09)")
    fig = bar_chart(costs_sorted, x_col="month_label", y_col="downstream_revenue",
                    title=None, color=PSH_NAVY, y_title="USD", x_title="Month")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<p class='poc-note'>PoC — Synthetic data only. For illustrative purposes.</p>", unsafe_allow_html=True)

r2c1, r2c2 = st.columns(2)

with r2c1:
    st.markdown("##### Payer category distribution")
    payer = df["payer_category"].value_counts().reset_index()
    payer.columns = ["payer", "count"]
    st.plotly_chart(pie_chart(payer, values_col="count", names_col="payer", title=None), use_container_width=True)

with r2c2:
    st.markdown("##### Revenue vs Cost overlay")
    fig = overlay_lines(costs_sorted, x_col="month_label",
                        y_cols=["downstream_revenue", "total_monthly_cost"],
                        title=None, colors=[PSH_NAVY, PSH_TEAL],
                        y_title="USD", x_title="Month")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<p class='poc-note'>PoC — Synthetic data only. For illustrative purposes.</p>", unsafe_allow_html=True)

st.markdown("##### Reimbursement amount distribution")
fig = histogram(df.dropna(subset=["reimbursement_amount"]), col="reimbursement_amount",
                title=None, bins=25, x_title="USD")
st.plotly_chart(fig, use_container_width=True)
st.markdown("<p class='poc-note'>PoC — Synthetic data only. For illustrative purposes.</p>", unsafe_allow_html=True)
