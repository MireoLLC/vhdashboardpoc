# Claude Code Instructions — Session 2
# TeleSitting Dashboard — Synthetic Data + Pages
**Project:** Penn State Health Virtual Health Dashboard PoC  
**Session:** 2 of 2  
**Prerequisite:** Session 1 must be complete and deployed before starting this session  
**Scope:** Generate TeleSitting synthetic data, build 2 TeleSitting pages, activate TeleSitting card

---

## Pre-Flight Check

Before writing any code:

1. Confirm working directory is `/Users/chanakaperera/Dev/vhdashboardpoc`
2. List all files — confirm Session 1 structure is in place:
   - `pages/telestroke/` exists with 5 TS page files
   - `pages/telesitting/` exists (currently empty with .gitkeep)
   - `app.py` has password gate and program selector
   - `.streamlit/secrets.toml` exists locally
3. Confirm `data/telestroke_synthetic.csv` exists
4. Tell me your plan before touching any files — wait for my confirmation

---

## Step 1 — Generate TeleSitting Synthetic Data

Update `generate_data.py` to add a new function `generate_telesitting_data()`.

### Patient Log — 500 records

**Period fields:**
- `fiscal_year` — FY2023-2024, FY2024-2025, FY2025-2026 (~167 records each)
- `month_name` — July through June distributed across fiscal year
- `month_number` — 1–12 (July=1, June=12)
- `quarter` — Q1 (Jul–Sep), Q2 (Oct–Dec), Q3 (Jan–Mar), Q4 (Apr–Jun)

**Patient & encounter identifiers:**
- `fin` — synthetic FIN (prefix FIN-, 10 digits)
- `first_name`, `last_name` — synthetic names via Faker
- `hospital` — one of: HSH, PMC, Holy Spirit, Hampden, Good Samaritan, St. Joseph (weighted: HSH 35%, PMC 25%, others 10% each)
- `unit` — hospital-specific units:
  - HSH: HSH_6ORTHO, HSH_4MED, HSH_NEURO, HSH_ICU
  - PMC: PMC_3SURG, PMC_MED, PMC_ICU
  - Others: one generic unit each
- `room` — synthetic room number (101–420)
- `cart_location` — Cart (70%), Wall Mount (30%)
- `service` — Medicine (30%), Orthopedics (20%), Neurology (15%), Surgery (15%), ICU (12%), Cardiology (8%)
- `nurse` — one of 10 synthetic nurse names
- `ascom` — synthetic 4-digit Ascom device number

**Monitoring session timestamps:**
- `admit_dt` — distributed across fiscal year months
- `admitting_tpa` — one of 8 synthetic TPA names: T. Johnson, M. Rivera, K. Williams, D. Chen, A. Patel, S. Thompson, R. Martinez, L. Anderson
- `discharge_dt` — admit_dt + 4 to 72 hours (weighted toward 12–48 hours)
- `discharging_tpa` — same pool as admitting TPA
- `total_hours_monitored` — derived: discharge_dt minus admit_dt in decimal hours

**Clinical observation inputs:**
- `reason_for_observation` — Fall Risk (40%), Confused (25%), Pulling Lines (15%), Aggressive Behavior (8%), Elopement (7%), Other (5%)
- `redirectable` — Yes (65%), No (35%)
- `risk_level` — High (45%), Medium (35%), Low (20%)
- `morse_score` — integer 25–85, weighted toward 45–65 using normal distribution
- `educated_on_program` — Yes (82%), No (18%)
- `patient_notes` — leave empty string (narrative field — not used)

**Device & equipment flags:**
- `trach_indicator` — Yes (8%), No (92%)
- `o2_indicator` — Yes (35%), No (65%)
- `heart_monitor_indicator` — Yes (28%), No (72%)
- `iv_indicator` — Yes (72%), No (28%)
- `pulse_oximeter_indicator` — Yes (45%), No (55%)
- `central_line_indicator` — Yes (15%), No (85%)
- `feed_tube_indicator` — Yes (12%), No (88%)
- `urinary_catheter_indicator` — Yes (25%), No (75%)
- `surgical_drain_indicator` — Yes (10%), No (90%)
- `wound_dressing_indicator` — Yes (18%), No (82%)

