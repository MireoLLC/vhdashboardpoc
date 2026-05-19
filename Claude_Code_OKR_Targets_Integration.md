# Claude Code Instructions — OKR & Performance Targets Integration
**Project:** Penn State Health Virtual Health Dashboard PoC  
**Session:** Performance Targets + Benchmarks  
**Scope:** Add industry-standard performance targets and traffic light indicators across all 5 TeleStroke dashboard pages  
**Framing:** "Performance Targets" — sourced from AHA/ASA, Joint Commission, and industry best practice. Not internal OKRs (those are not yet formally defined).

---

## Pre-Flight Check

Before writing any code:
1. Confirm working directory is `/Users/chanakaperera/Dev/vhdashboardpoc`
2. List all files in `pages/` and `utils/`
3. Confirm `data/telestroke_synthetic.csv` exists
4. Read this file in full before summarizing your plan
5. Wait for confirmation before making any changes

---

## Step 1 — Create utils/targets.py

Create a new file `utils/targets.py` that is the single source of truth for all performance targets. Every target used anywhere in the dashboard must come from this file — no hardcoded numbers in page files.

```python
# utils/targets.py
# Industry-standard performance targets for PSH TeleStroke Dashboard
# Sources: AHA/ASA Guidelines, Joint Commission, Get With The Guidelines

TARGETS = {

    # ── Phase 1 KPIs ──────────────────────────────────────────────

    "door_to_needle_compliance_60": {
        "label":       "Door-to-Needle Compliance (≤60 min)",
        "target":      0.85,
        "target_display": "≥85%",
        "unit":        "percent",
        "direction":   "higher_is_better",
        "source":      "AHA/ASA Stroke Guidelines 2019",
        "amber_threshold": 0.10,   # within 10% of target = amber
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
        "amber_threshold": 0.02,
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
    """Return target dict for a given KPI key. Returns None if not found."""
    return TARGETS.get(key)


def get_traffic_light(value, target_key):
    """
    Returns traffic light status: 'green', 'amber', or 'red'
    based on value vs target and direction.
    Returns 'gray' if no target defined.
    """
    t = TARGETS.get(target_key)
    if not t or t["target"] is None:
        return "gray"

    target    = t["target"]
    direction = t["direction"]
    amber_pct = t.get("amber_threshold", 0.10)

    if direction == "higher_is_better":
        if value >= target:
            return "green"
        elif value >= target * (1 - amber_pct):
            return "amber"
        else:
            return "red"
    else:  # lower_is_better
        if value <= target:
            return "green"
        elif value <= target * (1 + amber_pct):
            return "amber"
        else:
            return "red"


def get_traffic_light_color(status):
    """Returns hex color for a traffic light status."""
    return {
        "green": "#10B981",
        "amber": "#F59E0B",
        "red":   "#EF4444",
        "gray":  "#9CA3AF",
    }.get(status, "#9CA3AF")


def get_traffic_light_emoji(status):
    """Returns emoji for a traffic light status."""
    return {
        "green": "🟢",
        "amber": "🟡",
        "red":   "🔴",
        "gray":  "⚪",
    }.get(status, "⚪")
```

---

## Step 2 — Add Benchmark Reference Lines to utils/charts.py

Update `utils/charts.py` to support benchmark reference lines on all relevant chart types. Add the following helper function and update existing chart functions to accept an optional `benchmark` parameter:

```python
def add_benchmark_line(fig, value, label, color="#EF4444", dash="dash"):
    """
    Adds a horizontal benchmark reference line to a Plotly figure.
    Call after creating the chart, before returning it.
    
    Usage:
        fig = trend_line(df, x, y, title)
        fig = add_benchmark_line(fig, 0.85, "Target: ≥85%")
    """
    fig.add_hline(
        y=value,
        line_dash=dash,
        line_color=color,
        line_width=1.5,
        annotation_text=label,
        annotation_position="top right",
        annotation_font_size=11,
        annotation_font_color=color,
    )
    return fig


def add_benchmark_vline(fig, value, label, color="#EF4444"):
    """Adds a vertical benchmark line — for histograms/distributions."""
    fig.add_vline(
        x=value,
        line_dash="dash",
        line_color=color,
        line_width=1.5,
        annotation_text=label,
        annotation_position="top right",
        annotation_font_size=11,
        annotation_font_color=color,
    )
    return fig
```

---

## Step 3 — Create Targets Panel Component

Add a new function `render_targets_panel(target_keys, df)` to `utils/targets.py`. This renders a clean "Performance Targets" reference table at the bottom of each page.

