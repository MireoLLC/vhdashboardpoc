"""Page 5 — Provider Performance (Phase 2 KPIs · restricted in production)."""

import os
import sys

import pandas as pd
import streamlit as st

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from utils.charts import add_benchmark_line, overlay_lines  # noqa: E402
from utils.filters import render_telestroke_filters  # noqa: E402
from utils.sidebar import render_sidebar  # noqa: E402
from utils.targets import (  # noqa: E402
    get_traffic_light,
    get_traffic_light_emoji,
    render_kpi_card,
    render_targets_panel,
)
from utils.theme import FY_MONTH_ORDER, PSH_NAVY, PSH_TEAL, get_global_css  # noqa: E402

st.set_page_config(page_title="Provider Performance", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
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
    df["call_to_provider_dt"] = pd.to_datetime(df["call_to_provider_dt"], errors="coerce")
    return df


df_full = load_patients()

st.markdown("<h1>Provider Performance <span class='badge badge-phase2'>Phase 2</span></h1>", unsafe_allow_html=True)
st.warning(
    "In production, this page will require restricted access. Displayed here for PoC demonstration purposes only."
)
st.caption("Per-consultant scorecards and comparison.")

df = render_telestroke_filters(df_full)

if not len(df):
    st.warning("No records match the current filters.")
    st.stop()

df["month_name"] = pd.Categorical(df["month_name"], categories=FY_MONTH_ORDER, ordered=True)
df = df.sort_values(["fiscal_year", "month_name"])


def _provider_summary(d: pd.DataFrame) -> dict:
    av = d[d["encounter_type"] == "Audio/Video"]
    eligible = av[av["thrombolysis_eligibility_indicator"] == "Yes"]
    handle = (d["consult_signed_dt"] - d["call_to_provider_dt"]).dt.total_seconds() / 60.0
    return {
        "total_consults": len(d),
        "d2n_compliance_pct": (eligible["door_to_needle_compliant"] == "Yes").mean() * 100 if len(eligible) else float("nan"),
        "median_response_min": d["provider_response_minutes"].median(),
        "nihss_compliance_pct": (d["nihss_documentation_compliance"] == "Yes").mean() * 100,
        "consent_completion_pct": (d["consent_form_completed"] == "Yes").mean() * 100,
        "avg_handle_min": handle.mean(),
    }


# ── Section 1: Provider selector ──────────────────────────────────────────
providers = sorted(df["consultant_name"].dropna().unique().tolist())
selected = st.selectbox("Select consultant", providers, index=0 if providers else None)

selected_d2n_frac = None
selected_response_min = None
selected_nihss_frac = None
selected_consent_frac = None

if selected:
    pdf = df[df["consultant_name"] == selected]
    s = _provider_summary(pdf)

    selected_d2n_frac = (s["d2n_compliance_pct"] / 100.0) if pd.notna(s["d2n_compliance_pct"]) else None
    selected_response_min = s["median_response_min"] if pd.notna(s["median_response_min"]) else None
    selected_nihss_frac = s["nihss_compliance_pct"] / 100.0
    selected_consent_frac = s["consent_completion_pct"] / 100.0

    t1, t2, t3, t4 = st.columns(4)
    with t1:
        render_kpi_card("door_to_needle_compliance_60", selected_d2n_frac)
    with t2:
        render_kpi_card("door_to_neurologist_minutes", selected_response_min)
    with t3:
        render_kpi_card("nihss_documentation_compliance", selected_nihss_frac)
    with t4:
        render_kpi_card("consent_form_compliance", selected_consent_frac)
    st.caption(f"Volume: **{s['total_consults']:,}** consults · "
               f"Avg handle: **{s['avg_handle_min']:.1f} min**" if pd.notna(s['avg_handle_min']) else
               f"Volume: **{s['total_consults']:,}** consults")

st.markdown("---")

# ── Section 2: Comparison table (TS-19) ───────────────────────────────────
st.markdown("##### Provider comparison (TS-19)")

rows = []
for name in providers:
    s = _provider_summary(df[df["consultant_name"] == name])
    d2n_frac = (s["d2n_compliance_pct"] / 100.0) if pd.notna(s["d2n_compliance_pct"]) else None
    rows.append({
        "Status": get_traffic_light_emoji(get_traffic_light(d2n_frac, "door_to_needle_compliance_60")),
        "Provider": name,
        "Volume": s["total_consults"],
        "D2N Compliance %": round(s["d2n_compliance_pct"], 1) if pd.notna(s["d2n_compliance_pct"]) else None,
        "Median Response (min)": round(s["median_response_min"], 1) if pd.notna(s["median_response_min"]) else None,
        "Avg Handle (min)": round(s["avg_handle_min"], 1) if pd.notna(s["avg_handle_min"]) else None,
        "NIHSS Doc %": round(s["nihss_compliance_pct"], 1),
        "Consent %": round(s["consent_completion_pct"], 1),
    })

cmp_df = pd.DataFrame(rows)


def _cell_color(status_str):
    return {
        "green": "background-color: #DCFCE7",
        "amber": "background-color: #FEF3C7",
        "red":   "background-color: #FEE2E2",
        "gray":  "",
    }.get(status_str, "")


def _style(row):
    colors = ["" for _ in row]
    cols = list(row.index)

    def _set(col, target_key, value_for_grading):
        idx = cols.index(col)
        colors[idx] = _cell_color(get_traffic_light(value_for_grading, target_key))

    if pd.notna(row["D2N Compliance %"]):
        _set("D2N Compliance %", "door_to_needle_compliance_60", row["D2N Compliance %"] / 100.0)
    if pd.notna(row["Median Response (min)"]):
        _set("Median Response (min)", "door_to_neurologist_minutes", row["Median Response (min)"])
    if pd.notna(row["NIHSS Doc %"]):
        _set("NIHSS Doc %", "nihss_documentation_compliance", row["NIHSS Doc %"] / 100.0)
    if pd.notna(row["Consent %"]):
        _set("Consent %", "consent_form_compliance", row["Consent %"] / 100.0)
    return colors


st.dataframe(cmp_df.style.apply(_style, axis=1), use_container_width=True, hide_index=True)
st.caption("Status emoji reflects D2N compliance vs ≥85% target. "
           "Per-cell colors use the same target table as the KPI tiles "
           "(🟢 meeting · 🟡 within amber band · 🔴 missing target).")

# ── Section 3: Monthly trend for selected provider ────────────────────────
st.markdown("---")
st.markdown(f"##### Monthly trend — {selected}")

if selected:
    pdf = df[df["consultant_name"] == selected]
    eligible = pdf[(pdf["encounter_type"] == "Audio/Video") & (pdf["thrombolysis_eligibility_indicator"] == "Yes")]

    monthly_response = (
        pdf.groupby(["fiscal_year", "month_name"])["provider_response_minutes"].median().reset_index()
        .rename(columns={"provider_response_minutes": "median_response_min"})
    )
    if len(eligible):
        monthly_compliance = (
            eligible.assign(c=(eligible["door_to_needle_compliant"] == "Yes").astype(int))
            .groupby(["fiscal_year", "month_name"])["c"].mean().reset_index()
            .rename(columns={"c": "d2n_compliance_pct"})
        )
        monthly_compliance["d2n_compliance_pct"] *= 100
        merged = monthly_response.merge(monthly_compliance, on=["fiscal_year", "month_name"], how="left")
    else:
        merged = monthly_response.copy()
        merged["d2n_compliance_pct"] = None

    merged["month_name"] = pd.Categorical(merged["month_name"], categories=FY_MONTH_ORDER, ordered=True)
    merged = merged.sort_values(["fiscal_year", "month_name"])
    merged["month_label"] = merged["fiscal_year"].str[2:] + " " + merged["month_name"].astype(str).str[:3]

    if len(merged):
        fig = overlay_lines(
            merged.dropna(subset=["median_response_min"]),
            x_col="month_label",
            y_cols=["median_response_min", "d2n_compliance_pct"],
            title=None,
            colors=[PSH_NAVY, PSH_TEAL],
            x_title="Month",
            y_title="Min / %",
        )
        fig = add_benchmark_line(fig, 85, "D2N target: ≥85%")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Navy = median response (minutes) · Teal = D2N compliance (%)")
    else:
        st.info("Not enough data for a trend on this provider in the current filter.")

# ── Performance Targets reference panel ──────────────────────────────────
render_targets_panel([
    {"target_key": "door_to_needle_compliance_60",   "current_value": selected_d2n_frac},
    {"target_key": "door_to_neurologist_minutes",    "current_value": selected_response_min},
    {"target_key": "nihss_documentation_compliance", "current_value": selected_nihss_frac},
    {"target_key": "consent_form_compliance",        "current_value": selected_consent_frac},
])
