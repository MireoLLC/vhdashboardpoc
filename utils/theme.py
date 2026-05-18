"""PSH brand colors and global CSS injection (IBM Plex Sans + layout rules)."""

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

# Ordered month sequence for fiscal year (July = month 1)
FY_MONTH_ORDER = [
    "July", "August", "September", "October", "November", "December",
    "January", "February", "March", "April", "May", "June",
]


def get_global_css():
    """Return CSS string with IBM Plex Sans + global style overrides.

    Call once per page via st.markdown(get_global_css(), unsafe_allow_html=True).
    """
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

/* ── Hide sidebar collapse button entirely (no need for it in this PoC, and removes the "keyboard_double_arrow_right" Material Icons leak) ── */
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}
button[kind="header"] {
    display: none !important;
}
.st-emotion-cache-1egp75f {
    display: none !important;
}

/* ── Targeted font override — scoped to content surfaces only so Streamlit chrome (icons, kebab menus, etc.) is left alone ── */
.main *,
[data-testid="stMarkdownContainer"] *,
[data-testid="stSidebar"] .stMarkdown *,
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
.stButton > button,
.stSelectbox *,
.stMultiSelect * {
    font-family: 'IBM Plex Sans', sans-serif !important;
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

/* ── Sidebar buttons (Sign Out etc.) ── */
[data-testid="stSidebar"] .stButton > button {
    background-color: rgba(255,255,255,0.12) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    font-size: 0.78rem !important;
    padding: 6px 12px !important;
    border-radius: 6px !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(255,255,255,0.20) !important;
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
