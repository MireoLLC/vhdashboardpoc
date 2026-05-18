"""Page 5 — Provider Performance (Phase 2 KPIs · restricted in production)."""

import os
import sys

import pandas as pd
import streamlit as st

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from utils.charts import overlay_lines  # noqa: E402
from utils.filters import empty_state_check, render_filters  # noqa: E402
from utils.theme import FY_MONTH_ORDER, PAGE_CSS, PSH_NAVY, PSH_TEAL  # noqa: E402

st.set_page_config(page_title="Provider Performance", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
st.markdown(PAGE_CSS, unsafe_allow_html=True)

DATA_DIR = os.path.join(PROJECT_DIR, "data")


@st.cache_data
def load_patients():
    df = pd.read_csv(os.path.join(DATA_DIR, "telestroke_synthetic.csv"))
    df["ed_arrival_dt"] = pd.to_datetime(df["ed_arrival_dt"], errors="coerce")
    df["consult_signed_dt"] = pd.to_datetime(df["consult_signed_dt"], errors="coerce")
    df["call_to_provider_dt"] = pd.to_datetime(df["call_to_provider_dt"], errors="coerce")
    return df


df_full = load_patients()
df = render_filters(df_full)

st.markdown("<h1>Provider Performance <span class='phase2-badge'>Phase 2</span></h1>", unsafe_allow_html=True)
st.warning(
    "In production, this page will require restricted access. Displayed here for PoC demonstration purposes only."
)
st.caption("Per-consultant scorecards and comparison.")

if not empty_state_check(df):
    st.stop()


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

if selected:
    pdf = df[df["consultant_name"] == selected]
    s = _provider_summary(pdf)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total consults", f"{s['total_consults']:,}")
    c2.metric("D2N Compliance", f"{s['d2n_compliance_pct']:.1f}%" if pd.notna(s["d2n_compliance_pct"]) else "—",
              help="Benchmark ≥85%")
    c3.metric("Median response", f"{s['median_response_min']:.1f} min" if pd.notna(s["median_response_min"]) else "—",
              help="Benchmark ≤15 min")
    c4.metric("NIHSS documentation", f"{s['nihss_compliance_pct']:.1f}%")
    c5.metric("Consent completion", f"{s['consent_completion_pct']:.1f}%")

st.markdown("---")

# ── Section 2: Comparison table (TS-19) ───────────────────────────────────
st.markdown("##### Provider comparison (TS-19)")

rows = []
for name in providers:
    s = _provider_summary(df[df["consultant_name"] == name])
    rows.append({
        "Provider": name,
        "Volume": s["total_consults"],
        "D2N Compliance %": round(s["d2n_compliance_pct"], 1) if pd.notna(s["d2n_compliance_pct"]) else None,
        "Median Response (min)": round(s["median_response_min"], 1) if pd.notna(s["median_response_min"]) else None,
        "Avg Handle (min)": round(s["avg_handle_min"], 1) if pd.notna(s["avg_handle_min"]) else None,
        "NIHSS Doc %": round(s["nihss_compliance_pct"], 1),
        "Consent %": round(s["consent_completion_pct"], 1),
    })

cmp_df = pd.DataFrame(rows)


def _style(row):
    colors = ["" for _ in row]
    cols = list(row.index)

    def _set(col, ok):
        idx = cols.index(col)
        colors[idx] = f"background-color: {'#DCFCE7' if ok else '#FEE2E2'}"

    if pd.notna(row["D2N Compliance %"]):
        _set("D2N Compliance %", row["D2N Compliance %"] >= 85)
    if pd.notna(row["Median Response (min)"]):
        _set("Median Response (min)", row["Median Response (min)"] <= 15)
    if pd.notna(row["NIHSS Doc %"]):
        _set("NIHSS Doc %", row["NIHSS Doc %"] >= 85)
    if pd.notna(row["Consent %"]):
        _set("Consent %", row["Consent %"] >= 80)
    return colors


st.dataframe(cmp_df.style.apply(_style, axis=1), use_container_width=True, hide_index=True)
st.caption("Green = meeting benchmark · Red = below benchmark (D2N ≥85%, response ≤15 min, NIHSS doc ≥85%, consent ≥80%).")

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
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Navy = median response (minutes) · Teal = D2N compliance (%)")
    else:
        st.info("Not enough data for a trend on this provider in the current filter.")