**Known unusable fields (include but mark as empty/NA):**
- `falls` — leave empty (field not used by TPAs)
- `falls_with_injury` — leave empty (field not used)
- `midas_date` — leave empty (not consistently completed)
- `reason_for_midas` — leave empty (not consistently completed)

**Derived fields:**
- `device_count` — count of Yes device flags per record (0–10)
- `high_complexity` — Yes if device_count >= 3, No otherwise

### Redirect Log — 1,500 redirect events

Generate approximately 3 redirect events per patient on average, linked by FIN.

- `redirect_dt` — random datetime during the patient's monitoring session (between admit_dt and discharge_dt)
- `tpa` — same pool of 8 TPA names
- `fin` — linked to patient log FIN
- `first_name`, `last_name` — same as patient log (linked by FIN)
- `hospital`, `unit` — same as patient log entry for that FIN
- `reason_for_observation` — same as patient log entry for that FIN
- `redirectable` — Yes (70%), No (30%)
- `notify_activated` — Yes (18%), No (82%) — note: known data quality issues with accidental activations

**Derived redirect fields:**
- `redirect_count_per_patient` — count of redirect events per FIN (add to patient log)
- `notify_rate_per_patient` — notify_activated count / total redirects per FIN (add to patient log)

### Financial Summary — Monthly (36 rows, one per month across 3 fiscal years)

- `fiscal_year`, `month_name`, `month_number`
- `platform_licensing_cost` — 15,000–18,000 per month
- `tpa_labor_cost` — 45,000–65,000 per month
- `equipment_cost` — 3,000–5,000 per month
- `total_operating_cost` — sum of above three
- `baseline_sitter_hours` — 800–1,200 per month (pre-TeleSitting baseline)
- `actual_sitter_hours` — 200–400 per month (significantly reduced with TeleSitting)
- `loaded_sitter_hourly_rate` — 35–42 dollars (consistent per fiscal year)
- `labor_cost_avoidance` — (baseline_sitter_hours minus actual_sitter_hours) * loaded_sitter_hourly_rate
- `net_savings` — labor_cost_avoidance minus total_operating_cost

### Save files:
- `data/telesitting_patient_log.csv` — 500 patient records
- `data/telesitting_redirect_log.csv` — 1,500 redirect events
- `data/telesitting_cost.csv` — 36 monthly financial records

### Print generation summary:
```
TeleSitting Patient Log:   500 rows x [N] fields → telesitting_patient_log.csv
TeleSitting Redirect Log: 1500 rows x [N] fields → telesitting_redirect_log.csv
TeleSitting Cost Data:      36 rows x [N] fields → telesitting_cost.csv

Hospital mix:    HSH [N]% | PMC [N]% | ...
Reason mix:      Fall Risk [N]% | Confused [N]% | ...
Avg hours/patient: [N] hours
Notify activation rate: [N]%
Avg redirects/patient: [N]
```

---

## Step 2 — Build TeleSitting Page 1: Phase 1 Overview

Create `pages/telesitting/01_TSIT_Phase1_Overview.py`

### Page header:
```python
import streamlit as st
import pandas as pd
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.theme import *
from utils.charts import *
from utils.filters import render_telesitting_filters

# Back button
if st.button("← TeleSitting Home"):
    st.session_state.program = "telesitting"
    st.switch_page("app.py")

st.title("👁 TeleSitting — Phase 1 Overview")
st.markdown("*Operational and financial performance metrics*")
st.divider()
```

