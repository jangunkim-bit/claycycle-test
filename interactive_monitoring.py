import numpy as np
import plotly.graph_objects as go

BLUE = "#2563EB"
RED = "#E24A4A"
GREEN = "#1F7A5C"
NAVY = "#16324F"
GRID = "#E7EDF3"
AXIS = "#344054"


def _style_axes(fig):
    fig.update_xaxes(
        showline=True, linewidth=1.25, linecolor=AXIS, mirror=True,
        ticks="outside", ticklen=6, tickwidth=1.1, tickcolor=AXIS,
        showticklabels=True, tickfont=dict(size=12, color=AXIS),
        showgrid=True, gridcolor=GRID, gridwidth=1, zeroline=False,
        title_font=dict(size=14, color=AXIS),
    )
    fig.update_yaxes(
        showline=True, linewidth=1.25, linecolor=AXIS, mirror=True,
        ticks="outside", ticklen=6, tickwidth=1.1, tickcolor=AXIS,
        showticklabels=True, tickfont=dict(size=12, color=AXIS),
        showgrid=True, gridcolor=GRID, gridwidth=1, zeroline=False,
        title_font=dict(size=14, color=AXIS),
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", hovermode="closest",
        font=dict(family="Arial, sans-serif", size=12, color=AXIS),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
    )
    return fig


