"""Page 3 — Operational Performance (Phase 2 KPIs)."""

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
    bar_chart,
    heatmap,
    pie_chart,
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
from utils.theme import FY_MONTH_ORDER, PSH_NAVY, PSH_TEAL, get_global_css  # noqa: E402

st.set_page_config(page_title="Operational Performance", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
st.markdown(get_global_css(), unsafe_allow_html=True)

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("app.py")

render_sidebar()

DATA_DIR = os.path.join(PROJECT_DIR, "data")


@st.cache_data
def load_patients():
    df = pd.read_csv(os.path.join(DATA_DIR, "telestroke_synthetic.csv"))
    df["ed_arrival_dt"] = pd.to_datetime(df["ed_arrival_dt"], errors="coerce")
    df["consult_signed_dt"] = pd.to_datetime(df["consult_signed_dt"], errors="coerce")
    return df


df_full = load_patients()

st.markdown("<h1>Operational Performance <span class='badge badge-phase2'>Phase 2</span></h1>", unsafe_allow_html=True)
st.caption("Door-to-Needle detail, encounter mix, time-of-day patterns, and decision-to-administration delays.")

df = render_telestroke_filters(df_full)

if not len(df):
    st.warning("No records match the current filters.")
    st.stop()

df["month_name"] = pd.Categorical(df["month_name"], categories=FY_MONTH_ORDER, ordered=True)
df = df.sort_values(["fiscal_year", "month_name"])

# ── Section 1: KPI tiles ──────────────────────────────────────────────────
av = df[df["encounter_type"] == "Audio/Video"]
eligible = av[av["thrombolysis_eligibility_indicator"] == "Yes"]
median_d2n = eligible["door_to_needle_time_minutes"].median()
response_outlier_rate = (df["response_time_outlier_flag"] == "Yes").mean() * 100

# Avg consult duration = call_to_provider -> consult_signed in minutes
call_dt = pd.to_datetime(df["call_to_provider_dt"], errors="coerce")
signed_dt = df["consult_signed_dt"]
duration = (signed_dt - call_dt).dt.total_seconds() / 60.0
avg_consult_duration = duration.mean()

# ED vs Inpatient split — synthetic proxy using admit_status
ed_share = (df["admit_status"].isin(["Discharged", "Observation"])).mean() * 100
inpatient_share = 100 - ed_share

response_outlier_rate_frac = response_outlier_rate / 100.0

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card("door_to_needle_median_minutes", median_d2n)
with k2:
    render_kpi_card("response_time_outlier_rate", response_outlier_rate_frac)
with k3:
    render_gray_card(
        "Avg Consult Duration",
        f"{avg_consult_duration:.1f} min" if pd.notna(avg_consult_duration) else "—",
        note="TS-20 · Call-to-provider to consult-signed — trending only",
    )
with k4:
    render_gray_card(
        "ED vs Inpatient Mix",
        f"{ed_share:.0f}% / {inpatient_share:.0f}%",
        note="TS-17 · Proxy from admit status — trending only",
    )

st.markdown("---")

# ── Section 2: Charts ─────────────────────────────────────────────────────
r1c1, r1c2 = st.columns(2)

with r1c1:
    st.markdown("##### Encounter type breakdown")
    et = df["encounter_type"].value_counts().reset_index()
    et.columns = ["encounter_type", "count"]
    st.plotly_chart(pie_chart(et, values_col="count", names_col="encounter_type", title=None), use_container_width=True)

with r1c2:
    st.markdown("##### Phone vs Audio/Video monthly trend (TS-10 Phase 2)")
    monthly = (
        df.groupby(["fiscal_year", "month_name", "month_number", "encounter_type"]).size().reset_index(name="n")
        .pivot_table(index=["fiscal_year", "month_name", "month_number"], columns="encounter_type", values="n", fill_value=0)
        .reset_index()
        .sort_values(["fiscal_year", "month_number"])
    )
    monthly["month_label"] = monthly["fiscal_year"].str[2:] + " " + monthly["month_name"].str[:3]
    encounter_cols = [c for c in ["Audio/Video", "Phone", "Reg-No Consult"] if c in monthly.columns]
    st.plotly_chart(
        stacked_bar(monthly, x_col="month_label", y_cols=encounter_cols, title=None,
                    colors=[PSH_NAVY, PSH_TEAL, "#D6E4F0"], y_title="Consults"),
        use_container_width=True,
    )

r2c1, r2c2 = st.columns(2)

with r2c1:
    st.markdown("##### Volume by site (TS-11)")
    site = df.groupby("facility").size().reset_index(name="consults").sort_values("consults", ascending=True)
    st.plotly_chart(
        bar_chart(site, x_col="consults", y_col="facility", title=None,
                  orientation="h", x_title="Consults", y_title="Facility"),
        use_container_width=True,
    )

with r2c2:
    st.markdown("##### Time-of-day analysis heatmap (TS-18)")
    tod = df.groupby(["time_of_day_block", "facility"]).size().reset_index(name="consults")
    block_order = ["Morning (8a-4p)", "Evening (4p-12a)", "Night (12a-8a)"]
    tod["time_of_day_block"] = pd.Categorical(tod["time_of_day_block"], categories=block_order, ordered=True)
    tod = tod.sort_values("time_of_day_block")
    fig = heatmap(tod, x_col="facility", y_col="time_of_day_block", value_col="consults", title=None,
                  x_title="Facility", y_title="Time block")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Peak alert volume hours should align with the consultant staffing model.")

r3c1, r3c2 = st.columns(2)

with r3c1:
    st.markdown("##### ED vs Inpatient side-by-side (TS-17)")
    df_ei = df.copy()
    df_ei["setting"] = np.where(df_ei["admit_status"] == "Admitted", "Inpatient", "ED")
    by_setting = df_ei.groupby("setting").size().reset_index(name="consults")
    st.plotly_chart(
        bar_chart(by_setting, x_col="setting", y_col="consults", title=None,
                  color=PSH_TEAL, x_title="Setting", y_title="Consults"),
        use_container_width=True,
    )
    st.caption("Synthetic proxy using admit_status.")

with r3c2:
    st.markdown("##### Flight vs Ground transport (TS-13 · estimated)")
    transferred = df[df["transfer_status"] == "Transferred"].copy()
    if len(transferred):
        np.random.seed(7)
        transferred["transport_mode"] = np.where(
            np.random.random(len(transferred)) < 0.30, "Flight", "Ground"
        )
        tt = transferred.groupby(["facility", "transport_mode"]).size().reset_index(name="n")
        tt_pivot = tt.pivot_table(index="facility", columns="transport_mode", values="n", fill_value=0).reset_index()
        cols = [c for c in ["Flight", "Ground"] if c in tt_pivot.columns]
        st.plotly_chart(
            stacked_bar(tt_pivot, x_col="facility", y_cols=cols, title=None,
                        colors=[PSH_NAVY, PSH_TEAL], y_title="Transfers"),
            use_container_width=True,
        )
        st.caption("Transport mode is a synthetic estimate for PoC purposes only.")
    else:
        st.info("No transferred cases in the current filter.")

# ── Section 3: Decision-to-Administration (TS-16) ────────────────────────
st.markdown("---")
st.markdown("##### Decision-to-Administration Delay Tracking (TS-16)")

if len(eligible):
    trend = (
        eligible.groupby(["fiscal_year", "month_name", "month_number"])["decision_to_administration_minutes"].median().reset_index()
    )
    trend = trend.sort_values(["fiscal_year", "month_number"])
    fig = trend_line(
        trend, x_col="month_name", y_col="decision_to_administration_minutes",
        title=None,
        category_orders={"month_name": FY_MONTH_ORDER},
        y_title="Median minutes", x_title="Month",
        color_col="fiscal_year",
    )
    fig = add_benchmark_line(fig, 5, "Target: ≤5 min")
    st.plotly_chart(fig, use_container_width=True)

    site_table = (
        eligible.groupby("facility")
        .agg(median_min=("decision_to_administration_minutes", "median"),
             n=("decision_to_administration_minutes", "count"))
        .reset_index()
        .sort_values("median_min")
    )
    site_table["status"] = site_table["median_min"].apply(lambda v: "Above target" if v > 5 else "Meeting target")
    site_table.columns = ["Facility", "Median min", "Eligible cases", "Status"]

    def _color(row):
        if row["Status"] == "Above target":
            return ["background-color: #FEE2E2"] * len(row)
        return ["background-color: #DCFCE7"] * len(row)

    st.dataframe(site_table.style.apply(_color, axis=1), use_container_width=True, hide_index=True)
    st.caption("Outliers (median > 5 min benchmark) highlighted in red.")
else:
    st.info("No eligible cases for decision-to-administration analysis.")

# ── Performance Targets reference panel ──────────────────────────────────
median_d2a_for_panel = (
    eligible["decision_to_administration_minutes"].median()
    if len(eligible) else None
)
render_targets_panel([
    {"target_key": "door_to_needle_median_minutes",      "current_value": median_d2n},
    {"target_key": "response_time_outlier_rate",         "current_value": response_outlier_rate_frac},
    {"target_key": "decision_to_administration_minutes", "current_value": median_d2a_for_panel},
])
