"""Industry-standard performance targets for PSH TeleStroke Dashboard.

Single source of truth for every target referenced in the dashboard. Page
files should not hardcode benchmark values — look them up here.

Sources: AHA/ASA Guidelines, Joint Commission, Get With The Guidelines —
Stroke, CMS Hospital Readmissions Reduction Program, internal PSH SLAs.
"""

import pandas as pd
import streamlit as st


TARGETS = {

    # ── Phase 1 KPIs ──────────────────────────────────────────────

    "door_to_needle_compliance_60": {
        "label":       "Door-to-Needle Compliance (≤60 min)",
        "target":      0.85,
        "target_display": "≥85%",
        "unit":        "percent",
        "direction":   "higher_is_better",
        "source":      "AHA/ASA Stroke Guidelines 2019",
        "amber_threshold": 0.10,
        "story":       "TS-01",
    },

    "door_to_needle_compliance_45": {
        "label":       "Door-to-Needle Compliance (≤45 min)",
        "target":      0.50,
        "target_display": "≥50%",
        "unit":        "percent",
        "direction":   "higher_is_better",
        "source":      "AHA/ASA Target: Stroke 2020",
        "amber_threshold": 0.10,
        "story":       "TS-01",
    },

    "door_to_neurologist_minutes": {
        "label":       "Door-to-Neurologist Evaluation Time",
        "target":      20,
        "target_display": "≤20 min",
        "unit":        "minutes",
        "direction":   "lower_is_better",
        "source":      "AHA/ASA Telestroke Guidelines",
        "amber_threshold": 0.10,
        "story":       "TS-02",
    },

    "stroke_alert_volume": {
        "label":       "Monthly Stroke Alert Volume",
        "target":      None,
        "target_display": "Trending metric — no absolute target",
        "unit":        "count",
        "direction":   "higher_is_better",
        "source":      "Internal operational metric",
        "amber_threshold": None,
        "story":       "TS-04",
    },

    "cart_uptime": {
        "label":       "Telestroke Cart Uptime",
        "target":      0.99,
        "target_display": "≥99%",
        "unit":        "percent",
        "direction":   "higher_is_better",
        "source":      "PSH SLA / Vendor Contract",
        # 5% amber band (operational interpretation, not a clinical guideline).
        "amber_threshold": 0.05,
        "story":       "TS-05",
    },

    "door_to_cart_minutes": {
        "label":       "Door-to-Cart Registration Time",
        "target":      15,
        "target_display": "≤15 min",
        "unit":        "minutes",
        "direction":   "lower_is_better",
        "source":      "AHA/ASA Telestroke Operations",
        "amber_threshold": 0.10,
        "story":       "TS-06",
    },

    "neurologist_to_decision_minutes": {
        "label":       "Neurologist-to-Treatment Decision Time",
        "target":      20,
        "target_display": "≤20 min",
        "unit":        "minutes",
        "direction":   "lower_is_better",
        "source":      "AHA/ASA Telestroke Guidelines",
        "amber_threshold": 0.10,
        "story":       "TS-07",
    },

    "decision_to_administration_minutes": {
        "label":       "Decision-to-TNK Administration Time",
        "target":      5,
        "target_display": "≤5 min",
        "unit":        "minutes",
        "direction":   "lower_is_better",
        "source":      "AHA/ASA Get With The Guidelines",
        "amber_threshold": 0.20,
        "story":       "TS-10",
    },

    # ── Phase 2 Clinical Outcomes ──────────────────────────────────

    "treatment_rate": {
        "label":       "Thrombolysis Treatment Rate (Eligible Cases)",
        "target":      0.85,
        "target_display": "≥85%",
        "unit":        "percent",
        "direction":   "higher_is_better",
        "source":      "Get With The Guidelines — Stroke",
        "amber_threshold": 0.10,
        "story":       "TS-11",
    },

    "lvo_detection_rate": {
        "label":       "LVO Detection Rate",
        "target":      0.90,
        "target_display": "≥90%",
        "unit":        "percent",
        "direction":   "higher_is_better",
        "source":      "AHA/ASA LVO Triage Guidelines 2022",
        "amber_threshold": 0.10,
        "story":       "TS-12",
    },

    "nihss_documentation_compliance": {
        "label":       "NIHSS Documentation Compliance",
        "target":      0.95,
        "target_display": "≥95%",
        "unit":        "percent",
        "direction":   "higher_is_better",
        "source":      "Joint Commission Stroke Certification",
        "amber_threshold": 0.05,
        "story":       "TS-15",
    },

    "consent_form_compliance": {
        "label":       "Consent Form Completion Rate",
        "target":      0.95,
        "target_display": "≥95%",
        "unit":        "percent",
        "direction":   "higher_is_better",
        "source":      "Joint Commission / Regulatory",
        "amber_threshold": 0.05,
        "story":       "TS-19",
    },

    "thirty_day_readmission": {
        "label":       "30-Day Readmission Rate",
        "target":      0.12,
        "target_display": "≤12%",
        "unit":        "percent",
        "direction":   "lower_is_better",
        "source":      "CMS Hospital Readmissions Reduction Program",
        "amber_threshold": 0.20,
        "story":       "TS-21",
    },

    "icu_admission_rate": {
        "label":       "ICU Admission Rate",
        "target":      0.20,
        "target_display": "≤20%",
        "unit":        "percent",
        "direction":   "lower_is_better",
        "source":      "Industry benchmark — academic stroke centers",
        "amber_threshold": 0.25,
        "story":       "Phase 2",
    },

    # ── Phase 2 Operational ────────────────────────────────────────

    "door_to_needle_median_minutes": {
        "label":       "Median Door-to-Needle Time",
        "target":      45,
        "target_display": "≤45 min median",
        "unit":        "minutes",
        "direction":   "lower_is_better",
        "source":      "AHA/ASA Target: Stroke 2020",
        "amber_threshold": 0.15,
        "story":       "TS-14",
    },

    "response_time_outlier_rate": {
        "label":       "Consultant Response Time Outlier Rate",
        "target":      0.05,
        "target_display": "≤5% outliers (>15 min)",
        "unit":        "percent",
        "direction":   "lower_is_better",
        "source":      "PSH Telestroke Operations Standard",
        "amber_threshold": 0.50,
        "story":       "TS-16",
    },

    # ── Financial ─────────────────────────────────────────────────

    "cost_per_consult": {
        "label":       "Cost per Telestroke Consult",
        "target":      300,
        "target_display": "≤$300 per consult",
        "unit":        "currency",
        "direction":   "lower_is_better",
        "source":      "Industry benchmark — telestroke programs",
        "amber_threshold": 0.20,
        "story":       "TS-08",
    },
}