def terminal_settlement_selection_figure(fit_results, design_delta_st_mm, selected_index=None):
    """Interactive terminal-settlement evolution graph for a selected monitoring stage."""
    if not fit_results:
        raise ValueError("fit_results must contain at least one monitoring result.")

    n_results = len(fit_results)
    if selected_index is None:
        selected_index = n_results - 1
    selected_index = max(0, min(int(selected_index), n_results - 1))

    fig = go.Figure()
    xvals = [float(r["imax"]) for r in fit_results]
    yvals = [float(r["delta_ST_mm"]) for r in fit_results]
    selected = fit_results[selected_index]
    selected_x = xvals[selected_index]
    selected_delta_st = yvals[selected_index]
    stability_threshold = 1.0
    is_actual_latest = selected_index == n_results - 1

    if selected_index >= 1 and abs(yvals[selected_index - 1]) > 1e-12:
        latest_change_pct = (
            abs(selected_delta_st - yvals[selected_index - 1])
            / abs(yvals[selected_index - 1]) * 100.0
        )
        is_stable = latest_change_pct <= stability_threshold
    else:
        latest_change_pct = None
        is_stable = False

    fig.add_trace(go.Scatter(
        x=xvals, y=yvals, mode="lines",
        name="Monitoring-based prediction",
        line=dict(width=3, color=BLUE, shape="spline"),
        hoverinfo="skip",
    ))

    labels = []
    marker_sizes = []
    marker_colors = []
    marker_symbols = []
    for idx, r in enumerate(fit_results):
        if idx == selected_index:
            suffix = "Latest" if is_actual_latest else "Selected"
            labels.append(f'D{r["dataset"]} ({suffix})')
            marker_sizes.append(15)
            marker_colors.append(GREEN)
            marker_symbols.append("diamond")
        else:
            labels.append(f'D{r["dataset"]}')
            marker_sizes.append(10)
            marker_colors.append(BLUE)
            marker_symbols.append("circle")

    fig.add_trace(go.Scatter(
        x=xvals, y=yvals, mode="markers+text",
        text=labels,
        textposition=["bottom center" if idx == selected_index else "top center" for idx in range(n_results)],
        customdata=list(range(n_results)),
        showlegend=False,
        marker=dict(
            size=marker_sizes,
            color=marker_colors,
            symbol=marker_symbols,
            line=dict(color="white", width=2.1),
        ),
        hovertemplate=(
            "<b>Click to select this monitoring stage</b><br>"
            "i<sub>max</sub> = %{x:,.0f}<br>"
            "ΔS<sub>T</sub> = %{y:.2f} mm<extra></extra>"
        ),
    ))

    fig.add_shape(
        type="line", xref="paper", x0=0, x1=1, yref="y",
        y0=design_delta_st_mm, y1=design_delta_st_mm,
        line=dict(color=RED, width=2, dash="dash"), layer="below",
    )
    fig.add_shape(
        type="line", xref="paper", x0=0, x1=1, yref="y",
        y0=selected_delta_st, y1=selected_delta_st,
        line=dict(color=GREEN, width=2.4, dash="dot"), layer="below",
    )

    fig.add_annotation(
        x=0.985, y=design_delta_st_mm, xref="paper", yref="y",
        text=f"Design-stage Δ<i>S</i><sub>T</sub> = {design_delta_st_mm:.1f} mm",
        showarrow=False, xanchor="right", yanchor="top", yshift=-6,
        bgcolor="rgba(255,255,255,0.86)",
        font=dict(size=12, color=RED),
    )
    selected_label = "Monitoring-updated" if is_actual_latest else "Selected monitoring"
    fig.add_annotation(
        x=0.985, y=selected_delta_st, xref="paper", yref="y",
        text=f"{selected_label} Δ<i>S</i><sub>T</sub> = {selected_delta_st:.1f} mm",
        showarrow=False, xanchor="right", yanchor="bottom", yshift=8,
        bgcolor="rgba(255,255,255,0.90)",
        font=dict(size=12, color=GREEN),
    )

    if is_stable:
        status_text = (
            f"<b>STABLE</b><br>Change from previous stage = "
            f"{latest_change_pct:.2f}% ≤ {stability_threshold:.1f}%"
        )
        status_color = GREEN
        status_bg = "rgba(31,122,92,0.10)"
    else:
        if latest_change_pct is None:
            detail = "Previous monitoring result is unavailable."
        else:
            detail = (
                f"Change from previous stage = {latest_change_pct:.2f}% "
                f"> {stability_threshold:.1f}%"
            )
        status_text = (
            f"<b>INSUFFICIENT</b><br>{detail}<br>"
            "Additional monitoring data are required."
        )
        status_color = RED
        status_bg = "rgba(226,74,74,0.10)"

    fig.add_annotation(
        x=0.98, y=0.97, xref="paper", yref="paper",
        text=status_text, showarrow=False,
        xanchor="right", yanchor="top", align="left",
        bgcolor=status_bg, bordercolor=status_color, borderwidth=1.6, borderpad=9,
        font=dict(size=15, color=status_color),
    )

    if len(xvals) == 1:
        xmin = max(1.0, xvals[0] / 3.0)
        xmax = xvals[0] * 3.0
    else:
        xmin = max(1.0, min(xvals) / 1.5)
        xmax = max(xvals) * 1.5
    min_decade = int(np.floor(np.log10(xmin)))
    max_decade = int(np.ceil(np.log10(xmax)))
    tickvals = [10 ** p for p in range(min_decade, max_decade + 1)]

    all_y = yvals + [float(design_delta_st_mm), selected_delta_st]
    y_min = min(all_y)
    y_max = max(all_y)
    y_span = max(y_max - y_min, 1.0)

    fig.update_xaxes(
        type="log", tickmode="array", tickvals=tickvals,
        ticktext=[f"10<sup>{p}</sup>" if p != 0 else "1" for p in range(min_decade, max_decade + 1)],
        title="Maximum monitored cycle, <i>i</i><sub>max</sub>",
    )
    fig.update_yaxes(
        title="Predicted terminal repetitive settlement, Δ<i>S</i><sub>T</sub> (mm)",
        nticks=7,
        range=[y_min - 0.08 * y_span, y_max + 0.15 * y_span],
    )
    fig.update_layout(
        height=520, margin=dict(l=70, r=35, t=35, b=80),
        showlegend=False,
        clickmode="event+select",
    )
    return _style_axes(fig)
