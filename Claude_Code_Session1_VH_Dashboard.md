# Claude Code Instructions — Session 1
# VH Dashboard Restructure + TeleStroke Enhancement + Password Gate
**Project:** Penn State Health Virtual Health Dashboard PoC  
**Session:** 1 of 2  
**Scope:** Restructure folder, add password gate, redesign TeleStroke landing page, add unified program selector  
**Do not build:** TeleSitting pages or synthetic data — that is Session 2

---

## Pre-Flight Check

Before writing any code, do the following:

1. Confirm working directory is `/Users/chanakaperera/Dev/vhdashboardpoc`
2. List all existing files and folders
3. Confirm the venv exists at `.venv/`
4. Confirm `data/telestroke_synthetic.csv` exists
5. Tell me your plan before touching any files — wait for my confirmation

---

## Step 1 — Restructure Folder

Reorganize the existing pages folder to support two programs. Do not rewrite any page content — only move and rename files.

**Create this new structure:**

```
pages/
├── telestroke/
│   ├── 01_TS_Phase1_Overview.py
│   ├── 02_TS_Clinical_Outcomes.py
│   ├── 03_TS_Operational_Performance.py
│   ├── 04_TS_Financial.py
│   └── 05_TS_Provider_Performance.py
└── telesitting/
    └── .gitkeep
```

**Move and rename existing pages:**
- `pages/01_Phase1_Overview.py` → `pages/telestroke/01_TS_Phase1_Overview.py`
- `pages/02_Clinical_Outcomes.py` → `pages/telestroke/02_TS_Clinical_Outcomes.py`
- `pages/03_Operational_Performance.py` → `pages/telestroke/03_TS_Operational_Performance.py`
- `pages/04_Financial.py` → `pages/telestroke/04_TS_Financial.py`
- `pages/05_Provider_Performance.py` → `pages/telestroke/05_TS_Provider_Performance.py`

Create empty `pages/telesitting/` folder with a `.gitkeep` file so it exists in git.

---

## Step 2 — Add Password Gate

**Create `.streamlit/secrets.toml`:**

```toml
APP_PASSWORD = "pocvhchartskpi"
```

**Important:** Make sure `.streamlit/secrets.toml` is in `.gitignore` — this file must never be pushed to GitHub.

**Update `.gitignore` to include:**

```
.streamlit/secrets.toml
.venv/
__pycache__/
*.pyc
.DS_Store
data/*.csv
```

**Add this password check function to `app.py`** at the very top, before any other content:

```python
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        # Login page styling
        st.markdown("""
        <div style='max-width:400px; margin: 80px auto; text-align:center'>
        """, unsafe_allow_html=True)
        st.markdown("<h1 style='color:#1F3864; font-family:Segoe UI'>Penn State Health</h1>",
                    unsafe_allow_html=True)
        st.markdown("<h3 style='color:#1F7A8C; font-family:Segoe UI'>Virtual Health Dashboard</h3>",
                    unsafe_allow_html=True)
        st.markdown("<p style='color:#888; font-style:italic'>Art of the Possible — PoC</p>",
                    unsafe_allow_html=True)
        st.markdown("---")
        password = st.text_input("Enter access password", type="password",
                                  placeholder="Enter password...")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("Login", type="primary", use_container_width=True):
                if password == st.secrets["APP_PASSWORD"]:
                    st.session_state.authenticated = True
                    st.session_state.program = None
                    st.rerun()
                else:
                    st.error("Incorrect password. Please try again.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()
```

Call `check_password()` as the very first line of the main app body.

---

## Step 3 — Build Unified Program Selector Landing Page

Replace the existing `app.py` landing page content with a two-level landing page.

### Level 1 — Program Selector

Shown when `st.session_state.program` is None or not set.

```python
# Initialize program state
if "program" not in st.session_state:
    st.session_state.program = None
```

**Layout:**

- Page config: title="PSH Virtual Health Dashboard", icon="🏥", layout="wide"
- Inject CSS for card styling (see styling section below)
- Header section:
  - Large title: "Penn State Health Virtual Health Dashboard" in navy
  - Subtitle: "Virtual Care Program — Art of the Possible PoC" in teal italic
  - Small gray text: "Select a program to begin"
  - Horizontal divider

- Two program cards side by side using `st.columns(2)` with gap:

**LEFT CARD — TeleStroke:**
```
🧠 TeleStroke Dashboard
─────────────────────────────
Acute stroke response performance,
clinical outcomes, and financial
metrics across 6 spoke sites.

📊 500 records  |  FY2023–FY2026  |  5 pages
[Phase 1] [Phase 2]

[  Enter Dashboard →  ]
```
- Card border: 2px solid #1F7A8C
- Card background: #EBF5FB
- Button: primary teal style
- On click: `st.session_state.program = "telestroke"` then `st.rerun()`

**RIGHT CARD — TeleSitting:**
```
👁 TeleSitting Dashboard
─────────────────────────────
Remote patient monitoring,
safety outcomes, and cost
avoidance metrics. (Coming Soon)

🚧 Under Development

[  Coming Soon  ]  ← disabled/grayed button
```
- Card border: 2px solid #B0BEC5
- Card background: #F5F5F5
- Button: disabled, gray
- Do not navigate anywhere when clicked
- Add "🚧 Coming Soon" badge in amber

- Footer below cards:
  - Small italic gray text: "All data shown is synthetic — no real patient data is present"

### Level 2 — TeleStroke Program Landing

Shown when `st.session_state.program == "telestroke"`.

**Layout:**

**Back button at very top:**
```python
if st.button("← All Programs"):
    st.session_state.program = None
    st.rerun()
```

**Program header:**
- "🧠 TeleStroke Dashboard" in large navy (h1)
- "Penn State Health · Art of the Possible PoC" in teal italic
- Synthetic data warning badge: small amber box "⚠️ Synthetic Data Only — No Real Patient Data"
- Horizontal divider

**KPI Summary Row (4 columns):**

Calculate these from the loaded dataframe:

1. **Total Consults**
   - Value: count of all records
   - Label: "Total Consults"
   - Border color: teal (#1F7A8C)
   - No benchmark

2. **D2N Compliance**
   - Value: % of eligible AV cases with door_to_needle_time_minutes ≤ 60
   - Label: "D2N Compliance (≤60 min)"
   - Benchmark text: "Target: ≥85% · AHA/ASA"
   - Color: green if ≥85%, amber if 70–84%, red if <70%

3. **Median Response Time**
   - Value: median of provider response minutes (provider_response_dt minus call_to_provider_dt)
   - Label: "Median Response Time"
   - Benchmark text: "Target: ≤15 min"
   - Color: green if ≤15 min, amber if 15–20 min, red if >20 min

4. **Treatment Rate**
   - Value: % of eligible cases where treatment was administered
   - Label: "Treatment Rate (Eligible Cases)"
   - Border color: teal
   - No benchmark

Style each KPI card as:
```css
background: white;
border-radius: 8px;
border-left: 5px solid [color];
padding: 16px;
box-shadow: 0 1px 4px rgba(0,0,0,0.08);
```

**Quick Stats Row (3 columns):**

Left column — Consult Type Donut Chart:
- Small Plotly pie/donut chart
- Values: Audio/Video, Phone, Reg-No Consult counts
- Colors: teal, navy, light blue
- Title: "Consult Mix"
- Height: 200px

Middle column — Consult Volume by Fiscal Year:
- Small Plotly bar chart
- X: fiscal year, Y: count
- Color: teal
- Title: "Volume by Fiscal Year"
- Height: 200px

Right column — Top Facility Stat:
- Calculate which facility has highest D2N compliance among eligible cases
- Display as:
  ```
  🏆 Top Performing Site
  [Facility Name]
  [XX.X%] D2N Compliance
  ```
- Style with teal border card

**Navigation Cards Grid:**

Display 5 navigation cards in a 3+2 layout (row 1: 3 cards, row 2: 2 cards centered).

Each card contains:
- Icon + Title (bold navy)
- One line description (gray)
- Phase badge (teal for Phase 1, navy for Phase 2)
- "→" arrow right aligned

Card styles:
```css
background: white;
border-radius: 8px;
border-left: 5px solid #1F7A8C;
padding: 16px 20px;
margin-bottom: 12px;
box-shadow: 0 1px 4px rgba(0,0,0,0.06);
```

Cards:
1. **📊 Phase 1 Overview** — "Door-to-needle, neurologist response, cart uptime, alert volume" — [Phase 1 — teal badge]
2. **🏥 Clinical Outcomes** — "Treatment rates, LVO detection, mRS scores, 30-day readmissions" — [Phase 2 — navy badge]
3. **⚙️ Operational Performance** — "Consult mix, site distribution, time-of-day patterns, D2N detail" — [Phase 2 — navy badge]
4. **💰 Financial Summary** — "Cost of delivery, downstream revenue, payer mix" — [Phase 2 — navy badge]
5. **👨‍⚕️ Provider Performance** — "Per-consultant scorecards and benchmarking — 🔒 Restricted Access" — [Phase 2 — navy badge]

Cards are informational only — actual navigation happens via the Streamlit sidebar.
Add note below cards: "*Use the sidebar to navigate to each section*"

**Footer:**
```
Synthetic data only  ·  500 records  ·  FY2023–2026  ·  For demonstration purposes only
```
Small, gray, italic, centered.

---

## Step 4 — Update Sidebar

Update the sidebar in `app.py` to be program-aware:

**When no program selected:**
```
🏥 PSH Virtual Health Dashboard
Art of the Possible — PoC
─────────────────────────
← Select a program to begin
```

**When TeleStroke selected:**
```
🧠 TeleStroke Dashboard
─────────────────────────
Navigate to:
• Phase 1 Overview
• Clinical Outcomes
• Operational Performance
• Financial Summary
• Provider Performance
─────────────────────────
[← All Programs]
```

Sidebar background: navy (#1F3864), white text — apply via injected CSS.

---

## Step 5 — Update Page Files

At the top of each existing TeleStroke page file (after moving to pages/telestroke/), add:

```python
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Program context check
if "program" not in st.session_state or st.session_state.program != "telestroke":
    st.session_state.program = "telestroke"

# Back button
if st.button("← TeleStroke Home"):
    st.session_state.program = "telestroke"
    st.switch_page("app.py")
```

Also update data loading paths in each page file — since files moved to a subdirectory, update any relative paths to CSV files:
- Change `"data/telestroke_synthetic.csv"` to `os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'telestroke_synthetic.csv')`
- Apply same fix to cart_uptime and monthly_cost CSV paths

---

## Step 6 — CSS Styling

Add this global CSS injection to `app.py` (call it once after check_password()):

```python
def inject_css():
    st.markdown("""
    <style>
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1F3864 !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        [data-testid="stSidebar"] .stSelectbox label {
            color: white !important;
        }

        /* Main background */
        .main .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }

        /* KPI cards */
        .kpi-card {
            background: white;
            border-radius: 8px;
            padding: 16px 20px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            height: 100%;
        }

        /* Program cards */
        .program-card {
            border-radius: 12px;
            padding: 28px;
            margin: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        }

        /* Nav cards */
        .nav-card {
            background: white;
            border-radius: 8px;
            border-left: 5px solid #1F7A8C;
            padding: 16px 20px;
            margin-bottom: 10px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }

        /* Phase badges */
        .badge-phase1 {
            background: #1F7A8C;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }
        .badge-phase2 {
            background: #1F3864;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }
        .badge-coming-soon {
            background: #F59E0B;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }

        /* Headings */
        h1 { color: #1F3864 !important; font-family: 'Segoe UI', Arial, sans-serif !important; }
        h2 { color: #1F7A8C !important; font-family: 'Segoe UI', Arial, sans-serif !important; }
        h3 { color: #1F3864 !important; font-family: 'Segoe UI', Arial, sans-serif !important; }
    </style>
    """, unsafe_allow_html=True)
```

Call `inject_css()` immediately after `check_password()`.

---

## Step 7 — Verify Locally

After completing all steps:

1. Activate venv: `source .venv/bin/activate`
2. Run: `streamlit run app.py`
3. Verify the following in order:
   - Login page appears with PSH branding and password field
   - Password `pocvhchartskpi` grants access
   - Wrong password shows error
   - Program selector shows TeleStroke (active) and TeleSitting (Coming Soon) cards
   - TeleStroke card navigates to TeleStroke landing page
   - TeleStroke landing page shows KPI cards, quick stats, and navigation cards
   - Back button returns to program selector
   - Sidebar updates correctly based on program selection
   - All 5 TeleStroke pages still load without errors
   - No broken import paths

4. Report back with:
   - List of all files modified
   - Screenshot description of what each level looks like
   - Any errors or warnings encountered

**Do not push to GitHub until I confirm locally.**

---

## Important Notes

- Do not rewrite existing TeleStroke page content — only move, rename, and fix import paths
- Do not build TeleSitting pages or synthetic data — that is Session 2
- The TeleSitting card must be visually present but disabled/grayed
- secrets.toml must never be committed to git
- All CSV loading paths must be updated to work from the new subdirectory location
- Use `@st.cache_data` on all data loading functions
