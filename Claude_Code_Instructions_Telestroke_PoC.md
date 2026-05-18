# Claude Code Instructions — Telestroke Dashboard PoC
**Project:** Penn State Health Telestroke Dashboard — Art of the Possible  
**Stack:** Python 3.9.6 · Streamlit · Plotly  
**Goal:** Multi-page Streamlit dashboard with synthetic data demonstrating Phase 1 and Phase 2 Telestroke KPIs with drill-down and filter capability, mimicking a Power BI interface.

---

## Overview

Build a fully functional Streamlit dashboard PoC for the Penn State Health Telestroke program. The app will:

1. Generate 500 realistic synthetic patient records across FY2023-2024, FY2024-2025, and FY2025-2026
2. Serve those records from a local CSV file
3. Render a multi-page dashboard with sidebar navigation mimicking Power BI
4. Display all Phase 1 KPIs on the main overview page
5. Display all Phase 2 KPIs across dedicated sub-pages
6. Support global filters: Fiscal Year, Facility, Date Range, Encounter Type
7. Use Penn State Health navy/teal branding throughout

---

## Step 1 — Project Structure

Create the following folder and file structure inside the project directory:

```
telestroke_poc/
├── app.py                  # Main Streamlit entry point
├── generate_data.py        # Synthetic data generator
├── data/
│   └── telestroke_synthetic.csv   # Generated on first run
├── pages/
│   ├── 01_Phase1_Overview.py
│   ├── 02_Clinical_Outcomes.py
│   ├── 03_Operational_Performance.py
│   ├── 04_Financial.py
│   └── 05_Provider_Performance.py
├── utils/
│   ├── filters.py          # Shared sidebar filter logic
│   ├── charts.py           # Shared Plotly chart helpers
│   └── theme.py            # PSH color constants
└── requirements.txt
```

---

## Step 2 — Requirements File

Create `requirements.txt` with the following:

```
streamlit>=1.32.0
plotly>=5.18.0
pandas>=2.0.0
numpy>=1.24.0
faker>=22.0.0
```

---

## Step 3 — PSH Theme Constants

Create `utils/theme.py` with Penn State Health branding colors:

```python
# Penn State Health Brand Colors
PSH_NAVY     = "#1F3864"
PSH_TEAL     = "#1F7A8C"
PSH_BLUE     = "#378ADD"
PSH_LTBLUE   = "#D6E4F0"
PSH_WHITE    = "#FFFFFF"
PSH_GRAY     = "#F2F2F2"
PSH_AMBER    = "#F59E0B"
PSH_GREEN    = "#10B981"
PSH_RED      = "#EF4444"

# Benchmark colors
BENCHMARK_COLOR  = "#EF4444"   # Red line for targets
COMPLIANCE_PASS  = "#10B981"   # Green for meeting target
COMPLIANCE_FAIL  = "#EF4444"   # Red for missing target

# Chart defaults
FONT_FAMILY = "Segoe UI, Arial, sans-serif"
CHART_BG    = "#FFFFFF"
GRID_COLOR  = "#E5E7EB"
```

---

## Step 4 — Synthetic Data Generator

Create `generate_data.py`. This script generates 500 realistic telestroke records.

### Field requirements (all 54 fields from the governance spec):

**Period fields:**
- `fiscal_year` — one of FY2023-2024, FY2024-2025, FY2025-2026 (roughly 167 records each)
- `month_name` — July through June (distributed across fiscal year)
- `month_number` — 1–12 (July=1)
- `quarter` — Q1 (Jul–Sep), Q2 (Oct–Dec), Q3 (Jan–Mar), Q4 (Apr–Jun)

**Patient & encounter identifiers (anonymized — no real PHI):**
- `mrn` — synthetic 8-digit number (prefix SYN-)
- `fin` — synthetic 10-digit number
- `case_number` — used in FY2025-2026 only (prefix CASE-)
- `facility` — one of: Hershey Medical Center, Holy Spirit, Mount Nittany, Hampden, Good Samaritan, St. Joseph
- `consultant_name` — one of 6 synthetic neurologist names (Dr. A. Singh, Dr. M. Patel, Dr. R. Chen, Dr. L. Torres, Dr. K. Williams, Dr. J. Okafor)
- `encounter_type` — Audio/Video (70%), Phone (20%), Reg-No Consult (10%)

