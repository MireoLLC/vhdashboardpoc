"""Horizontal filter bars rendered at the top of each program's pages."""

from datetime import datetime

import pandas as pd
import streamlit as st


_ALL = "All"


def render_telestroke_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render the TeleStroke horizontal filter bar and return the filtered df.

    Filters:
      - Fiscal Year (selectbox, "All" default)
      - Facility (multiselect, max 3, "All facilities" placeholder when empty)
      - Encounter Type (selectbox, "All" default)
      - Consultant (multiselect, "All consultants" placeholder when empty)
      - Date Range (date_input).
    """
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1.5, 1.5, 2])

        with col1:
            fiscal_years = sorted(df["fiscal_year"].unique().tolist())
            selected_fy = st.selectbox(
                "Fiscal Year",
                options=[_ALL] + fiscal_years,
                index=0,
                key="filter_fy",
            )

        with col2:
            facilities = sorted(df["facility"].unique().tolist())
            selected_facilities = st.multiselect(
                "Facility",
                options=facilities,
                default=[],
                placeholder="All facilities",
                max_selections=3,
                key="filter_facility",
            )

        with col3:
            enc_options = [_ALL, "Audio/Video", "Phone", "Reg-No Consult"]
            selected_enc = st.selectbox(
                "Encounter Type",
                options=enc_options,
                index=0,
                key="filter_enc_type",
            )

        with col4:
            consultants = sorted(df["consultant_name"].unique().tolist())
            selected_consultants = st.multiselect(
                "Consultant",
                options=consultants,
                default=[],
                placeholder="All consultants",
                key="filter_consultant",
            )

        with col5:
            arrival = pd.to_datetime(df["ed_arrival_dt"], errors="coerce")
            min_date = arrival.min().date()
            max_date = arrival.max().date()
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="filter_date_range",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    filtered = df.copy()

    if selected_fy != _ALL:
        filtered = filtered[filtered["fiscal_year"] == selected_fy]
    if selected_facilities:
        filtered = filtered[filtered["facility"].isin(selected_facilities)]
    if selected_enc != _ALL:
        filtered = filtered[filtered["encounter_type"] == selected_enc]
    if selected_consultants:
        filtered = filtered[filtered["consultant_name"].isin(selected_consultants)]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        filtered["ed_arrival_dt"] = pd.to_datetime(filtered["ed_arrival_dt"], errors="coerce")
        filtered = filtered[
            (filtered["ed_arrival_dt"].dt.date >= date_range[0])
            & (filtered["ed_arrival_dt"].dt.date <= date_range[1])
        ]

    st.caption(f"**{len(filtered):,}** of {len(df):,} records shown")

    return filtered


def render_telesitting_filters(pl_df: pd.DataFrame, rl_df: pd.DataFrame):
    """Render the TeleSitting horizontal filter bar. Returns (filtered_pl_df, filtered_rl_df)."""
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 2])

        with col1:
            fiscal_years = sorted(pl_df["fiscal_year"].unique().tolist())
            selected_fy = st.multiselect(
                "Fiscal Year",
                options=fiscal_years,
                default=fiscal_years,
                key="tsit_filter_fy",
            )

        with col2:
            hospitals = sorted(pl_df["hospital"].unique().tolist())
            selected_hospitals = st.multiselect(
                "Hospital",
                options=hospitals,
                default=hospitals,
                key="tsit_filter_hospital",
            )

        with col3:
            risk_levels = ["High", "Medium", "Low"]
            selected_risk = st.multiselect(
                "Risk Level",
                options=risk_levels,
                default=risk_levels,
                key="tsit_filter_risk",
            )

        with col4:
            admit = pd.to_datetime(pl_df["admit_dt"], errors="coerce")
            min_date = admit.min().date()
            max_date = admit.max().date()
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="tsit_filter_date",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    filtered_pl = pl_df.copy()
    if selected_fy:
        filtered_pl = filtered_pl[filtered_pl["fiscal_year"].isin(selected_fy)]
    if selected_hospitals:
        filtered_pl = filtered_pl[filtered_pl["hospital"].isin(selected_hospitals)]
    if selected_risk:
        filtered_pl = filtered_pl[filtered_pl["risk_level"].isin(selected_risk)]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        filtered_pl["admit_dt"] = pd.to_datetime(filtered_pl["admit_dt"], errors="coerce")
        filtered_pl = filtered_pl[
            (filtered_pl["admit_dt"].dt.date >= date_range[0])
            & (filtered_pl["admit_dt"].dt.date <= date_range[1])
        ]

    filtered_rl = rl_df[rl_df["fin"].isin(filtered_pl["fin"])]

    st.caption(
        f"**{len(filtered_pl):,}** patients · **{len(filtered_rl):,}** redirect events shown"
    )

    return filtered_pl, filtered_rl
