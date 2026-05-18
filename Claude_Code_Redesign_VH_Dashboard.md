# Claude Code Instructions — Full Redesign
# VH Dashboard — Clean Architecture
**Project:** Penn State Health Virtual Health Dashboard PoC  
**Session:** Full redesign — keep existing chart/page content, restructure shell  
**Design decisions:**
- Login → straight to TeleStroke Phase 1 Overview (no landing page)
- Left sidebar organized into two sections: TeleStroke PoC and TeleSitting PoC
- Filters move to top of each page as horizontal filter bar
- IBM Plex Sans font throughout via Google Fonts
- No "Art of the Possible" anywhere
- No program selector landing page
- TeleSitting section shows "Coming Soon" header only — no page links visible

---

## Pre-Flight Check

Before writing any code:

1. Confirm working directory is `/Users/chanakaperera/Dev/vhdashboardpoc`
2. List all files and folders
3. Confirm `.venv/` exists
4. Confirm `data/telestroke_synthetic.csv` exists
5. List all files currently in `pages/`
6. Summarize your plan and wait for confirmation before making any changes

---

## Step 1 — Clean Up Existing Structure

### Delete or clear these files:
- `app.py` — rewrite from scratch (do not keep any existing content)
- `.streamlit/config.toml` — rewrite from scratch
- `utils/theme.py` — rewrite from scratch
- `utils/filters.py` — rewrite from scratch

### Keep these files unchanged (content only — paths may change):
- All page files in `pages/` — keep all chart and KPI logic intact
- `utils/charts.py` — keep unchanged
- `generate_data.py` — keep unchanged
- `data/*.csv` — keep unchanged
- `requirements.txt` — update only if new packages needed

### Rename page files to clean names without emoji or TS_ prefix:
```
pages/1_📊_Phase1_Overview.py     → pages/01_Phase1_Overview.py
pages/2_🏥_Clinical_Outcomes.py   → pages/02_Clinical_Outcomes.py
pages/3_⚙️_Operational.py         → pages/03_Operational.py
pages/4_💰_Financial.py           → pages/04_Financial.py
pages/5_🔒_Provider.py            → pages/05_Provider_Performance.py
```
Use `git mv` for all renames to preserve history.

---

## Step 2 — Google Fonts Setup

### Add IBM Plex Sans to requirements.txt:
No pip package needed — loaded via HTML injection.

### Create the font injection function in `utils/theme.py`:

IBM Plex Sans is loaded from Google Fonts CDN. Inject it on every page via HTML.

The font weights needed:
- 300 (Light) — for captions and small labels
- 400 (Regular) — for body text
- 500 (Medium) — for KPI values and card labels
- 600 (SemiBold) — for section headers
- 700 (Bold) — for page titles and sidebar section headers

---

## Step 3 — Rewrite utils/theme.py