**Clinical presentation timestamps — generate realistic datetime values:**
- `ed_arrival_dt` — distributed across fiscal year months
- `stroke_alert_initiation_dt` — ed_arrival_dt + 5–25 minutes
- `last_known_normal_dt` — ed_arrival_dt minus 30 minutes to 6 hours

**Consult initiation timestamps:**
- `call_to_provider_dt` — stroke_alert_initiation_dt + 2–10 minutes
- `provider_response_dt` — call_to_provider_dt + 1–20 minutes (target ≤15 min)
- `neurologist_evaluation_start_dt` — provider_response_dt + 1–5 minutes

**Treatment decision & administration (Audio/Video only):**
- `treatment_decision_dt` — neurologist_evaluation_start_dt + 5–30 minutes
- `thrombolysis_eligibility_indicator` — Yes (40%), No (60%)
- `treatment_agent` — TNK (for FY2024-2025 and FY2025-2026), tPA (for FY2023-2024), None if not eligible
- `thrombolysis_administration_dt` — treatment_decision_dt + 2–15 minutes (only if eligible)
- `order_entry_dt` — treatment_decision_dt + 1–5 minutes (Phase 2 field)

**Consult closure:**
- `consult_signed_dt` — neurologist_evaluation_start_dt + 20–60 minutes
- `depart_dt` — ed_arrival_dt + 60–240 minutes
- `dido_time_minutes` — derived: depart_dt minus ed_arrival_dt in minutes

**Clinical assessment:**
- `nihss_score` — integer 0–42, weighted toward 4–16 (realistic stroke severity)
- `pre_mrs_score` — integer 0–5, weighted toward 0–1
- `discharge_mrs_score` — integer 0–6
- `ninety_day_mrs_score` — integer 0–6 (Phase 2 field, ~30% missing)
- `nihss_documentation_compliance` — Yes (85%), No (15%)
- `consent_form_completed` — Yes (78%), No (22%)

**Disposition & transfer:**
- `transfer_status` — Transferred (45%), Not Transferred (55%)
- `transfer_destination` — Hershey Medical Center (if transferred), blank otherwise
- `discharge_destination` — Home (40%), Rehab (25%), SNF (15%), Expired (3%), Other (17%)
- `lvo_indicator` — Yes (25%), No (75%) — Phase 2 field

**Procedures & outcomes:**
- `treatment_administered` — Yes if eligible and agent not None, No otherwise
- `stroke_diagnosis` — Ischemic Stroke (55%), TIA (20%), Hemorrhagic Stroke (15%), Mimics (10%)
- `stroke_subtype` — derived from diagnosis
- `admit_status` — Admitted (60%), Observation (25%), Discharged (15%)
- `length_of_stay_days` — integer 1–14 (Phase 2 field)
- `icu_admission` — Yes (20%), No (80%) — Phase 2 field
- `thirty_day_readmission` — Yes (12%), No (88%) — Phase 2 field
- `door_to_needle_time_minutes` — derived: thrombolysis_administration_dt minus ed_arrival_dt (eligible cases only)
- `symptom_to_treatment_time_minutes` — derived: thrombolysis_administration_dt minus last_known_normal_dt

**Quality & outlier flags:**
- `lkn_flag` — Yes if last_known_normal to stroke_alert >= 4.5 hours
- `response_time_outlier_flag` — Yes if provider_response_dt minus call_to_provider_dt > 15 minutes
- `outlier_exclusion_flag` — Yes (~8% of eligible cases)
- `outlier_exception_reason` — one of: Uncontrolled Hypertension, Consent Delay, Extended Treatment Window, None

**Financial (Phase 2):**
- `payer_category` — Medicare (45%), Medicaid (15%), Commercial (30%), Self-Pay (10%)
- `reimbursement_amount` — realistic range $8,000–$45,000 based on admit status and LVO