### Load data:
```python
@st.cache_data
def load_telesitting_data():
    base = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    pl = pd.read_csv(os.path.join(base, 'telesitting_patient_log.csv'), parse_dates=['admit_dt','discharge_dt'])
    rl = pd.read_csv(os.path.join(base, 'telesitting_redirect_log.csv'), parse_dates=['redirect_dt'])
    cost = pd.read_csv(os.path.join(base, 'telesitting_cost.csv'))
    return pl, rl, cost
```

### Apply sidebar filters (fiscal year, hospital, date range)

### Finance data note banner:
```python
st.info("💡 Finance metrics (TSIT-03, TSIT-04, TSIT-05) are shown with synthetic data. "
        "Production values require confirmed data from Finance (Melissa Eberly).")
```

### KPI Tiles Row (6 tiles across):

**Tile 1 — TSIT-08: Peak Monitored Census**
- Value: max patients monitored simultaneously (approximate from synthetic data)
- Label: "Peak Monitored Census"
- Border: teal
- Note: "Source: Caregility platform"

**Tile 2 — TSIT-07: Avg Monitored Census**
- Value: average daily monitored patients (derived from total_hours_monitored / days in period)
- Label: "Avg Daily Census"
- Border: teal
- Note: "⚠️ Approximation — methodology disclosed"

**Tile 3 — TSIT-03: Sitter Hours Avoided**
- Value: sum of (baseline_sitter_hours minus actual_sitter_hours) for filtered period
- Label: "Sitter Hours Avoided"
- Border: green
- Badge: "Requires Finance Data" in amber

**Tile 4 — TSIT-04: Gross Labor Cost Avoidance**
- Value: sum of labor_cost_avoidance formatted as $X,XXX,XXX
- Label: "Gross Labor Cost Avoidance"
- Border: green
- Badge: "Requires Finance Data" in amber

**Tile 5 — TSIT-05: Monthly Operating Cost**
- Value: average monthly total_operating_cost formatted as $XX,XXX
- Label: "Avg Monthly Operating Cost"
- Border: navy
- Badge: "Requires Finance Data" in amber

**Tile 6 — TSIT-09: Conversion to Bedside 1:1**
- Value: synthetic 8.2% conversion rate
- Label: "Conversion to Bedside 1:1"
- Border: amber
- Note: "⚠️ Tracked via email since Feb 2026 only"

### Charts Section 1 — Census & Volume (2 columns):

Left: Monthly monitored patient volume bar chart
- X: month_name sorted by fiscal year then month_number
- Y: count of unique FINs
- Color: by fiscal year
- Title: "Monthly Monitored Patient Volume"
- Benchmark line: none

Right: Monitored hours by hospital bar chart
- X: hospital
- Y: sum of total_hours_monitored
- Color: teal gradient
- Title: "Total Monitoring Hours by Facility"

### Charts Section 2 — Cost Avoidance (2 columns):

Left: Sitter hours baseline vs actual overlay line chart
- Two lines: baseline_sitter_hours (red dashed) and actual_sitter_hours (teal solid)
- X: month_name
- Title: "Sitter Hours: Baseline vs Actual"
- Legend clearly labeled

Right: Labor cost avoidance trend line
- X: month_name
- Y: labor_cost_avoidance
- Color: green
- Title: "Monthly Labor Cost Avoidance ($)"
- Cumulative total shown as annotation

### Charts Section 3 — Observation Profile (2 columns):

Left: Reason for observation pie chart
- Values: count per reason_for_observation
- Colors: PSH palette
- Title: "Reason for Monitoring Placement"

Right: Risk level by facility stacked bar
- X: hospital
- Y: count
- Stack: risk_level (High/Medium/Low)
- Colors: red/amber/green
- Title: "Risk Level Distribution by Facility"

### Charts Section 4 — Monitoring Patterns (2 columns):

Left: Monitoring duration histogram
- X: total_hours_monitored binned (0-4, 4-8, 8-12, 12-24, 24-48, 48+)
- Y: count
- Color: teal
- Title: "Monitoring Session Duration Distribution"
- Median line annotation