```python
# utils/theme.py
# PSH Brand colors and global CSS

# Brand colors
PSH_NAVY     = "#1F3864"
PSH_TEAL     = "#1F7A8C"
PSH_BLUE     = "#378ADD"
PSH_LTBLUE   = "#D6E4F0"
PSH_WHITE    = "#FFFFFF"
PSH_GRAY     = "#F4F6F9"
PSH_MIDGRAY  = "#E2E6EA"
PSH_DARKGRAY = "#6B7280"
PSH_AMBER    = "#F59E0B"
PSH_GREEN    = "#10B981"
PSH_RED      = "#EF4444"

FONT_FAMILY  = "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif"

BENCHMARK_COLOR = "#EF4444"
COMPLIANCE_PASS = "#10B981"
COMPLIANCE_FAIL = "#EF4444"

CHART_BG    = "#FFFFFF"
GRID_COLOR  = "#E5E7EB"

def get_global_css():
    """
    Returns CSS string with IBM Plex Sans font import and
    global style overrides for the entire app.
    Call this once per page via st.markdown(get_global_css(), unsafe_allow_html=True)
    """
    return """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
/* ── Global font override ── */
html, body, [class*="css"], [data-testid],
h1, h2, h3, h4, h5, h6,
p, span, div, label, button,
.stMarkdown, .stText, .stMetric,
[data-testid="stMarkdownContainer"] *,
[data-testid="stSidebar"] * {
    font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Heading sizes and weights ── */
h1, [data-testid="stMarkdownContainer"] h1 {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: #1F3864 !important;
    letter-spacing: -0.02em !important;
    line-height: 1.2 !important;
    margin-bottom: 0.25rem !important;
}
h2, [data-testid="stMarkdownContainer"] h2 {
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    color: #1F3864 !important;
    letter-spacing: -0.01em !important;
}
h3, [data-testid="stMarkdownContainer"] h3 {
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: #1F7A8C !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #1F3864 !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stMarkdown p {
    color: rgba(255,255,255,0.65) !important;
    font-size: 0.75rem !important;
}

/* ── Hide default Streamlit sidebar nav ── */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ── Main content area ── */
.main .block-container {
    padding-top: 1.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1400px !important;
}

/* ── Filter bar at top of page ── */
.filter-bar {
    background: #F4F6F9;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 20px;
    border: 1px solid #E2E6EA;
}

/* ── KPI cards ── */
.kpi-card {
    background: white;
    border-radius: 8px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    border-left: 4px solid #1F7A8C;
    height: 100%;
}
.kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1F3864;
    line-height: 1.1;
    margin: 4px 0;
}
.kpi-label {
    font-size: 0.78rem;
    font-weight: 500;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.kpi-benchmark {
    font-size: 0.72rem;
    color: #6B7280;
    margin-top: 4px;
}

/* ── Phase badges ── */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-phase1 { background: #1F7A8C; color: white; }
.badge-phase2 { background: #1F3864; color: white; }
.badge-coming { background: #F59E0B; color: white; }
.badge-midas  { background: #EF4444; color: white; }
.badge-finance { background: #F59E0B; color: white; }

/* ── Metric containers ── */
[data-testid="metric-container"] {
    background: white !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}
[data-testid="metric-container"] label {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #6B7280 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #1F3864 !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #E2E6EA !important;
    margin: 1rem 0 !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
}

/* ── Selectbox and multiselect ── */
.stSelectbox label, .stMultiSelect label, .stDateInput label {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #6B7280 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}

/* ── Streamlit tabs ── */
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
}

/* ── Section headers inside pages ── */
.section-header {
    font-size: 0.85rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 1.5rem 0 0.75rem;
    padding-bottom: 6px;
    border-bottom: 1px solid #E2E6EA;
}
</style>
"""
```

---

## Step 4 — Rewrite utils/filters.py

Create a new `render_filters(df, program="telestroke")` function that renders a **horizontal filter bar at the top of each page** — not in the sidebar.

