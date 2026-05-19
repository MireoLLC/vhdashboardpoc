"""Global sidebar — TeleStroke PoC nav + Program Health widget + TeleSitting
placeholder + Sign Out.

Call ``render_sidebar()`` once per page (and from ``app.py``). Streamlit's
native sidebar nav is hidden via CSS so this block is the only navigation
surface.
"""

import os

import pandas as pd
import streamlit as st

from utils.targets import (
    get_traffic_light,
    get_traffic_light_emoji,
)


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(PROJECT_DIR, "data")


@st.cache_data
def _load_program_health():
    """Compute the three sidebar Program Health metrics from the full,
    unfiltered dataset. Cached — runs once per session and is reused across
    every page render.
    """
    pts_path = os.path.join(DATA_DIR, "telestroke_synthetic.csv")
    cart_path = os.path.join(DATA_DIR, "cart_uptime_synthetic.csv")
    try:
        df = pd.read_csv(pts_path)
        cart_df = pd.read_csv(cart_path)
    except FileNotFoundError:
        return None

    av = df[df["encounter_type"] == "Audio/Video"]
    eligible = av[av["thrombolysis_eligibility_indicator"] == "Yes"]

    d2n_fraction = (eligible["door_to_needle_compliant"] == "Yes").mean() if len(eligible) else 0.0
    median_response = df["provider_response_minutes"].median() if len(df) else 0.0
    cart_uptime_fraction = (cart_df["cart_uptime_pct"].mean() / 100.0) if len(cart_df) else 0.0

    return {
        "d2n_compliance": float(d2n_fraction),
        "median_response_minutes": float(median_response),
        "cart_uptime": float(cart_uptime_fraction),
    }


def _program_health_row(label, value_text, status):
    emoji = get_traffic_light_emoji(status)
    return (
        "<div style='display:flex;justify-content:space-between;margin-bottom:4px'>"
        f"<span style='color:rgba(255,255,255,0.7)'>{label}</span>"
        f"<span>{emoji} {value_text}</span>"
        "</div>"
    )


def render_sidebar():
    """Render the navy sidebar shared across the whole app."""
    with st.sidebar:
        # ── Header ──
        st.markdown(
            """
            <div style='padding:48px 8px 8px;border-bottom:1px solid rgba(255,255,255,0.15);
                        margin-bottom:16px'>
                <div style='font-size:0.7rem;font-weight:600;letter-spacing:0.08em;
                            color:rgba(255,255,255,0.5);text-transform:uppercase;
                            margin-bottom:4px'>Penn State Health</div>
                <div style='font-size:1rem;font-weight:700;color:white;line-height:1.2'>
                    Virtual Health<br>Dashboard
                </div>
                <div style='font-size:0.7rem;color:rgba(255,255,255,0.4);margin-top:4px'>
                    Clinical Performance PoC
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── TeleStroke section ──
        st.markdown(
            """
            <div style='font-size:0.68rem;font-weight:600;letter-spacing:0.08em;
                        color:rgba(255,255,255,0.45);text-transform:uppercase;
                        padding:8px 8px 4px;margin-top:4px'>
                🧠 TeleStroke PoC
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.page_link("pages/01_Phase1_Overview.py", label="Phase 1 Overview", icon="📊")
        st.page_link("pages/02_Clinical_Outcomes.py", label="Clinical Outcomes", icon="🏥")
        st.page_link("pages/03_Operational.py", label="Operational", icon="⚙️")
        st.page_link("pages/04_Financial.py", label="Financial", icon="💰")
        st.page_link("pages/05_Provider_Performance.py", label="Provider Performance", icon="🔒")

        # ── Program Health widget — program-wide, unfiltered ──
        health = _load_program_health()
        if health is not None:
            d2n_status = get_traffic_light(health["d2n_compliance"], "door_to_needle_compliance_60")
            rt_status  = get_traffic_light(health["median_response_minutes"], "door_to_neurologist_minutes")
            cu_status  = get_traffic_light(health["cart_uptime"], "cart_uptime")

            d2n_row = _program_health_row(
                "D2N Compliance",
                f"{health['d2n_compliance'] * 100:.0f}%",
                d2n_status,
            )
            rt_row = _program_health_row(
                "Response Time",
                f"{health['median_response_minutes']:.0f} min",
                rt_status,
            )
            cu_row = _program_health_row(
                "Cart Uptime",
                f"{health['cart_uptime'] * 100:.0f}%",
                cu_status,
            )

            st.markdown(
                "<div style='background:rgba(255,255,255,0.08);border-radius:6px;"
                "padding:10px 12px;margin:12px 0 4px;font-size:0.72rem'>"
                "<div style='color:rgba(255,255,255,0.5);font-size:0.65rem;"
                "text-transform:uppercase;letter-spacing:0.06em;"
                "margin-bottom:6px'>Program Health</div>"
                f"{d2n_row}{rt_row}{cu_row}"
                "</div>",
                unsafe_allow_html=True,
            )

        # ── Divider ──
        st.markdown(
            "<div style='border-top:1px solid rgba(255,255,255,0.12);margin:12px 0'></div>",
            unsafe_allow_html=True,
        )

        # ── TeleSitting section (Coming Soon — no page links yet) ──
        st.markdown(
            """
            <div style='font-size:0.68rem;font-weight:600;letter-spacing:0.08em;
                        color:rgba(255,255,255,0.45);text-transform:uppercase;
                        padding:8px 8px 4px'>
                👁 TeleSitting PoC
            </div>
            <div style='padding:6px 8px 12px'>
                <div style='font-size:0.78rem;color:rgba(255,255,255,0.35);
                            font-style:italic'>Coming Soon</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Bottom: Sign Out ──
        st.markdown(
            "<div style='border-top:1px solid rgba(255,255,255,0.12);"
            "margin-top:auto;padding-top:12px'></div>",
            unsafe_allow_html=True,
        )

        if st.button("Sign Out", use_container_width=True, key="sidebar_signout"):
            st.session_state.authenticated = False
            st.rerun()

        st.markdown(
            """
            <div style='font-size:0.65rem;color:rgba(255,255,255,0.3);
                        text-align:center;padding:8px 0;margin-top:8px'>
                ⚠️ Synthetic data only<br>No real patient data
            </div>
            """,
            unsafe_allow_html=True,
        )