Right: Redirects per patient distribution
- X: redirect_count_per_patient
- Y: count
- Color: navy
- Title: "Redirect Events per Patient"
- Mean annotation

---

## Step 3 — Build TeleSitting Page 2: Clinical Safety

Create `pages/telesitting/02_TSIT_Clinical_Safety.py`

### Page header:
```python
# Back button
if st.button("← TeleSitting Home"):
    st.session_state.program = "telesitting"
    st.switch_page("app.py")

st.title("👁 TeleSitting — Clinical Safety")
st.markdown("*Patient safety outcomes and intervention effectiveness*")
st.divider()
```

### MIDAS crosswalk warning banner:
```python
st.warning("⚠️ Phase 2 clinical safety metrics (TSIT-01, TSIT-02, TSIT-10, TSIT-12) require the "
           "FIN-to-MRN crosswalk to link TeleSitting records with MIDAS safety data. "
           "All values shown here are synthetic. Production metrics are blocked pending "
           "crosswalk resolution with PSH health informatics.")
```

### KPI Tiles Row (6 tiles):

**Tile 1 — TSIT-10: Falls in Monitored Cohort**
- Value: synthetic count (~12 per 500 patients)
- Label: "Falls — Monitored Cohort"
- Border: red
- Badge: "🔗 Requires MIDAS Crosswalk" in red

**Tile 2 — TSIT-01: Falls with Injury Rate**
- Value: synthetic ~4.2% of monitored patients
- Label: "Falls with Injury Rate"
- Border: red
- Badge: "🔗 Requires MIDAS Crosswalk" in red

**Tile 3 — TSIT-11: Device Removal Events**
- Value: synthetic count derived from redirect log (coded from notify_activated events)
- Label: "Device Removal Events"
- Border: amber
- Note: "⚠️ Requires redirect log coding framework"

**Tile 4 — TSIT-12: Restraint Utilization Rate**
- Value: synthetic ~3.1%
- Label: "Restraint Utilization Rate"
- Border: red
- Badge: "🔗 Requires MIDAS Crosswalk" in red

**Tile 5 — TSIT-14: TeleSitting Utilization Rate**
- Value: synthetic ~68% (monitored hours / staffed hours)
- Label: "Utilization Rate"
- Border: teal
- Note: "Denominator requires scheduling system data"

**Tile 6 — TSIT-15: Avg Escalation Response Time**
- Value: synthetic median 2.8 minutes
- Label: "Avg Escalation Response"
- Border: teal
- Note: "⚠️ Notify Activated field has known data quality issues"

### Charts Section 1 — Redirect Effectiveness (2 columns):

Left: Redirect compliance rate by hospital
- Grouped bar: redirectable Yes vs No per hospital
- Colors: green (Yes) and red (No)
- Title: "Redirect Compliance Rate by Facility"
- Y axis: percentage

Right: Notify activation trend by month
- Line chart: notify_activated count per month
- Color: amber
- Title: "Notify Activations by Month"
- Note annotation: "Includes accidental activations"

### Charts Section 2 — Device & Complexity (2 columns):

Left: Device indicator heatmap
- X: hospital
- Y: device type (O2, IV, Central Line, etc.)
- Value: % of patients with each device per hospital
- Color scale: light to dark teal
- Title: "Device Prevalence by Facility (%)"

Right: Device count distribution
- Bar chart: count of patients by device_count (0,1,2,3,4,5+)
- Color: navy gradient
- Title: "Number of Devices per Patient"
- Annotation: avg device count

### Charts Section 3 — Patient Profile (2 columns):

Left: Morse score distribution histogram
- X: morse_score binned (0-24, 25-44, 45-54, 55-64, 65-74, 75+)
- Color: teal
- Title: "Morse Fall Scale Score Distribution"
- Risk threshold lines: 25 (low risk), 45 (medium), 55 (high)