def get_target(key):
    """Return the target dict for a given KPI key, or None if missing."""
    return TARGETS.get(key)


def get_traffic_light(value, target_key):
    """Return ``'green'`` / ``'amber'`` / ``'red'`` based on value vs target.

    Returns ``'gray'`` if the KPI has no target defined (trending-only).
    For ``higher_is_better`` metrics, green = at or above target. For
    ``lower_is_better`` metrics, green = at or below target. The amber band
    is target * amber_threshold on the wrong side of the target.
    """
    t = TARGETS.get(target_key)
    if not t or t["target"] is None or value is None:
        return "gray"
    if isinstance(value, float) and pd.isna(value):
        return "gray"

    target    = t["target"]
    direction = t["direction"]
    amber_pct = t.get("amber_threshold", 0.10) or 0.10

    if direction == "higher_is_better":
        if value >= target:
            return "green"
        elif value >= target * (1 - amber_pct):
            return "amber"
        return "red"
    # lower_is_better
    if value <= target:
        return "green"
    elif value <= target * (1 + amber_pct):
        return "amber"
    return "red"


def get_traffic_light_color(status):
    """Hex color for a traffic-light status."""
    return {
        "green": "#10B981",
        "amber": "#F59E0B",
        "red":   "#EF4444",
        "gray":  "#9CA3AF",
    }.get(status, "#9CA3AF")


def get_traffic_light_emoji(status):
    """Emoji for a traffic-light status."""
    return {
        "green": "🟢",
        "amber": "🟡",
        "red":   "🔴",
        "gray":  "⚪",
    }.get(status, "⚪")


