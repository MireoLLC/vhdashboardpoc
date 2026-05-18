"""Reusable Plotly chart helpers with Penn State Health theming."""

import plotly.express as px
import plotly.graph_objects as go

from utils.theme import (
    BENCHMARK_COLOR,
    CHART_BG,
    FONT_FAMILY,
    GRID_COLOR,
    PSH_BLUE,
    PSH_LTBLUE,
    PSH_NAVY,
    PSH_TEAL,
)


def _apply_layout(fig, title=None, x_title=None, y_title=None, height=380):
    fig.update_layout(
        title=dict(text=title, font=dict(family=FONT_FAMILY, size=15, color=PSH_NAVY)) if title else None,
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        font=dict(family=FONT_FAMILY, color="#1F2937", size=12),
        margin=dict(l=40, r=20, t=50 if title else 20, b=40),
        height=height,
        xaxis=dict(title=x_title, gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        yaxis=dict(title=y_title, gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0),
    )
    return fig


def _add_benchmark_line(fig, benchmark, label="Benchmark", horizontal=True):
    if benchmark is None:
        return fig
    if horizontal:
        fig.add_hline(
            y=benchmark,
            line_dash="dash",
            line_color=BENCHMARK_COLOR,
            annotation_text=f"{label}: {benchmark}",
            annotation_position="top right",
            annotation_font_color=BENCHMARK_COLOR,
        )
    else:
        fig.add_vline(
            x=benchmark,
            line_dash="dash",
            line_color=BENCHMARK_COLOR,
            annotation_text=f"{label}: {benchmark}",
            annotation_position="top right",
            annotation_font_color=BENCHMARK_COLOR,
        )
    return fig


def kpi_card(value, label, benchmark=None, delta=None, color=PSH_TEAL):
    """Return a dict suitable for unpacking into st.metric, plus helper text."""
    helper = f"Benchmark: {benchmark}" if benchmark is not None else ""
    return {
        "label": label,
        "value": value,
        "delta": delta,
        "help": helper,
        "color": color,
    }


def trend_line(df, x_col, y_col, title, benchmark=None, color=PSH_TEAL, y_title=None, x_title=None, category_orders=None):
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        markers=True,
        category_orders=category_orders,
    )
    fig.update_traces(line=dict(color=color, width=3), marker=dict(size=7, color=color))
    fig = _apply_layout(fig, title=title, x_title=x_title or x_col, y_title=y_title or y_col)
    fig = _add_benchmark_line(fig, benchmark)
    return fig


def bar_chart(df, x_col, y_col, title, color=PSH_TEAL, orientation="v", color_col=None, benchmark=None, category_orders=None, y_title=None, x_title=None):
    if color_col:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            orientation=orientation,
            color_discrete_sequence=[PSH_NAVY, PSH_TEAL, PSH_BLUE, PSH_LTBLUE],
            category_orders=category_orders,
        )
    else:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            orientation=orientation,
            category_orders=category_orders,
        )
        fig.update_traces(marker_color=color)
    fig = _apply_layout(fig, title=title, x_title=x_title or x_col, y_title=y_title or y_col)
    fig = _add_benchmark_line(fig, benchmark, horizontal=(orientation == "v"))
    return fig


def stacked_bar(df, x_col, y_cols, title, colors=None, category_orders=None, percent=False, x_title=None, y_title=None):
    fig = go.Figure()
    palette = colors or [PSH_NAVY, PSH_TEAL, PSH_BLUE, PSH_LTBLUE]
    for i, col in enumerate(y_cols):
        fig.add_trace(
            go.Bar(
                x=df[x_col],
                y=df[col],
                name=col,
                marker_color=palette[i % len(palette)],
            )
        )
    barmode = "stack"
    fig.update_layout(barmode=barmode)
    fig = _apply_layout(fig, title=title, x_title=x_title or x_col, y_title=y_title or ("Share" if percent else "Count"))
    if percent:
        fig.update_yaxes(tickformat=".0%")
    if category_orders and x_col in category_orders:
        fig.update_xaxes(categoryorder="array", categoryarray=category_orders[x_col])
    return fig


def histogram(df, col, title, bins=20, benchmark=None, color=PSH_TEAL, x_title=None, y_title="Count"):
    fig = px.histogram(df, x=col, nbins=bins)
    fig.update_traces(marker_color=color, marker_line_color=PSH_NAVY, marker_line_width=0.5)
    fig = _apply_layout(fig, title=title, x_title=x_title or col, y_title=y_title)
    fig = _add_benchmark_line(fig, benchmark, horizontal=False)
    return fig


def pie_chart(df, values_col, names_col, title, colors=None):
    palette = colors or [PSH_NAVY, PSH_TEAL, PSH_BLUE, PSH_LTBLUE, "#F59E0B", "#10B981"]
    fig = px.pie(df, values=values_col, names=names_col, color_discrete_sequence=palette, hole=0.4)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig = _apply_layout(fig, title=title)
    fig.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, x=1.05))
    return fig


def heatmap(df, x_col, y_col, value_col, title, x_title=None, y_title=None):
    pivot = df.pivot_table(index=y_col, columns=x_col, values=value_col, aggfunc="sum", fill_value=0)
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=list(pivot.index),
            colorscale=[[0, "#D6E4F0"], [0.5, "#378ADD"], [1, "#1F3864"]],
            colorbar=dict(title=value_col),
            hovertemplate=f"{x_col}: %{{x}}<br>{y_col}: %{{y}}<br>{value_col}: %{{z}}<extra></extra>",
        )
    )
    fig = _apply_layout(fig, title=title, x_title=x_title or x_col, y_title=y_title or y_col, height=420)
    return fig


def grouped_bar(df, x_col, y_cols, title, colors=None, category_orders=None, x_title=None, y_title=None):
    fig = go.Figure()
    palette = colors or [PSH_NAVY, PSH_TEAL, PSH_BLUE, PSH_LTBLUE]
    for i, col in enumerate(y_cols):
        fig.add_trace(
            go.Bar(
                x=df[x_col],
                y=df[col],
                name=col,
                marker_color=palette[i % len(palette)],
            )
        )
    fig.update_layout(barmode="group")
    fig = _apply_layout(fig, title=title, x_title=x_title or x_col, y_title=y_title or "Count")
    if category_orders and x_col in category_orders:
        fig.update_xaxes(categoryorder="array", categoryarray=category_orders[x_col])
    return fig


def overlay_lines(df, x_col, y_cols, title, colors=None, category_orders=None, x_title=None, y_title=None):
    fig = go.Figure()
    palette = colors or [PSH_NAVY, PSH_TEAL, PSH_BLUE, "#F59E0B"]
    for i, col in enumerate(y_cols):
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[col],
                mode="lines+markers",
                name=col,
                line=dict(color=palette[i % len(palette)], width=3),
                marker=dict(size=7),
            )
        )
    fig = _apply_layout(fig, title=title, x_title=x_title or x_col, y_title=y_title or "Value")
    if category_orders and x_col in category_orders:
        fig.update_xaxes(categoryorder="array", categoryarray=category_orders[x_col])
    return fig