### Derived KPI fields (add as calculated columns):
- `door_to_needle_compliant` — Yes if door_to_needle_time_minutes <= 60
- `door_to_needle_compliant_45` — Yes if <= 45 minutes
- `door_to_needle_compliant_30` — Yes if <= 30 minutes
- `door_to_neurologist_minutes` — neurologist_evaluation_start_dt minus ed_arrival_dt
- `door_to_cart_minutes` — stroke_alert_initiation_dt minus ed_arrival_dt
- `neurologist_to_decision_minutes` — treatment_decision_dt minus neurologist_evaluation_start_dt
- `decision_to_administration_minutes` — thrombolysis_administration_dt minus treatment_decision_dt
- `time_of_day_block` — Morning (8a–4p), Evening (4p–12a), Night (12a–8a)

### Cart uptime synthetic data:
Generate a separate DataFrame `cart_uptime_df` with monthly cart uptime per facility:
- `fiscal_year`, `month_name`, `facility`, `cart_uptime_pct` (range 94–99.8%)

### Financial synthetic data:
Generate a separate DataFrame `monthly_cost_df`:
- `fiscal_year`, `month_name`, `total_monthly_cost` (range $45,000–$65,000)
- `downstream_revenue` (range $180,000–$420,000)

Save all three DataFrames to `data/` as separate CSV files:
- `telestroke_synthetic.csv`
- `cart_uptime_synthetic.csv`
- `monthly_cost_synthetic.csv`

Print a confirmation summary when generation is complete showing record counts and field counts.

---

## Step 5 — Shared Filter Utility

Create `utils/filters.py`. This module renders a consistent sidebar filter panel used on every page.

```python
# Sidebar filter panel — call render_filters(df) on every page
# Returns filtered dataframe and selected filter values
# Filters to include:
#   - Fiscal Year (multiselect — default all)
#   - Facility / Spoke Site (multiselect — default all)
#   - Encounter Type (multiselect — default all)
#   - Date Range (date range picker using ed_arrival_dt)
#   - Consultant Name (multiselect — default all)
# Display PSH logo placeholder and "Telestroke Dashboard" header in sidebar
# Show active record count at bottom of sidebar: "Showing X of 500 records"
```

---

## Step 6 — Shared Chart Helpers

Create `utils/charts.py` with reusable Plotly chart functions:

```python
# Functions to create:
# kpi_card(value, label, benchmark=None, delta=None, color=PSH_TEAL)
#   — returns a styled metric dict for use with st.metric or plotly indicator
#
# trend_line(df, x_col, y_col, title, benchmark=None, color=PSH_TEAL)
#   — returns Plotly line chart with optional red benchmark line
#
# bar_chart(df, x_col, y_col, title, color=PSH_TEAL, orientation='v')
#   — returns Plotly bar chart
#
# stacked_bar(df, x_col, y_cols, title, colors=None)
#   — returns Plotly stacked bar chart
#
# histogram(df, col, title, bins=20, benchmark=None)
#   — returns Plotly histogram with optional benchmark line
#
# pie_chart(df, values_col, names_col, title)
#   — returns Plotly pie chart
#
# heatmap(df, x_col, y_col, value_col, title)
#   — returns Plotly heatmap
#
# All charts must:
#   - Use PSH navy/teal color scheme from theme.py
#   - Have clean white background
#   - Use Segoe UI font
#   - Include title and axis labels
#   - Be responsive width (use_container_width=True)
```

---

## Step 7 — Main App Entry Point

Create `app.py`:

```python
# app.py — Streamlit entry point
# 
# Configure:
#   - Page title: "PSH Telestroke Dashboard"
#   - Page icon: 🧠
#   - Layout: wide
#   - Sidebar state: expanded
#
# On first run, check if data/telestroke_synthetic.csv exists.
# If not, call generate_data.py automatically.
#
# Render a home/landing page with:
#   - PSH Telestroke Dashboard title (navy, large)
#   - Subtitle: "Art of the Possible — Synthetic Data PoC"
#   - Four summary KPI cards across the top:
#       1. Total Consults (count of all records)
#       2. Overall Door-to-Needle Compliance % (eligible cases <=60 min)
#       3. Average Response Time (median provider response minutes)
#       4. Treatment Rate % (treated / eligible)
#   - A brief description paragraph explaining this is a PoC
#   - Navigation instructions pointing to sidebar pages
#   - A "Last refreshed" timestamp
```