```python
# utils/filters.py

import streamlit as st
import pandas as pd
from datetime import datetime

def render_telestroke_filters(df):
    """
    Renders a horizontal filter bar at the top of the page.
    Returns filtered dataframe.
    Uses st.columns for horizontal layout.
    Filters: Fiscal Year, Facility, Encounter Type, Consultant, Date Range
    """
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1.5, 1.5, 2])
        
        with col1:
            fiscal_years = sorted(df['fiscal_year'].unique().tolist())
            selected_fy = st.multiselect(
                "Fiscal Year",
                options=fiscal_years,
                default=fiscal_years,
                key="filter_fy"
            )
        
        with col2:
            facilities = sorted(df['facility'].unique().tolist())
            selected_facilities = st.multiselect(
                "Facility",
                options=facilities,
                default=facilities,
                key="filter_facility"
            )
        
        with col3:
            enc_types = sorted(df['encounter_type'].unique().tolist())
            selected_enc = st.multiselect(
                "Encounter Type",
                options=enc_types,
                default=enc_types,
                key="filter_enc_type"
            )
        
        with col4:
            consultants = sorted(df['consultant_name'].unique().tolist())
            selected_consultants = st.multiselect(
                "Consultant",
                options=consultants,
                default=consultants,
                key="filter_consultant"
            )
        
        with col5:
            min_date = pd.to_datetime(df['ed_arrival_dt']).min().date()
            max_date = pd.to_datetime(df['ed_arrival_dt']).max().date()
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="filter_date_range"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered = df.copy()
    
    if selected_fy:
        filtered = filtered[filtered['fiscal_year'].isin(selected_fy)]
    if selected_facilities:
        filtered = filtered[filtered['facility'].isin(selected_facilities)]
    if selected_enc:
        filtered = filtered[filtered['encounter_type'].isin(selected_enc)]
    if selected_consultants:
        filtered = filtered[filtered['consultant_name'].isin(selected_consultants)]
    if len(date_range) == 2:
        filtered['ed_arrival_dt'] = pd.to_datetime(filtered['ed_arrival_dt'])
        filtered = filtered[
            (filtered['ed_arrival_dt'].dt.date >= date_range[0]) &
            (filtered['ed_arrival_dt'].dt.date <= date_range[1])
        ]
    
    # Show record count
    st.caption(f"**{len(filtered):,}** of {len(df):,} records shown")
    
    return filtered


def render_telesitting_filters(pl_df, rl_df):
    """
    Renders a horizontal filter bar for TeleSitting pages.
    Returns filtered patient log df and redirect log df.
    Filters: Fiscal Year, Hospital, Risk Level, Date Range
    """
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 2])
        
        with col1:
            fiscal_years = sorted(pl_df['fiscal_year'].unique().tolist())
            selected_fy = st.multiselect(
                "Fiscal Year",
                options=fiscal_years,
                default=fiscal_years,
                key="tsit_filter_fy"
            )
        
        with col2:
            hospitals = sorted(pl_df['hospital'].unique().tolist())
            selected_hospitals = st.multiselect(
                "Hospital",
                options=hospitals,
                default=hospitals,
                key="tsit_filter_hospital"
            )
        
        with col3:
            risk_levels = ['High', 'Medium', 'Low']
            selected_risk = st.multiselect(
                "Risk Level",
                options=risk_levels,
                default=risk_levels,
                key="tsit_filter_risk"
            )
        
        with col4:
            min_date = pd.to_datetime(pl_df['admit_dt']).min().date()
            max_date = pd.to_datetime(pl_df['admit_dt']).max().date()
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="tsit_filter_date"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_pl = pl_df.copy()
    if selected_fy:
        filtered_pl = filtered_pl[filtered_pl['fiscal_year'].isin(selected_fy)]
    if selected_hospitals:
        filtered_pl = filtered_pl[filtered_pl['hospital'].isin(selected_hospitals)]
    if selected_risk:
        filtered_pl = filtered_pl[filtered_pl['risk_level'].isin(selected_risk)]
    if len(date_range) == 2:
        filtered_pl['admit_dt'] = pd.to_datetime(filtered_pl['admit_dt'])
        filtered_pl = filtered_pl[
            (filtered_pl['admit_dt'].dt.date >= date_range[0]) &
            (filtered_pl['admit_dt'].dt.date <= date_range[1])
        ]
    
    filtered_rl = rl_df[rl_df['fin'].isin(filtered_pl['fin'])]
    
    st.caption(f"**{len(filtered_pl):,}** patients · **{len(filtered_rl):,}** redirect events shown")
    
    return filtered_pl, filtered_rl
```

---

## Step 5 — Rewrite app.py

`app.py` has one job — password gate. After login, Streamlit loads the first page automatically.