```python
def render_targets_panel(target_data):
    """
    Renders a collapsible Performance Targets reference panel.
    
    target_data: list of dicts with keys:
        - target_key: str (key from TARGETS dict)
        - current_value: float (actual calculated value)
    
    Renders as an st.expander with a styled table showing:
    - KPI name
    - Current performance
    - Target
    - Traffic light status
    - Source citation
    """
    import streamlit as st
    
    with st.expander("📋 Performance Targets & Benchmarks", expanded=False):
        st.markdown("""
        <p style='font-size:0.75rem;color:#6B7280;margin-bottom:12px'>
        Targets are based on industry standards from AHA/ASA Guidelines, 
        Joint Commission Stroke Certification, and Get With The Guidelines — Stroke program. 
        These are reference benchmarks, not formally adopted PSH OKRs.
        </p>
        """, unsafe_allow_html=True)
        
        rows = []
        for item in target_data:
            t = TARGETS.get(item["target_key"])
            if not t:
                continue
            current = item["current_value"]
            status  = get_traffic_light(current, item["target_key"])
            emoji   = get_traffic_light_emoji(status)
            
            # Format current value
            if t["unit"] == "percent":
                current_display = f"{current*100:.1f}%"
            elif t["unit"] == "minutes":
                current_display = f"{current:.1f} min"
            elif t["unit"] == "currency":
                current_display = f"${current:,.0f}"
            else:
                current_display = f"{current:,.0f}"
            
            rows.append({
                "Status":      emoji,
                "KPI":         t["label"],
                "Current":     current_display,
                "Target":      t["target_display"],
                "Story":       t["story"],
                "Source":      t["source"],
            })
        
        if rows:
            import pandas as pd
            panel_df = pd.DataFrame(rows)
            st.dataframe(
                panel_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn("", width="small"),
                    "KPI":    st.column_config.TextColumn("KPI", width="large"),
                    "Current": st.column_config.TextColumn("Current", width="medium"),
                    "Target": st.column_config.TextColumn("Target", width="medium"),
                    "Story":  st.column_config.TextColumn("Story ID", width="small"),
                    "Source": st.column_config.TextColumn("Benchmark Source", width="large"),
                }
            )
```

---

## Step 4 — Update pages/01_Phase1_Overview.py

### 4a — Import targets
Add to imports at top of file:
```python
from utils.targets import get_target, get_traffic_light, get_traffic_light_color, get_traffic_light_emoji, render_targets_panel
from utils.charts import add_benchmark_line, add_benchmark_vline
```

### 4b — Update KPI tiles with traffic lights

For each KPI tile, calculate the traffic light status and apply border color dynamically. Replace static border colors with traffic-light-driven colors.

Example pattern for D2N Compliance tile:
```python
# Calculate value
d2n_compliance = len(df_av[df_av['door_to_needle_time_minutes'] <= 60]) / len(df_av) if len(df_av) > 0 else 0

# Get traffic light
tl_status = get_traffic_light(d2n_compliance, "door_to_needle_compliance_60")
tl_color  = get_traffic_light_color(tl_status)
tl_emoji  = get_traffic_light_emoji(tl_status)
t         = get_target("door_to_needle_compliance_60")

# Render styled KPI card
st.markdown(f"""
<div class="kpi-card" style="border-left-color:{tl_color}">
    <div class="kpi-label">D2N Compliance (≤60 min)</div>
    <div class="kpi-value">{tl_emoji} {d2n_compliance*100:.1f}%</div>
    <div class="kpi-benchmark">Target: {t['target_display']} · {t['source']}</div>
</div>
""", unsafe_allow_html=True)
```

Apply this pattern to ALL KPI tiles on the page:
- D2N Compliance — target key: `door_to_needle_compliance_60`
- Median Door-to-Neurologist — target key: `door_to_neurologist_minutes`
- Avg Stroke Alert Volume — target key: `stroke_alert_volume` (gray — no target)
- Cart Uptime — target key: `cart_uptime`
- Median Door-to-Cart — target key: `door_to_cart_minutes`
- Median Neurologist-to-Decision — target key: `neurologist_to_decision_minutes`
- Median Decision-to-TNK — target key: `decision_to_administration_minutes`

### 4c — Add benchmark lines to charts

For every time-series or trend chart on this page, add a benchmark reference line:

- **D2N Compliance trend chart:**
  ```python
  fig = add_benchmark_line(fig, 0.85, "Target: ≥85% (AHA/ASA)")
  ```

- **Door-to-Neurologist trend:**
  ```python
  fig = add_benchmark_line(fig, 20, "Target: ≤20 min")
  ```

- **Door-to-Cart trend:**
  ```python
  fig = add_benchmark_line(fig, 15, "Target: ≤15 min")
  ```

- **Neurologist-to-Decision trend:**
  ```python
  fig = add_benchmark_line(fig, 20, "Target: ≤20 min")
  ```

- **Decision-to-TNK trend:**
  ```python
  fig = add_benchmark_line(fig, 5, "Target: ≤5 min")
  ```