---

## Step 8 — Page 1: Phase 1 Overview

Create `pages/01_Phase1_Overview.py`:

### Layout: Power BI-style with KPI tiles at top, charts below

**Section 1 — KPI Tiles Row (use st.columns)**

Render the following KPI cards across the top of the page. Each card shows current value, benchmark, and a delta indicator:

| KPI | Story | Benchmark |
|---|---|---|
| Door-to-Needle Compliance % | TS-01 | ≥85% (AHA/ASA) |
| Median Door-to-Neurologist (min) | TS-02 | ≤30 min |
| Total Stroke Alerts (month) | TS-04 | N/A |
| Cart Uptime % | TS-05 | ≥99% SLA |
| Median Door-to-Cart (min) | TS-06 | ≤15 min |
| Median Neuro-to-Decision (min) | TS-07 | ≤20 min |
| Median Decision-to-TNK (min) | TS-10 | ≤5 min |

**Section 2 — Charts Row 1 (two columns)**

Left: Monthly stroke alert volume bar chart (TS-04) — x=month, y=count, colored by fiscal year  
Right: Door-to-Needle compliance trend line (TS-01) — monthly % with red benchmark at 85%

**Section 3 — Charts Row 2 (two columns)**

Left: Door-to-Neurologist distribution histogram (TS-02) — bins by minute intervals, benchmark at 30 min  
Right: Door-to-Cart registration trend line (TS-06) — monthly median with benchmark at 15 min

**Section 4 — Charts Row 3 (two columns)**

Left: Neurologist-to-Decision time trend (TS-07) — monthly median with benchmark at 20 min  
Right: Decision-to-TNK time bar chart by facility (TS-10) — benchmark at 5 min

**Section 5 — Door-to-Needle Threshold Buckets (full width)**

Stacked percentage bar chart showing monthly distribution of cases in:
- <30 min (dark teal)
- 30–45 min (medium teal)
- 45–60 min (light blue)
- >60 min (red)

---

## Step 9 — Page 2: Clinical Outcomes (Phase 2)

Create `pages/02_Clinical_Outcomes.py`:

**Section 1 — KPI Tiles**
- Treatment Rate % (treated / eligible)
- LVO Detection Rate %
- 30-Day Readmission Rate %
- ICU Admission Rate %
- NIHSS Documentation Compliance %
- Consent Form Completion %

**Section 2 — Charts**
- Stroke diagnosis distribution pie chart
- Discharge disposition bar chart
- Pre-mRS vs Discharge mRS comparison (grouped bar)
- NIHSS score distribution histogram
- Transfer volume by facility (TS-12 style stacked bar: total vs LVO)
- 90-Day mRS Score distribution (Phase 2 field — note partial data)

**Section 3 — Outlier Exclusion (TS-22)**
- KPI showing raw vs adjusted door-to-needle compliance %
- Table showing outlier exception reason distribution
- Toggle: Raw vs Adjusted compliance trend line

---

## Step 10 — Page 3: Operational Performance (Phase 2)

Create `pages/03_Operational_Performance.py`:

**Section 1 — KPI Tiles**
- Median Door-to-Needle Time (TS-14)
- Response Time Outlier Rate %
- Average Consult Duration (TS-20)
- ED vs Inpatient split %

**Section 2 — Charts**
- Phone vs Audio-Video breakdown pie + monthly trend (TS-10 Phase 2)
- Volume by site distribution sortable bar chart (TS-11)
- Time-of-day analysis heatmap — x=facility, y=time block, value=consult volume (TS-18)
- ED vs Inpatient side-by-side KPI comparison (TS-17)
- Flight vs Ground transport stacked bar (TS-13) — note as estimated

**Section 3 — Decision-to-Administration Delay Tracking (TS-16)**
- Trend line: decision-to-TNK by month
- Site comparison table: median decision-to-TNK per facility
- Outliers highlighted where >5 min

---

## Step 11 — Page 4: Financial Summary (Phase 2)

Create `pages/04_Financial.py`:

**Section 1 — KPI Tiles**
- Monthly Cost of Delivery (TS-08)
- Downstream Revenue from Transfers (TS-09)
- Net Revenue (Revenue minus Cost)
- Payer Mix % (Medicare dominant)

**Section 2 — Charts**
- Monthly cost trend line (TS-08)
- Downstream revenue bar chart by month (TS-09)
- Payer category distribution pie chart
- Revenue vs Cost overlay line chart by month
- Reimbursement amount distribution histogram

**Note:** Label all financial charts with: *"PoC — Synthetic data only. For illustrative purposes."*

---

## Step 12 — Page 5: Provider Performance (Phase 2 — Restricted)

Create `pages/05_Provider_Performance.py`:

**Access note:** Add a yellow `st.warning` banner at top:  
*"In production, this page will require restricted access. Displayed here for PoC demonstration purposes only."*

**Section 1 — Provider Selector**
- Dropdown to select individual consultant
- Show provider summary KPI cards:
  - Total consults
  - Door-to-Needle compliance %
  - Median response time
  - NIHSS documentation compliance %
  - Consent form completion %

**Section 2 — Provider Comparison Table (TS-19)**
- Table showing all providers side by side:
  - Volume, D2N compliance %, median response time, avg handle time
  - Color-coded: green if meeting benchmark, red if not
- Monthly trend lines per selected provider

---

## Step 13 — Sidebar Navigation & Global Filters

In every page file, import and call `render_filters(df)` from `utils/filters.py` at the top.

The sidebar should show:
- 🧠 **PSH Telestroke Dashboard** header in navy
- *Art of the Possible — PoC* subtitle in gray italic
- Divider
- Filter controls (Fiscal Year, Facility, Date Range, Encounter Type, Consultant)
- Divider
- Active record count
- Divider
- Navigation links (Streamlit handles page nav natively via the pages/ folder)

---

## Step 14 — Styling & Layout Requirements

Apply the following across all pages:

```python
# Add to app.py and every page:
st.markdown("""
<style>
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #1F3864;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    /* KPI card styling */
    [data-testid="metric-container"] {
        background-color: #F2F2F2;
        border: 1px solid #D6E4F0;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #1F7A8C;
    }
    /* Page title */
    h1 { color: #1F3864; font-family: 'Segoe UI', Arial, sans-serif; }
    h2 { color: #1F7A8C; font-family: 'Segoe UI', Arial, sans-serif; }
    /* Benchmark badge */
    .benchmark { font-size: 11px; color: #6B7280; }
</style>
""", unsafe_allow_html=True)
```

---

## Step 15 — Run Instructions

After creating all files, provide the following run instructions:

```bash
# Install dependencies
pip install -r requirements.txt

# Generate synthetic data (first time only)
python generate_data.py

# Launch dashboard
streamlit run app.py
```

The app should open automatically at `http://localhost:8501`

---

## Important Notes for Claude Code

1. **Do not use real patient data** — all data must be synthetic and clearly labeled as such throughout the UI
2. **All timestamps must be internally consistent** — ed_arrival_dt < stroke_alert_initiation_dt < provider_response_dt < neurologist_evaluation_start_dt < treatment_decision_dt < thrombolysis_administration_dt
3. **Null handling** — Phase 2 fields should have realistic missing data rates (10–30%) to simulate real-world incompleteness
4. **Encounter type filtering** — some KPIs only apply to Audio/Video consults (treatment, door-to-needle). Filter automatically and note it in the chart subtitle
5. **Fiscal year months** — FY runs July to June. Month Number 1 = July, 12 = June. Ensure all trend charts sort correctly
6. **Benchmark lines** — every time-based KPI must show a visible red benchmark line on charts
7. **Responsive layout** — use `use_container_width=True` on all Plotly charts
8. **Error handling** — if a filtered dataset returns zero rows, show a friendly `st.info` message rather than a broken chart
9. **Performance** — use `@st.cache_data` on all data loading functions to prevent reloading on every interaction
10. **Phase labels** — Phase 2 KPIs and charts should be subtly labeled with a teal "Phase 2" badge so stakeholders understand what is currently available vs. future state
