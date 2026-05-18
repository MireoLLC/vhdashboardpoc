"""PSH Virtual Health Dashboard — entry point.

Single job: password gate. On success, redirect to Phase 1 Overview.
Sidebar is centralized in utils.sidebar.render_sidebar() so every page can
call it.
"""

import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.sidebar import render_sidebar  # noqa: E402
from utils.theme import get_global_css  # noqa: E402

st.set_page_config(
    page_title="PSH Virtual Health Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_global_css(), unsafe_allow_html=True)


def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # Hide sidebar entirely on the login page
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] { display: none !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        _, center, _ = st.columns([1, 1.2, 1])
        with center:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(
                "<h1 style='color:#1F3864;text-align:center;font-size:1.6rem;"
                "font-weight:700;margin-bottom:4px'>Penn State Health</h1>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<h2 style='color:#1F7A8C;text-align:center;font-size:1.1rem;"
                "font-weight:600;margin-bottom:2px'>Virtual Health Dashboard</h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='color:#6B7280;text-align:center;font-size:0.8rem;"
                "margin-bottom:24px'>Clinical Performance · PoC</p>",
                unsafe_allow_html=True,
            )
            st.divider()
            password = st.text_input(
                "Access password",
                type="password",
                placeholder="Enter password...",
                label_visibility="collapsed",
            )
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", type="primary", use_container_width=True):
                if password == st.secrets["APP_PASSWORD"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password")
        st.stop()


check_password()

# Authenticated — render the shared sidebar, then bounce to Phase 1 Overview.
render_sidebar()

st.switch_page("pages/01_Phase1_Overview.py")