For distribution histograms, add vertical benchmark lines:
- **D2N distribution histogram:**
  ```python
  fig = add_benchmark_vline(fig, 60, "60 min")
  fig = add_benchmark_vline(fig, 45, "45 min", color="#F59E0B")
  ```

### 4d — Add targets panel at bottom of page

After all charts, add:
```python
render_targets_panel([
    {"target_key": "door_to_needle_compliance_60",      "current_value": d2n_compliance},
    {"target_key": "door_to_needle_compliance_45",      "current_value": d2n_compliance_45},
    {"target_key": "door_to_neurologist_minutes",       "current_value": median_d2n_minutes},
    {"target_key": "cart_uptime",                       "current_value": cart_uptime_pct},
    {"target_key": "door_to_cart_minutes",              "current_value": median_d2c},
    {"target_key": "neurologist_to_decision_minutes",   "current_value": median_n2d},
    {"target_key": "decision_to_administration_minutes","current_value": median_d2a},
])
```

---

## Step 5 — Update pages/02_Clinical_Outcomes.py

### 5a — Import targets (same as Step 4a)

### 5b — Update KPI tiles with traffic lights

Apply the same traffic light pattern to all Clinical Outcomes KPI tiles:
- Treatment Rate — target key: `treatment_rate`
- LVO Detection Rate — target key: `lvo_detection_rate`
- NIHSS Documentation Compliance — target key: `nihss_documentation_compliance`
- Consent Form Completion — target key: `consent_form_compliance`
- 30-Day Readmission Rate — target key: `thirty_day_readmission`
- ICU Admission Rate — target key: `icu_admission_rate`

### 5c — Add benchmark lines to charts

- **30-Day Readmission trend:**
  ```python
  fig = add_benchmark_line(fig, 0.12, "Target: ≤12% (CMS)")
  ```

- **Treatment Rate trend:**
  ```python
  fig = add_benchmark_line(fig, 0.85, "Target: ≥85% (GWTG)")
  ```

- **NIHSS compliance trend:**
  ```python
  fig = add_benchmark_line(fig, 0.95, "Target: ≥95% (Joint Commission)")
  ```

### 5d — Add targets panel at bottom of page

```python
render_targets_panel([
    {"target_key": "treatment_rate",              "current_value": treatment_rate},
    {"target_key": "lvo_detection_rate",          "current_value": lvo_rate},
    {"target_key": "nihss_documentation_compliance", "current_value": nihss_compliance},
    {"target_key": "consent_form_compliance",     "current_value": consent_rate},
    {"target_key": "thirty_day_readmission",      "current_value": readmission_rate},
    {"target_key": "icu_admission_rate",          "current_value": icu_rate},
])
```

---

## Step 6 — Update pages/03_Operational.py

### 6a — Import targets (same as Step 4a)

### 6b — Update KPI tiles with traffic lights

- Median D2N Time — target key: `door_to_needle_median_minutes`
- Response Time Outlier Rate — target key: `response_time_outlier_rate`
- Encounter type mix — target key: `stroke_alert_volume` (gray — trending only)
- Consult duration — no target (gray)

### 6c — Add benchmark lines to charts

- **D2N detail distribution:**
  ```python
  fig = add_benchmark_vline(fig, 45, "45 min target")
  fig = add_benchmark_vline(fig, 60, "60 min AHA limit", color="#EF4444")
  ```

- **Response time outlier trend:**
  ```python
  fig = add_benchmark_line(fig, 0.05, "Target: ≤5% outliers")
  ```

- **Time-of-day heatmap** — add annotation note:
  ```
  "Peak alert volume hours should align with staffing model"
  ```

### 6d — Add targets panel at bottom of page

```python
render_targets_panel([
    {"target_key": "door_to_needle_median_minutes",  "current_value": median_d2n},
    {"target_key": "response_time_outlier_rate",     "current_value": outlier_rate},
    {"target_key": "decision_to_administration_minutes", "current_value": median_d2a},
])
```

---

## Step 7 — Update pages/04_Financial.py

### 7a — Import targets (same as Step 4a)

### 7b — Update KPI tiles with traffic lights

- Cost per Consult — target key: `cost_per_consult`
  - Calculate as: total_monthly_cost / total_consults_that_month
- Monthly Operating Cost — gray (trending metric, no absolute target)
- Downstream Revenue — gray (trending metric)
- Net Revenue — gray (trending metric)

### 7c — Add benchmark lines to charts

- **Cost per consult trend:**
  ```python
  fig = add_benchmark_line(fig, 300, "Target: ≤$300/consult")
  ```

- **Revenue vs Cost overlay** — no benchmark line needed, the lines themselves tell the story

### 7d — Add targets panel at bottom of page

