"""Shared sidebar filter panel used on every page."""

from datetime import date

import pandas as pd
import streamlit as st


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render the sidebar filter panel and return the filtered DataFrame.

    The full (unfiltered) record count is captured before any filters are
    applied so the sidebar can show "Showing X of Y records".
    """
    total_records = len(df)

    with st.sidebar:
        st.markdown(
            "<h2 style='color:white; margin-bottom:0;'>🧠 PSH Telestroke Dashboard</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color:#D6E4F0; font-style:italic; margin-top:0;'>Art of the Possible — PoC</p>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("**Filters**")

        # Fiscal Year
        fy_options = sorted(df["fiscal_year"].dropna().unique().tolist())
        fy_selected = st.multiselect("Fiscal Year", fy_options, default=fy_options)

        # Facility
        facility_options = sorted(df["facility"].dropna().unique().tolist())
        facility_selected = st.multiselect("Facility / Spoke Site", facility_options, default=facility_options)

        # Encounter type
        encounter_options = sorted(df["encounter_type"].dropna().unique().tolist())
        encounter_selected = st.multiselect("Encounter Type", encounter_options, default=encounter_options)

        # Date range
        ed_arrival = pd.to_datetime(df["ed_arrival_dt"])
        min_date = ed_arrival.min().date()
        max_date = ed_arrival.max().date()
        date_range = st.date_input(
            "Date Range (ED arrival)",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        # Consultant
        consultant_options = sorted(df["consultant_name"].dropna().unique().tolist())
        consultant_selected = st.multiselect("Consultant", consultant_options, default=consultant_options)

        st.markdown("---")

    # Apply filters
    filtered = df.copy()
    if fy_selected:
        filtered = filtered[filtered["fiscal_year"].isin(fy_selected)]
    if facility_selected:
        filtered = filtered[filtered["facility"].isin(facility_selected)]
    if encounter_selected:
        filtered = filtered[filtered["encounter_type"].isin(encounter_selected)]
    if consultant_selected:
        filtered = filtered[filtered["consultant_name"].isin(consultant_selected)]

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        ed_dt = pd.to_datetime(filtered["ed_arrival_dt"])
        filtered = filtered[(ed_dt.dt.date >= start) & (ed_dt.dt.date <= end)]
    elif isinstance(date_range, date):
        ed_dt = pd.to_datetime(filtered["ed_arrival_dt"])
        filtered = filtered[ed_dt.dt.date == date_range]

    with st.sidebar:
        st.markdown(
            f"<div style='color:#D6E4F0;'><b>Showing {len(filtered):,} of {total_records:,} records</b></div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.caption("Synthetic data only — not real PHI")

    return filtered


def empty_state_check(df: pd.DataFrame) -> bool:
    """Return True if the filtered DataFrame has rows; otherwise show an info message and return False."""
    if len(df) == 0:
        st.info("No records match the selected filters. Widen your filter selection in the sidebar.")
        return False
    return True