```python
# app.py

import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))
from utils.theme import get_global_css

# ── Page config ──
st.set_page_config(
    page_title="PSH Virtual Health Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Inject global CSS and IBM Plex Sans ──
st.markdown(get_global_css(), unsafe_allow_html=True)

# ── Password gate ──
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # Hide sidebar nav on login page
        st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        </style>
        """, unsafe_allow_html=True)

        # Centered login card
        _, center, _ = st.columns([1, 1.2, 1])
        with center:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(
                "<h1 style='color:#1F3864;text-align:center;font-size:1.6rem;"
                "font-weight:700;margin-bottom:4px'>Penn State Health</h1>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<h2 style='color:#1F7A8C;text-align:center;font-size:1.1rem;"
                "font-weight:600;margin-bottom:2px'>Virtual Health Dashboard</h2>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<p style='color:#6B7280;text-align:center;font-size:0.8rem;"
                "margin-bottom:24px'>Clinical Performance · PoC</p>",
                unsafe_allow_html=True
            )
            st.divider()
            password = st.text_input(
                "Access password",
                type="password",
                placeholder="Enter password...",
                label_visibility="collapsed"
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

# ── Build sidebar navigation manually ──
# (Streamlit native nav is hidden via CSS — we build our own)

with st.sidebar:
    # Logo / header
    st.markdown("""
    <div style='padding:16px 8px 8px;border-bottom:1px solid rgba(255,255,255,0.15);
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
    """, unsafe_allow_html=True)

    # ── TeleStroke section ──
    st.markdown("""
    <div style='font-size:0.68rem;font-weight:600;letter-spacing:0.08em;
                color:rgba(255,255,255,0.45);text-transform:uppercase;
                padding:8px 8px 4px;margin-top:4px'>
        🧠 TeleStroke PoC
    </div>
    """, unsafe_allow_html=True)

    # Navigation links for TeleStroke
    # Using st.page_link for proper Streamlit navigation
    st.page_link("pages/01_Phase1_Overview.py",
                 label="Phase 1 Overview", icon="📊")
    st.page_link("pages/02_Clinical_Outcomes.py",
                 label="Clinical Outcomes", icon="🏥")
    st.page_link("pages/03_Operational.py",
                 label="Operational", icon="⚙️")
    st.page_link("pages/04_Financial.py",
                 label="Financial", icon="💰")
    st.page_link("pages/05_Provider_Performance.py",
                 label="Provider Performance", icon="🔒")

    # ── Divider ──
    st.markdown("""
    <div style='border-top:1px solid rgba(255,255,255,0.12);margin:12px 0'></div>
    """, unsafe_allow_html=True)

    # ── TeleSitting section ──
    st.markdown("""
    <div style='font-size:0.68rem;font-weight:600;letter-spacing:0.08em;
                color:rgba(255,255,255,0.45);text-transform:uppercase;
                padding:8px 8px 4px'>
        👁 TeleSitting PoC
    </div>
    <div style='padding:6px 8px 12px'>
        <div style='font-size:0.78rem;color:rgba(255,255,255,0.35);
                    font-style:italic'>Coming Soon</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bottom: logout ──
    st.markdown("""
    <div style='border-top:1px solid rgba(255,255,255,0.12);
                margin-top:auto;padding-top:12px'></div>
    """, unsafe_allow_html=True)

    if st.button("Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    # ── Synthetic data notice ──
    st.markdown("""
    <div style='font-size:0.65rem;color:rgba(255,255,255,0.3);
                text-align:center;padding:8px 0;margin-top:8px'>
        ⚠️ Synthetic data only<br>No real patient data
    </div>
    """, unsafe_allow_html=True)

# ── Welcome redirect ──
# After login, redirect to Phase 1 Overview automatically
st.switch_page("pages/01_Phase1_Overview.py")
```

---

## Step 6 — Update .streamlit/config.toml

```toml
[theme]
primaryColor = "#1F7A8C"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F4F6F9"
textColor = "#1F3864"
font = "sans serif"

[server]
headless = true
```

---

## Step 7 — Update Each Page File

For each of the 5 TeleStroke page files, update the top section only. Do not change any chart or KPI logic.

**Add to the top of every page file:**

