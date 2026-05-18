"""Penn State Health Telestroke Dashboard — entry point.

Loads the synthetic CSV (running the generator on first launch if missing),
renders the shared sidebar filters, and shows a landing page with four
summary KPI cards plus orientation copy.
"""

import os
import subprocess
import sys
from datetime import datetime

import pandas as pd
import streamlit as st

from utils.filters import render_filters
from utils.theme import PAGE_CSS, PSH_NAVY, PSH_TEAL

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
PATIENTS_CSV = os.path.join(DATA_DIR, "telestroke_synthetic.csv")
CART_CSV = os.path.join(DATA_DIR, "cart_uptime_synthetic.csv")
COSTS_CSV = os.path.join(DATA_DIR, "monthly_cost_synthetic.csv")

st.set_page_config(
    page_title="PSH Telestroke Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _ensure_data():
    if not (os.path.exists(PATIENTS_CSV) and os.path.exists(CART_CSV) and os.path.exists(COSTS_CSV)):
        with st.spinner("Generating synthetic data (first-run only)..."):
            subprocess.run([sys.executable, os.path.join(PROJECT_DIR, "generate_data.py")], check=True)


@st.cache_data
def load_patients() -> pd.DataFrame:
    df = pd.read_csv(PATIENTS_CSV)
    datetime_cols = [
        "ed_arrival_dt",
        "stroke_alert_initiation_dt",
        "last_known_normal_dt",
        "call_to_provider_dt",
        "provider_response_dt",
        "neurologist_evaluation_start_dt",
        "treatment_decision_dt",
        "thrombolysis_administration_dt",
        "order_entry_dt",
        "consult_signed_dt",
        "depart_dt",
    ]
    for c in datetime_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


@st.cache_data
def load_cart() -> pd.DataFrame:
    return pd.read_csv(CART_CSV)


@st.cache_data
def load_costs() -> pd.DataFrame:
    return pd.read_csv(COSTS_CSV)


_ensure_data()
st.markdown(PAGE_CSS, unsafe_allow_html=True)

df = load_patients()
filtered = render_filters(df)

# ── Landing page ─────────────────────────────────────────────────────────
st.markdown(f"<h1 style='color:{PSH_NAVY}; margin-bottom:0;'>PSH Telestroke Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    f"<p style='color:{PSH_TEAL}; font-size:18px; margin-top:0;'>Art of the Possible — Synthetic Data PoC</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Summary KPI cards
total_consults = len(filtered)
eligible_av = filtered[(filtered["encounter_type"] == "Audio/Video") & (filtered["thrombolysis_eligibility_indicator"] == "Yes")]
treated = eligible_av[eligible_av["treatment_administered"] == "Yes"]

if len(eligible_av):
    d2n_compliance = (eligible_av["door_to_needle_compliant"] == "Yes").mean() * 100
    treatment_rate = (len(treated) / len(eligible_av)) * 100
else:
    d2n_compliance = 0.0
    treatment_rate = 0.0

median_response = filtered["provider_response_minutes"].median() if len(filtered) else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Consults", f"{total_consults:,}")
c2.metric("D2N Compliance (≤60 min)", f"{d2n_compliance:.1f}%", help="Eligible Audio/Video cases. Benchmark: ≥85%")
c3.metric("Median Response Time", f"{median_response:.1f} min", help="Call-to-provider to provider-response. Benchmark: ≤15 min")
c4.metric("Treatment Rate", f"{treatment_rate:.1f}%", help="Treated / eligible Audio/Video cases")

st.markdown("---")

# Description and nav
st.markdown(
    """
    ### About this dashboard

    This proof-of-concept demonstrates how the Penn State Health Telestroke program could
    track Phase 1 and Phase 2 KPIs in a single interactive dashboard. All records shown
    here are **synthetic** — no real patient data is present.

    Use the **sidebar filters** to drill into a fiscal year, facility, encounter type,
    date range, or individual consultant. Filters apply to every page.

    ### Pages

    - **Phase 1 Overview** — door-to-needle, door-to-neurologist, cart uptime, response times
    - **Clinical Outcomes** *(Phase 2)* — treatment, LVO detection, readmissions, mRS, outlier exclusion
    - **Operational Performance** *(Phase 2)* — D2N detail, time-of-day patterns, decision-to-administration delays
    - **Financial** *(Phase 2)* — cost of delivery, downstream revenue, payer mix
    - **Provider Performance** *(Phase 2 — restricted)* — per-consultant scorecards
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"<p class='poc-note'>Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
    unsafe_allow_html=True,
)