Right: Monitored hours by service line
- Horizontal bar chart
- X: total_hours_monitored sum
- Y: service
- Color: teal
- Title: "Monitoring Hours by Service Line"

### Charts Section 4 — Data Quality Flags (full width):

Display a styled table showing known data quality issues:

| Field | Issue | Status | Recommendation |
|-------|-------|--------|----------------|
| Falls | Not used by TPAs | ⛔ Unusable | Source from MIDAS via crosswalk |
| Falls With Injury | TPAs not informed of outcomes | ⛔ Unusable | Source from MIDAS via crosswalk |
| Midas Date | Not consistently completed | ⛔ Unusable | Remove from collection |
| Reason For Midas | Not consistently completed | ⛔ Unusable | Remove from collection |
| Notify Activated | Accidental activations occur | ⚠️ Unreliable | Reconcile with iObserver downloads |
| Problem & Redirect Method | Narrative free-text | ⚠️ Unstructured | Requires coding framework |

Style table with color-coded status column: red for Unusable, amber for Unreliable.

---

## Step 4 — Activate TeleSitting Card on Landing Page

Update `app.py` — change the TeleSitting program card from "Coming Soon" to fully active:

**Updated RIGHT CARD — TeleSitting:**
```
👁 TeleSitting Dashboard
─────────────────────────────
Remote patient monitoring,
safety outcomes, and cost
avoidance metrics across
PSH facilities.

📊 500 records  |  FY2023–FY2026  |  2 pages
[Phase 1] [Phase 2]

[  Enter Dashboard →  ]
```
- Card border: 2px solid #1F7A8C
- Card background: #EBF5FB
- Button: active teal style
- On click: `st.session_state.program = "telesitting"` then `st.rerun()`
- Remove "Coming Soon" badge

### Add TeleSitting Landing Page to app.py Level 2:

When `st.session_state.program == "telesitting"` show:

**Back button:** "← All Programs"

**Program header:**
- "👁 TeleSitting Dashboard" in large navy
- "Penn State Health · Art of the Possible PoC" in teal italic
- Synthetic data badge

**KPI Summary Row (4 tiles):**
1. Total Patients Monitored — count of unique FINs
2. Total Redirect Events — count of redirect log records
3. Avg Hours per Patient — mean total_hours_monitored
4. Notify Activation Rate — % of redirect events with notify_activated = Yes

**Quick Stats Row (3 columns):**
- Left: Hospital distribution donut chart
- Middle: Reason for observation bar chart (top 5)
- Right: Data completeness stat — "X of 14 fields fully usable" with teal/red indicator

**Navigation Cards (2 cards):**
1. **📊 Phase 1 Overview** — "Census, cost avoidance, sitter hours, monitoring patterns" — [Phase 1 — teal badge]
2. **🛡 Clinical Safety** — "Device removals, redirect compliance, escalation response, data quality flags" — [Phase 2 — navy badge]

**Footer:** Same synthetic data disclaimer as TeleStroke

### Update Sidebar for TeleSitting:

When `st.session_state.program == "telesitting"`:
```
👁 TeleSitting Dashboard
─────────────────────────
Navigate to:
• Phase 1 Overview
• Clinical Safety
─────────────────────────
[← All Programs]
```

---

## Step 5 — Update utils/filters.py

Add `render_telesitting_filters(pl_df, rl_df)` function:

```python
def render_telesitting_filters(pl_df, rl_df):
    """
    Renders TeleSitting sidebar filters.
    Returns filtered patient log df, filtered redirect log df, and filter values.
    Filters: Fiscal Year, Hospital, Date Range, Risk Level
    """
    st.sidebar.markdown("### Filters")

    # Fiscal Year
    fiscal_years = sorted(pl_df['fiscal_year'].unique().tolist())
    selected_fy = st.sidebar.multiselect("Fiscal Year", fiscal_years, default=fiscal_years)

    # Hospital
    hospitals = sorted(pl_df['hospital'].unique().tolist())
    selected_hospitals = st.sidebar.multiselect("Hospital", hospitals, default=hospitals)

    # Date Range
    min_date = pl_df['admit_dt'].min().date()
    max_date = pl_df['admit_dt'].max().date()
    date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date),
                                        min_value=min_date, max_value=max_date)

    # Risk Level
    risk_levels = ['High', 'Medium', 'Low']
    selected_risk = st.sidebar.multiselect("Risk Level", risk_levels, default=risk_levels)

    # Apply filters
    filtered_pl = pl_df[
        (pl_df['fiscal_year'].isin(selected_fy)) &
        (pl_df['hospital'].isin(selected_hospitals)) &
        (pl_df['risk_level'].isin(selected_risk))
    ]

    if len(date_range) == 2:
        filtered_pl = filtered_pl[
            (filtered_pl['admit_dt'].dt.date >= date_range[0]) &
            (filtered_pl['admit_dt'].dt.date <= date_range[1])
        ]

    # Filter redirect log by matching FINs
    filtered_rl = rl_df[rl_df['fin'].isin(filtered_pl['fin'])]

    # Show record count
    st.sidebar.divider()
    st.sidebar.caption(f"Showing {len(filtered_pl):,} of {len(pl_df):,} patients")
    st.sidebar.caption(f"{len(filtered_rl):,} redirect events")

    return filtered_pl, filtered_rl, {
        'fiscal_years': selected_fy,
        'hospitals': selected_hospitals,
        'date_range': date_range,
        'risk_levels': selected_risk
    }
```

---

## Step 6 — Verify and Report

After completing all steps:

1. Run `python generate_data.py` — confirm all 5 CSV files generate:
   - `telestroke_synthetic.csv`
   - `cart_uptime_synthetic.csv`
   - `monthly_cost_synthetic.csv`
   - `telesitting_patient_log.csv`
   - `telesitting_redirect_log.csv`
   - `telesitting_cost.csv`

2. Run `.venv/bin/streamlit run app.py`

3. Verify full flow:
   - Login with `pocvhchartskpi` ✓
   - Both program cards active on landing page ✓
   - TeleStroke landing page and all 5 pages load ✓
   - TeleSitting landing page loads with KPI tiles ✓
   - TeleSitting Phase 1 Overview loads with all charts ✓
   - TeleSitting Clinical Safety loads with MIDAS warning ✓
   - Back buttons work on all pages ✓
   - Sidebar updates correctly for each program ✓
   - Filters work on both TeleStroke and TeleSitting pages ✓
   - No broken imports or path errors ✓

4. Report back with:
   - Complete file list
   - Record counts for all CSVs
   - Any errors or warnings
   - Confirmation ready to push to GitHub

**Do not push to GitHub until confirmed.**

---

## Step 7 — Pre-Push Checklist

Before pushing confirm:

```bash
# Verify secrets not tracked
git status
# .streamlit/secrets.toml should NOT appear

# Verify .gitignore is correct
cat .gitignore

# Stage all changes
git add .
git status  # Review what will be committed

# Commit
git commit -m "Session 2 - TeleSitting dashboard + unified program selector"

# Push
git push origin main
```

After pushing, go to Streamlit Community Cloud:
- Add secret: `APP_PASSWORD = "pocvhchartskpi"`
- Click Reboot app
- Verify live URL works end to end

---

## Important Notes

- TeleSitting data uses FIN not MRN — this is intentional per the governance spec
- MIDAS-dependent KPIs must be clearly badged as requiring crosswalk — do not show fabricated safety numbers without the warning banner
- The data quality flags table in Clinical Safety is important for stakeholder transparency — do not skip it
- All financial metrics must show the "Requires Finance Data" badge
- Notify activation rate should reflect the known 18% synthetic rate with the data quality caveat
- Use `@st.cache_data` on all data loading functions in both page files
