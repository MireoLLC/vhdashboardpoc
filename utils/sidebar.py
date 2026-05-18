"""Global sidebar — TeleStroke PoC nav + TeleSitting placeholder + Sign Out.

Call render_sidebar() once per page (and from app.py). Streamlit's native
sidebar nav is hidden via CSS so this block is the only navigation surface.
"""

import streamlit as st


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