```python
render_targets_panel([
    {"target_key": "cost_per_consult", "current_value": avg_cost_per_consult},
])
```

---

## Step 8 — Update pages/05_Provider_Performance.py

### 8a — Import targets (same as Step 4a)

### 8b — Update provider comparison table

In the provider comparison table, add a "vs Target" column for each metric:
- D2N Compliance % — show traffic light emoji + value + target
- Median Response Time — show traffic light emoji + value + target
- NIHSS Documentation % — show traffic light emoji + value + target
- Consent Completion % — show traffic light emoji + value + target

Color-code each row using `get_traffic_light()` based on the provider's D2N compliance vs target.

### 8c — Add benchmark lines to provider trend charts

For the per-provider monthly D2N compliance trend:
```python
fig = add_benchmark_line(fig, 0.85, "Target: ≥85%")
```

### 8d — Add targets panel at bottom of page

```python
render_targets_panel([
    {"target_key": "door_to_needle_compliance_60", "current_value": selected_provider_d2n},
    {"target_key": "door_to_neurologist_minutes",  "current_value": selected_provider_response},
    {"target_key": "nihss_documentation_compliance", "current_value": selected_nihss},
    {"target_key": "consent_form_compliance",      "current_value": selected_consent},
])
```

---

## Step 9 — Update utils/sidebar.py

Add a small "Performance Summary" indicator in the sidebar showing overall program health at a glance. Place it below the TeleStroke nav links and above the TeleSitting section.

```python
# In render_sidebar(), after the TeleStroke nav links:

# Load data and calculate overall traffic light
# Show a compact 3-metric summary:

st.sidebar.markdown("""
<div style='background:rgba(255,255,255,0.08);border-radius:6px;
            padding:10px 12px;margin:8px 0;font-size:0.72rem'>
    <div style='color:rgba(255,255,255,0.5);font-size:0.65rem;
                text-transform:uppercase;letter-spacing:0.06em;
                margin-bottom:6px'>Program Health</div>
    <div style='display:flex;justify-content:space-between;margin-bottom:4px'>
        <span style='color:rgba(255,255,255,0.7)'>D2N Compliance</span>
        <span>{d2n_emoji} {d2n_val}%</span>
    </div>
    <div style='display:flex;justify-content:space-between;margin-bottom:4px'>
        <span style='color:rgba(255,255,255,0.7)'>Response Time</span>
        <span>{rt_emoji} {rt_val} min</span>
    </div>
    <div style='display:flex;justify-content:space-between'>
        <span style='color:rgba(255,255,255,0.7)'>Cart Uptime</span>
        <span>{cu_emoji} {cu_val}%</span>
    </div>
</div>
""".format(
    d2n_emoji=d2n_emoji, d2n_val=d2n_val,
    rt_emoji=rt_emoji,   rt_val=rt_val,
    cu_emoji=cu_emoji,   cu_val=cu_val,
), unsafe_allow_html=True)
```

Load the data at the top of `render_sidebar()` using `@st.cache_data` and calculate the three values. Pass the emoji and value strings into the HTML format call.

---

## Step 10 — Verify and Report

After completing all steps:

1. Run: `.venv/bin/python -m streamlit run app.py`

2. Verify on each page:
   - KPI tiles show traffic light emoji and colored left border
   - Each tile shows target value and source citation below the metric
   - All trend charts have red dashed benchmark lines with labels
   - All distribution charts have vertical benchmark lines
   - Targets panel expander appears at bottom of every page
   - Targets panel shows correct current value, target, status, and source
   - Sidebar shows Program Health summary with 3 traffic light indicators
   - Provider Performance table shows per-provider traffic light colors

3. Spot check traffic light logic:
   - D2N at 56.2% should show 🔴 Red (target 85%)
   - Response time at 10.5 min should show 🟢 Green (target ≤20 min)
   - Cart uptime ~96.8% should show 🟡 Amber (target ≥99%, within 10%)

4. Report back with confirmation before pushing to GitHub

**Do not push to GitHub until confirmed.**

---

## Important Notes

- All target values in `utils/targets.py` are industry standards — do NOT change target values without updating the source citation
- The `render_targets_panel()` function uses `st.expander` — it is collapsed by default so it does not clutter the page
- Traffic light logic: green = meeting target, amber = within threshold of target, red = missing target by more than threshold
- For "lower is better" metrics (time-based), green means the value is AT or BELOW the target
- For "higher is better" metrics (compliance %), green means the value is AT or ABOVE the target
- The sidebar Program Health widget loads data on every page render — use `@st.cache_data` to prevent performance issues
- Do not add targets to TeleSitting pages — those KPI definitions are not yet finalized
- Phase 2 fields that are synthetic (LVO, 30-day readmission, ICU) should show a small "⚠️ Synthetic" label next to the traffic light so stakeholders understand the data is not real