```python
import streamlit as st
import pandas as pd
import os
import sys

# Add project root to path
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from utils.theme import get_global_css
from utils.filters import render_telestroke_filters

# Inject global CSS and font
st.markdown(get_global_css(), unsafe_allow_html=True)

# Authentication check
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("app.py")

# Rebuild sidebar on every page
# (copy the exact same sidebar block from app.py)
# This ensures consistent nav on all pages
```

**IMPORTANT:** Copy the full sidebar `with st.sidebar:` block from `app.py` into every page file. This is the only way to keep the sidebar consistent across all pages in Streamlit's multipage architecture.

**Then update the data loading path in each page:**
```python
DATA_DIR = os.path.join(PROJECT_DIR, "data")
df = pd.read_csv(os.path.join(DATA_DIR, "telestroke_synthetic.csv"))
```

**Then replace sidebar filter calls with the new horizontal filter:**
```python
# REMOVE any st.sidebar filter calls
# REPLACE with:
df = render_telestroke_filters(df)
# Place this AFTER the page title, BEFORE any charts
```

---

## Step 8 — Fix generate_data.py Treatment Rate

Update `generate_data.py` so that approximately 20% of thrombolysis-eligible Audio/Video cases have `treatment_administered = No` with a realistic contraindication reason. This will produce a treatment rate of approximately 75-80% instead of 100%.

```python
# In the section where treatment_administered is set for eligible cases:
# Instead of: all eligible cases get treatment_administered = Yes
# Use this logic:

import numpy as np

# For eligible AV cases, 80% treated, 20% not treated (contraindication)
contraindication_reasons = [
    "Uncontrolled Hypertension",
    "Consent Declined",
    "Spontaneous Improvement",
    "Recent Surgery",
    "Active Bleeding",
    "Symptom Onset Unknown"
]

# For each eligible AV row:
# treatment_administered = np.random.choice(['Yes', 'No'], p=[0.80, 0.20])
# If No: contraindication_reason = np.random.choice(contraindication_reasons)
# If Yes: contraindication_reason = None
```

After updating `generate_data.py`, run it to regenerate the CSV:
```bash
cd /Users/chanakaperera/Dev/vhdashboardpoc && .venv/bin/python generate_data.py
```

Confirm the new treatment rate is approximately 75-82% before proceeding.

---

## Step 9 — Verify Full Flow

After all changes:

1. Run: `.venv/bin/python -m streamlit run app.py`

2. Verify in order:
   - Login page shows — no sidebar, centered PSH branding, IBM Plex Sans font
   - Correct password `pocvhchartskpi` → redirects straight to Phase 1 Overview
   - Sidebar shows two sections: TeleStroke PoC (5 links) and TeleSitting PoC (Coming Soon text only)
   - All 5 nav links work and load correct pages
   - Each page shows horizontal filter bar at top with 5 filter dropdowns
   - Filters update charts when changed
   - IBM Plex Sans rendering consistently on login, sidebar, and all pages
   - Sign Out button works and returns to login
   - Treatment Rate showing approximately 75-82% (not 100%)

3. Report back with:
   - Confirmation each step completed
   - Any errors or warnings
   - Description of what each page looks like
   - Confirm ready to push to GitHub

**Do not push to GitHub until confirmed.**

---

## Important Notes

- The sidebar `with st.sidebar:` block MUST be duplicated in every page file — this is required by Streamlit's multipage architecture to maintain consistent navigation
- IBM Plex Sans loads from Google Fonts CDN — requires internet connection to render. Falls back to system sans-serif if offline
- `[data-testid="stSidebarNav"]` hidden via CSS — this hides Streamlit's auto-generated page list so our custom nav shows instead
- The `st.switch_page()` at the bottom of `app.py` fires after login to redirect to Phase 1 Overview
- Filter keys must be unique per page — the `key=` parameter in each filter widget prevents Streamlit state conflicts across pages
- Do not remove or modify any Plotly chart code in the existing page files — only modify imports, sidebar block, data loading paths, and filter calls
