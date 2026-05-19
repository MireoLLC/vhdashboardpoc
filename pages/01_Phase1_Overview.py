"""Page 1 — Phase 1 Overview KPIs (TS-01, TS-02, TS-04, TS-05, TS-06, TS-07, TS-10)."""

import os
import sys

import numpy as np
import pandas as pd
import streamlit as st

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from utils.charts import (  # noqa: E402
    add_benchmark_line,
    add_benchmark_vline,
    bar_chart,
    histogram,
    stacked_bar,
    trend_line,
)
from utils.filters import render_telestroke_filters  # noqa: E402
from utils.sidebar import render_sidebar  # noqa: E402
from utils.targets import (  # noqa: E402
    render_gray_card,
    render_kpi_card,
    render_targets_panel,
)
from utils.theme import FY_MONTH_ORDER, PSH_LTBLUE, PSH_NAVY, PSH_RED, PSH_TEAL, get_global_css  # noqa: E402

st.set_page_config(page_title="Phase 1 Overview", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
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
def load_cart():
    return pd.read_csv(os.path.join(DATA_DIR, "cart_uptime_synthetic.csv"))


df_full = load_patients()
cart_df = load_cart()

st.markdown(f"<h1>Phase 1 Overview</h1>", unsafe_allow_html=True)
st.caption("Foundational Telestroke KPIs — door-to-needle, neurologist response, cart uptime, treatment timing.")

df = render_telestroke_filters(df_full)

if not len(df):
    st.warning("No records match the current filters.")
    st.stop()

df["month_name"] = pd.Categorical(df["month_name"], categories=FY_MONTH_ORDER, ordered=True)
df = df.sort_values(["fiscal_year", "month_name"])

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

# Fractions for traffic-light grading (existing display variables stay in pct
# form so the rest of the page is unchanged).
d2n_compliance_frac = d2n_compliance / 100.0
cart_uptime_frac    = cart_uptime / 100.0

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card("door_to_needle_compliance_60", d2n_compliance_frac)
with k2:
    render_kpi_card("door_to_neurologist_minutes", median_d2neuro)
with k3:
    render_gray_card(
        "Avg Stroke Alerts / Month",
        f"{alerts_per_month:.0f}",
        note="TS-04 · Trending volume metric — no absolute target",
    )
with k4:
    render_kpi_card("cart_uptime", cart_uptime_frac)

k5, k6, k7, _ = st.columns(4)
with k5:
    render_kpi_card("door_to_cart_minutes", median_d2cart)
with k6:
    render_kpi_card("neurologist_to_decision_minutes", median_neuro_decision)
with k7:
    render_kpi_card("decision_to_administration_minutes", median_decision_tnk)

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
            title=None,
            category_orders={"month_name": FY_MONTH_ORDER},
            y_title="Compliance %", x_title="Month",
            color_col="fiscal_year",
        )
        fig = add_benchmark_line(fig, 85, "Target: ≥85% (AHA/ASA)")
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
                    bins=25, x_title="Minutes")
    fig = add_benchmark_vline(fig, 20, "Target: ≤20 min")
    st.plotly_chart(fig, use_container_width=True)

with r2c2:
    st.markdown("##### Door-to-Cart trend (TS-06)")
    cart_trend = (
        df.groupby(["fiscal_year", "month_name", "month_number"])["door_to_cart_minutes"].median().reset_index()
    )
    cart_trend = cart_trend.sort_values(["fiscal_year", "month_number"])
    fig = trend_line(
        cart_trend, x_col="month_name", y_col="door_to_cart_minutes",
        title=None,
        category_orders={"month_name": FY_MONTH_ORDER},
        y_title="Median minutes", x_title="Month",
        color_col="fiscal_year",
    )
    fig = add_benchmark_line(fig, 15, "Target: ≤15 min")
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
            title=None,
            category_orders={"month_name": FY_MONTH_ORDER},
            y_title="Median minutes", x_title="Month",
            color_col="fiscal_year",
        )
        fig = add_benchmark_line(fig, 20, "Target: ≤20 min")
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
            title=None, color=PSH_TEAL,
            x_title="Facility", y_title="Median minutes",
        )
        fig = add_benchmark_line(fig, 5, "Target: ≤5 min")
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
    # month_name is Categorical further up the page; convert to string here so
    # the downstream pivot_table + fillna(0) doesn't fail with "Cannot setitem
    # on a Categorical with a new category (0)".
    el["month_name"] = el["month_name"].astype(str)
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

# ── Performance Targets reference panel ──────────────────────────────────
render_targets_panel([
    {"target_key": "door_to_needle_compliance_60",       "current_value": d2n_compliance_frac},
    {"target_key": "door_to_neurologist_minutes",        "current_value": median_d2neuro},
    {"target_key": "cart_uptime",                        "current_value": cart_uptime_frac},
    {"target_key": "door_to_cart_minutes",               "current_value": median_d2cart},
    {"target_key": "neurologist_to_decision_minutes",    "current_value": median_neuro_decision},
    {"target_key": "decision_to_administration_minutes", "current_value": median_decision_tnk},
])