def render_kpi_card(target_key, current_value, *, display_value=None, synthetic=False, extra_note=None):
    """Render one styled KPI tile with a traffic-light left border.

    ``current_value`` should be in the unit expected by ``get_traffic_light``
    (fraction for percent, raw number for minutes/currency). ``display_value``
    overrides the auto-formatted text shown to the user; pass it when you
    want a different denomination on screen than what's used for grading.
    """
    t = TARGETS.get(target_key)
    if not t:
        st.markdown(f"<div class='kpi-card'><div class='kpi-label'>{target_key}</div>"
                    "<div class='kpi-value'>—</div></div>", unsafe_allow_html=True)
        return

    status = get_traffic_light(current_value, target_key)
    color  = get_traffic_light_color(status)
    emoji  = get_traffic_light_emoji(status)

    if display_value is not None:
        value_text = display_value
    elif current_value is None or (isinstance(current_value, float) and pd.isna(current_value)):
        value_text = "—"
    elif t["unit"] == "percent":
        value_text = f"{current_value * 100:.1f}%"
    elif t["unit"] == "minutes":
        value_text = f"{current_value:.1f} min"
    elif t["unit"] == "currency":
        value_text = f"${current_value:,.0f}"
    else:
        value_text = f"{current_value:,.0f}"

    synthetic_badge = (
        "<span style='display:inline-block;background:#FEF3C7;border:1px solid #F59E0B;"
        "color:#92400E;font-size:0.62rem;padding:1px 6px;border-radius:3px;"
        "margin-left:6px;vertical-align:middle'>⚠️ Synthetic</span>"
        if synthetic else ""
    )
    note_html = (
        f"<div style='font-size:0.7rem;color:#6B7280;margin-top:2px'>{extra_note}</div>"
        if extra_note else ""
    )

    st.markdown(
        f"""
        <div class='kpi-card' style='border-left-color:{color}'>
            <div class='kpi-label'>{t['label']}{synthetic_badge}</div>
            <div class='kpi-value'>{emoji} {value_text}</div>
            <div class='kpi-benchmark'>Target: {t['target_display']} · {t['source']}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_gray_card(label, value_text, *, note=None):
    """Render a no-target trending KPI tile (gray left border)."""
    note_html = (
        f"<div class='kpi-benchmark'>{note}</div>"
        if note else ""
    )
    st.markdown(
        f"""
        <div class='kpi-card' style='border-left-color:#9CA3AF'>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value'>⚪ {value_text}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_targets_panel(target_data):
    """Render a collapsible Performance Targets & Benchmarks reference table.

    ``target_data`` is a list of dicts with ``target_key`` and
    ``current_value`` (in the unit expected by ``get_traffic_light``).
    """
    with st.expander("📋 Performance Targets & Benchmarks", expanded=False):
        st.markdown(
            "<p style='font-size:0.75rem;color:#6B7280;margin-bottom:12px'>"
            "Targets are based on industry standards from AHA/ASA Guidelines, "
            "Joint Commission Stroke Certification, and the Get With The "
            "Guidelines — Stroke program. These are reference benchmarks, "
            "not formally adopted PSH OKRs.</p>",
            unsafe_allow_html=True,
        )

        rows = []
        for item in target_data:
            t = TARGETS.get(item["target_key"])
            if not t:
                continue
            current = item["current_value"]
            status  = get_traffic_light(current, item["target_key"])
            emoji   = get_traffic_light_emoji(status)

            if current is None or (isinstance(current, float) and pd.isna(current)):
                current_display = "—"
            elif t["unit"] == "percent":
                current_display = f"{current * 100:.1f}%"
            elif t["unit"] == "minutes":
                current_display = f"{current:.1f} min"
            elif t["unit"] == "currency":
                current_display = f"${current:,.0f}"
            else:
                current_display = f"{current:,.0f}"

            rows.append({
                "Status":  emoji,
                "KPI":     t["label"],
                "Current": current_display,
                "Target":  t["target_display"],
                "Story":   t["story"],
                "Source":  t["source"],
            })

        if not rows:
            st.caption("No targets to display for this view.")
            return

        panel_df = pd.DataFrame(rows)
        st.dataframe(
            panel_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status":  st.column_config.TextColumn("",                width="small"),
                "KPI":     st.column_config.TextColumn("KPI",             width="large"),
                "Current": st.column_config.TextColumn("Current",         width="medium"),
                "Target":  st.column_config.TextColumn("Target",          width="medium"),
                "Story":   st.column_config.TextColumn("Story ID",        width="small"),
                "Source":  st.column_config.TextColumn("Benchmark Source", width="large"),
            },
        )
