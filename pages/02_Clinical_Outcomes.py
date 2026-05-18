"""Page 2 — Clinical Outcomes (Phase 2 KPIs)."""

import os
import sys

import pandas as pd
import streamlit as st

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from utils.charts import bar_chart, grouped_bar, histogram, pie_chart, stacked_bar, trend_line  # noqa: E402
from utils.filters import render_telestroke_filters  # noqa: E402
from utils.sidebar import render_sidebar  # noqa: E402
from utils.theme import FY_MONTH_ORDER, PSH_NAVY, PSH_TEAL, get_global_css  # noqa: E402

st.set_page_config(page_title="Clinical Outcomes", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
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


df_full = load_patients()

st.markdown("<h1>Clinical Outcomes <span class='badge badge-phase2'>Phase 2</span></h1>", unsafe_allow_html=True)
st.caption("Treatment, disposition, mRS, transfers, and outlier exclusion analysis.")

df = render_telestroke_filters(df_full)

if not len(df):
    st.warning("No records match the current filters.")
    st.stop()

df["month_name"] = pd.Categorical(df["month_name"], categories=FY_MONTH_ORDER, ordered=True)
df = df.sort_values(["fiscal_year", "month_name"])

# ── Section 1: KPI tiles ──────────────────────────────────────────────────
av = df[df["encounter_type"] == "Audio/Video"]
eligible = av[av["thrombolysis_eligibility_indicator"] == "Yes"]
treated = eligible[eligible["treatment_administered"] == "Yes"]

treatment_rate = (len(treated) / len(eligible) * 100) if len(eligible) else 0.0
lvo_rate = (df["lvo_indicator"] == "Yes").mean() * 100
readmit_rate = (df["thirty_day_readmission"] == "Yes").mean() * 100
icu_rate = (df["icu_admission"] == "Yes").mean() * 100
nihss_compliance = (df["nihss_documentation_compliance"] == "Yes").mean() * 100
consent_completion = (df["consent_form_completed"] == "Yes").mean() * 100

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Treatment Rate", f"{treatment_rate:.1f}%", help="Treated / eligible Audio-Video cases")
c2.metric("LVO Detection Rate", f"{lvo_rate:.1f}%")
c3.metric("30-Day Readmission", f"{readmit_rate:.1f}%")
c4.metric("ICU Admission", f"{icu_rate:.1f}%")
c5.metric("NIHSS Documentation", f"{nihss_compliance:.1f}%")
c6.metric("Consent Completion", f"{consent_completion:.1f}%")

st.markdown("---")

# ── Section 2: Charts ─────────────────────────────────────────────────────
r1c1, r1c2 = st.columns(2)

with r1c1:
    st.markdown("##### Stroke diagnosis distribution")
    diag = df["stroke_diagnosis"].value_counts().reset_index()
    diag.columns = ["diagnosis", "count"]
    st.plotly_chart(pie_chart(diag, values_col="count", names_col="diagnosis", title=None), use_container_width=True)

with r1c2:
    st.markdown("##### Discharge disposition")
    disp = df["discharge_destination"].value_counts().reset_index()
    disp.columns = ["destination", "count"]
    disp = disp.sort_values("count", ascending=False)
    st.plotly_chart(
        bar_chart(disp, x_col="destination", y_col="count", title=None, x_title="Destination", y_title="Patients"),
        use_container_width=True,
    )

r2c1, r2c2 = st.columns(2)

with r2c1:
    st.markdown("##### Pre-mRS vs Discharge mRS")
    pre_counts = df["pre_mrs_score"].value_counts().sort_index()
    dc_counts = df["discharge_mrs_score"].value_counts().sort_index()
    mrs_compare = pd.DataFrame({
        "mRS score": list(range(7)),
        "Pre-stroke": [int(pre_counts.get(i, 0)) for i in range(7)],
        "Discharge": [int(dc_counts.get(i, 0)) for i in range(7)],
    })
    st.plotly_chart(
        grouped_bar(mrs_compare, x_col="mRS score", y_cols=["Pre-stroke", "Discharge"], title=None,
                    colors=[PSH_NAVY, PSH_TEAL], y_title="Patients"),
        use_container_width=True,
    )

with r2c2:
    st.markdown("##### NIHSS score distribution")
    st.plotly_chart(
        histogram(df.dropna(subset=["nihss_score"]), col="nihss_score", title=None,
                  bins=22, x_title="NIHSS score"),
        use_container_width=True,
    )

r3c1, r3c2 = st.columns(2)

with r3c1:
    st.markdown("##### Transfer volume by facility (TS-12)")
    transfers = df[df["transfer_status"] == "Transferred"].groupby("facility").agg(
        total=("mrn", "size"),
        lvo=("lvo_indicator", lambda x: (x == "Yes").sum()),
    ).reset_index()
    transfers["non_lvo"] = transfers["total"] - transfers["lvo"]
    transfers = transfers.sort_values("total", ascending=False)
    st.plotly_chart(
        stacked_bar(transfers, x_col="facility", y_cols=["lvo", "non_lvo"], title=None,
                    colors=[PSH_NAVY, PSH_TEAL], y_title="Transferred patients"),
        use_container_width=True,
    )
    st.caption("Stacked: LVO vs non-LVO transfers.")

with r3c2:
    st.markdown("##### 90-Day mRS distribution <span class='phase2-badge'>Phase 2</span>", unsafe_allow_html=True)
    mrs90 = df.dropna(subset=["ninety_day_mrs_score"])
    missing_pct = (1 - len(mrs90) / len(df)) * 100 if len(df) else 0
    if len(mrs90):
        st.plotly_chart(
            histogram(mrs90, col="ninety_day_mrs_score", title=None, bins=7, x_title="90-day mRS"),
            use_container_width=True,
        )
        st.caption(f"Note: {missing_pct:.0f}% of records have no 90-day mRS score (partial Phase 2 data).")
    else:
        st.info("No 90-day mRS data available for the current filter.")

# ── Section 3: Outlier Exclusion (TS-22) ─────────────────────────────────
st.markdown("---")
st.markdown("##### Outlier Exclusion Analysis (TS-22)")

if len(eligible):
    raw_d2n = (eligible["door_to_needle_compliant"] == "Yes").mean() * 100
    adjusted_pool = eligible[eligible["outlier_exclusion_flag"] != "Yes"]
    adjusted_d2n = (
        (adjusted_pool["door_to_needle_compliant"] == "Yes").mean() * 100
        if len(adjusted_pool) else 0.0
    )

    oc1, oc2, oc3 = st.columns(3)
    oc1.metric("Raw D2N compliance", f"{raw_d2n:.1f}%")
    oc2.metric("Adjusted D2N compliance", f"{adjusted_d2n:.1f}%", delta=f"{adjusted_d2n - raw_d2n:+.1f} pp")
    oc3.metric("Cases excluded", f"{(eligible['outlier_exclusion_flag'] == 'Yes').sum()}", help="Outlier exclusion flag = Yes")

    st.markdown("**Outlier exception reasons**")
    reasons = eligible[eligible["outlier_exclusion_flag"] == "Yes"]["outlier_exception_reason"].value_counts().reset_index()
    reasons.columns = ["Reason", "Count"]
    if len(reasons):
        st.dataframe(reasons, use_container_width=True, hide_index=True)
    else:
        st.caption("No outlier-excluded cases in this filter.")

    show_adjusted = st.toggle("Show adjusted (outlier-excluded) trend instead of raw", value=False)
    pool = adjusted_pool if show_adjusted else eligible
    if len(pool):
        trend = (
            pool.assign(compliant=(pool["door_to_needle_compliant"] == "Yes").astype(int))
            .groupby(["fiscal_year", "month_name", "month_number"])
            .agg(compliance_pct=("compliant", "mean"))
            .reset_index()
        )
        trend["compliance_pct"] = trend["compliance_pct"] * 100
        trend = trend.sort_values(["fiscal_year", "month_number"])
        fig = trend_line(
            trend, x_col="month_name", y_col="compliance_pct",
            title=None, benchmark=85,
            category_orders={"month_name": FY_MONTH_ORDER},
            y_title="Compliance %", x_title="Month",
            color=PSH_TEAL,
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No eligible Audio/Video cases for outlier analysis.")
