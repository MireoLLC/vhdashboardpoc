"""Penn State Health brand theme constants for the Telestroke PoC."""

# Penn State Health Brand Colors
PSH_NAVY = "#1F3864"
PSH_TEAL = "#1F7A8C"
PSH_BLUE = "#378ADD"
PSH_LTBLUE = "#D6E4F0"
PSH_WHITE = "#FFFFFF"
PSH_GRAY = "#F2F2F2"
PSH_AMBER = "#F59E0B"
PSH_GREEN = "#10B981"
PSH_RED = "#EF4444"

# Benchmark colors
BENCHMARK_COLOR = "#EF4444"
COMPLIANCE_PASS = "#10B981"
COMPLIANCE_FAIL = "#EF4444"

# Chart defaults
FONT_FAMILY = "Segoe UI, Arial, sans-serif"
CHART_BG = "#FFFFFF"
GRID_COLOR = "#E5E7EB"

# Ordered month sequence for fiscal-year (July = 1)
FY_MONTH_ORDER = [
    "July", "August", "September", "October", "November", "December",
    "January", "February", "March", "April", "May", "June",
]

# Page-wide CSS injected at the top of every page
PAGE_CSS = """
<style>
    [data-testid="stSidebar"] {
        background-color: #1F3864;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="metric-container"] {
        background-color: #F2F2F2;
        border: 1px solid #D6E4F0;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #1F7A8C;
    }
    h1 { color: #1F3864; font-family: 'Segoe UI', Arial, sans-serif; }
    h2 { color: #1F7A8C; font-family: 'Segoe UI', Arial, sans-serif; }
    h3 { color: #1F3864; font-family: 'Segoe UI', Arial, sans-serif; }
    .benchmark { font-size: 11px; color: #6B7280; }
    .phase2-badge {
        display: inline-block;
        background-color: #1F7A8C;
        color: white !important;
        font-size: 10px;
        padding: 2px 8px;
        border-radius: 10px;
        margin-left: 6px;
        vertical-align: middle;
        font-weight: 600;
    }
    .poc-note {
        font-size: 11px;
        color: #6B7280;
        font-style: italic;
        margin-top: -8px;
        margin-bottom: 8px;
    }
</style>
"""
