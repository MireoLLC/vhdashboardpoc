"""Page 1 — Phase 1 Overview KPIs (TS-01, TS-02, TS-04, TS-05, TS-06, TS-07, TS-10)."""

import os
import sys

import numpy as np
import pandas as pd
import streamlit as st

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from utils.charts import bar_chart, histogram, stacked_bar, trend_line  # noqa: E402
from utils.filters import empty_state_check, render_filters  # noqa: E402
from utils.theme import FY_MONTH_ORDER, PAGE_CSS, PSH_LTBLUE, PSH_NAVY, PSH_RED, PSH_TEAL  # noqa: E402

st.set_page_config(page_title="Phase 1 Overview", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
st.markdown(PAGE_CSS, unsafe_allow_html=True)

DATA_DIR = os.path.join(PROJECT_DIR, "data")


@st.cache_data
def load_patients():
    df = pd.read_csv(os.path.join(DATA_DIR, "telestroke_synthetic.csv"))
    df["ed_arrival_dt"] = pd.to_datetime(df["ed_arrival_dt"], errors="coerce")
    return df


@st.cache_data
def load_cart():
    return pd.read_csv(os.path.join(DATA_DIR, "cart_uptime_synthetic.csv"))


df_full = load_patients()
cart_df = load_cart()
df = render_filters(df_full)

st.markdown(f"<h1>Phase 1 Overview</h1>", unsafe_allow_html=True)
st.caption("Foundational Telestroke KPIs — door-to-needle, neurologist response, cart uptime, treatment timing.")

if not empty_state_check(df):
    st.stop()

# ── Section 1: KPI tiles ─────────────────────────────────────────────────
av = df[df["encounter_type"] == "Audio/Video"]
eligible = av[av["thrombolysis_eligibility_indicator"] == "Yes"]

d2n_compliance = (eligible["door_to_needle_compliant"] == "Yes").mean() * 100 if len(eligible) else 0.0
median_d2neuro = df["door_to_neurologist_minutes"].median()

# Stroke alerts per month average across the selection
alerts_per_month = (
    df.groupby(["fiscal_year", "month_name"]).size().mean() if len(df) else 0
)

# Cart uptime filtered to the same fiscal years and facilities as selected df
cart_filt = cart_df[
    cart_df["fiscal_year"].isin(df["fiscal_year"].unique()) & cart_df["facility"].isin(df["facility"].unique())
]
cart_uptime = cart_filt["cart_uptime_pct"].mean() if len(cart_filt) else 0.0

median_d2cart = df["door_to_cart_minutes"].median()
median_neuro_decision = av["neurologist_to_decision_minutes"].median()
median_decision_tnk = eligible["decision_to_administration_minutes"].median()

k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
k1.metric("D2N Compliance (≤60 min)", f"{d2n_compliance:.1f}%", help="TS-01 · Benchmark ≥85% (AHA/ASA)")
k2.metric("Median Door-to-Neurologist", f"{median_d2neuro:.1f} min" if pd.notna(median_d2neuro) else "—", help="TS-02 · Benchmark ≤30 min")
k3.metric("Avg Stroke Alerts / Month", f"{alerts_per_month:.0f}", help="TS-04 · Volume reference")
k4.metric("Cart Uptime", f"{cart_uptime:.1f}%", help="TS-05 · Benchmark ≥99% SLA")
k5.metric("Median Door-to-Cart", f"{median_d2cart:.1f} min" if pd.notna(median_d2cart) else "—", help="TS-06 · Benchmark ≤15 min")
k6.metric("Median Neuro-to-Decision", f"{median_neuro_decision:.1f} min" if pd.notna(median_neuro_decision) else "—", help="TS-07 · Benchmark ≤20 min · A/V only")
k7.metric("Median Decision-to-TNK", f"{median_decision_tnk:.1f} min" if pd.notna(median_decision_tnk) else "—", help="TS-10 · Benchmark ≤5 min · Eligible only")

st.markdown("---")

# ── Section 2: Row 1 ─────────────────────────────────────────────────────
r1c1, r1c2 = st.columns(2)

with r1c1:
    st.markdown("##### Monthly stroke alert volume (TS-04)")
    volume = df.groupby(["fiscal_year", "month_name", "month_number"]).size().reset_index(name="alerts")
    volume = volume.sort_values(["fiscal_year", "month_number"])
    fig = bar_chart(
        volume, x_col="month_name", y_col="alerts",
        title=None, color_col="fiscal_year",
        category_orders={"month_name": FY_MONTH_ORDER},
        x_title="Month (fiscal-year order)", y_title="Alerts",
    )
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    st.markdown("##### Door-to-Needle compliance trend (TS-01)")
    if len(eligible):
        trend = (
            eligible.assign(month=eligible["month_name"], compliant=(eligible["door_to_needle_compliant"] == "Yes").astype(int))
            .groupby(["fiscal_year", "month_name", "month_number"])
            .agg(compliance_pct=("compliant", "mean"), n=("compliant", "size"))
            .reset_index()
        )
        trend["compliance_pct"] = trend["compliance_pct"] * 100
        trend = trend.sort_values(["fiscal_year", "month_number"])
        fig = trend_line(
            trend, x_col="month_name", y_col="compliance_pct",
            title=None, benchmark=85,
            category_orders={"month_name": FY_MONTH_ORDER},
            y_title="Compliance %", x_title="Month",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Audio/Video, thrombolysis-eligible cases only.")
    else:
        st.info("No eligible Audio/Video cases in the current filter.")

# ── Section 3: Row 2 ─────────────────────────────────────────────────────
r2c1, r2c2 = st.columns(2)

with r2c1:
    st.markdown("##### Door-to-Neurologist distribution (TS-02)")
    fig = histogram(df.dropna(subset=["door_to_neurologist_minutes"]),
                    col="door_to_neurologist_minutes", title=None,
                    bins=25, benchmark=30, x_title="Minutes")
    st.plotly_chart(fig, use_container_width=True)

with r2c2:
    st.markdown("##### Door-to-Cart trend (TS-06)")
    cart_trend = (
        df.groupby(["fiscal_year", "month_name", "month_number"])["door_to_cart_minutes"].median().reset_index()
    )
    cart_trend = cart_trend.sort_values(["fiscal_year", "month_number"])
    fig = trend_line(
        cart_trend, x_col="month_name", y_col="door_to_cart_minutes",
        title=None, benchmark=15,
        category_orders={"month_name": FY_MONTH_ORDER},
        y_title="Median minutes", x_title="Month",
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Section 4: Row 3 ─────────────────────────────────────────────────────
r3c1, r3c2 = st.columns(2)

with r3c1:
    st.markdown("##### Neurologist-to-Decision trend (TS-07)")
    if len(av):
        nd = (
            av.groupby(["fiscal_year", "month_name", "month_number"])["neurologist_to_decision_minutes"].median().reset_index()
        )
        nd = nd.sort_values(["fiscal_year", "month_number"])
        fig = trend_line(
            nd, x_col="month_name", y_col="neurologist_to_decision_minutes",
            title=None, benchmark=20,
            category_orders={"month_name": FY_MONTH_ORDER},
            y_title="Median minutes", x_title="Month",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Audio/Video consults only.")
    else:
        st.info("No Audio/Video consults in the current filter.")

with r3c2:
    st.markdown("##### Decision-to-TNK by facility (TS-10)")
    if len(eligible):
        by_fac = (
            eligible.groupby("facility")["decision_to_administration_minutes"].median().reset_index()
            .sort_values("decision_to_administration_minutes")
        )
        fig = bar_chart(
            by_fac, x_col="facility", y_col="decision_to_administration_minutes",
            title=None, benchmark=5, color=PSH_TEAL,
            x_title="Facility", y_title="Median minutes",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Eligible cases only.")
    else:
        st.info("No eligible cases in the current filter.")

# ── Section 5: D2N threshold buckets (full width) ─────────────────────────
st.markdown("---")
st.markdown("##### Door-to-Needle distribution by threshold bucket")

if len(eligible):
    def bucket(m):
        if pd.isna(m):
            return None
        if m < 30:
            return "<30 min"
        if m < 45:
            return "30-45 min"
        if m <= 60:
            return "45-60 min"
        return ">60 min"

    el = eligible.copy()
    el["d2n_bucket"] = el["door_to_needle_time_minutes"].apply(bucket)
    el = el.dropna(subset=["d2n_bucket"])

    buckets_order = ["<30 min", "30-45 min", "45-60 min", ">60 min"]
    grouped = (
        el.groupby(["fiscal_year", "month_name", "month_number", "d2n_bucket"]).size().reset_index(name="n")
    )
    pivot = grouped.pivot_table(
        index=["fiscal_year", "month_name", "month_number"],
        columns="d2n_bucket",
        values="n",
        fill_value=0,
    ).reset_index()
    # Ensure all bucket columns exist
    for b in buckets_order:
        if b not in pivot.columns:
            pivot[b] = 0
    pivot["_total"] = pivot[buckets_order].sum(axis=1)
    for b in buckets_order:
        pivot[b] = pivot[b] / pivot["_total"].replace(0, np.nan)
    pivot = pivot.fillna(0).sort_values(["fiscal_year", "month_number"])
    pivot["month_label"] = pivot["fiscal_year"].str[2:] + " " + pivot["month_name"].str[:3]

    fig = stacked_bar(
        pivot,
        x_col="month_label",
        y_cols=buckets_order,
        title=None,
        colors=[PSH_NAVY, PSH_TEAL, PSH_LTBLUE, PSH_RED],
        percent=True,
        x_title="Month (FY · short)",
        y_title="Share of eligible cases",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No eligible cases for threshold bucket analysis.")
