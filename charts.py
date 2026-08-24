import numpy as np
import plotly.graph_objects as go
from calc_core import modified_accumulation, monitoring_accumulation

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


def static_response_figure(sigma_v0, delta_sigma, e0, eb, e_static, cc):
    """Static e-log sigma'v response referenced to e0 at 1 kPa."""
    sigma_ref = 1.0
    peak_stress = max(float(sigma_v0 + delta_sigma), sigma_ref * 1.01)
    sig = np.logspace(np.log10(sigma_ref), np.log10(peak_stress), 260)
    e_sig = e0 - cc * np.log10(sig / sigma_ref)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sig, y=e_sig, mode="lines", name="Static compression line",
        line=dict(width=3.7, color=BLUE),
        hovertemplate="σ′v = %{x:.1f} kPa<br>e = %{y:.4f}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=[sigma_ref], y=[e0], mode="markers", name="Initial state",
        marker=dict(size=12, color="#64748B", line=dict(color="white", width=2)),
        hovertemplate=f"<b>e<sub>0</sub> = {e0:.4f}</b><br>σ′v = 1.0 kPa<extra>Initial state</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[sigma_v0], y=[eb], mode="markers+text", name="Baseline state",
        marker=dict(size=13, color=BLUE, line=dict(color="white", width=2)),
        text=[f"e<sub>b</sub> = {eb:.4f}"], textposition="top left",
        textfont=dict(size=13, color=NAVY),
        hovertemplate=f"<b>e<sub>b</sub> = {eb:.4f}</b><br>σ′v0 = {sigma_v0:.1f} kPa<extra>Baseline state</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[peak_stress], y=[e_static], mode="markers+text", name="Peak static state",
        marker=dict(size=13, color=NAVY, line=dict(color="white", width=2)),
        text=[f"e<sub>static</sub> = {e_static:.4f}"], textposition="bottom left",
        textfont=dict(size=13, color=NAVY),
        hovertemplate=(
            f"<b>e<sub>static</sub> = {e_static:.4f}</b><br>"
            f"σ′v0 + Δσ = {peak_stress:.1f} kPa<extra>Peak static state</extra>"
        ),
    ))

    # Explicit logarithmic ticks prevent Plotly auto-tick expansion and keep
    # the baseline marker at the actual sigma'_v0 location.
    candidate_ticks = []
    max_decade = int(np.ceil(np.log10(peak_stress * 1.15)))
    for power in range(0, max_decade + 1):
        for mult in (1, 2, 5):
            value = mult * (10 ** power)
            if sigma_ref <= value <= peak_stress * 1.15:
                candidate_ticks.append(value)
    if sigma_v0 not in candidate_ticks:
        candidate_ticks.append(float(sigma_v0))
    if peak_stress not in candidate_ticks:
        candidate_ticks.append(float(peak_stress))
    tickvals = sorted(set(candidate_ticks))

    e_span = max(e0 - e_static, 0.05)
    fig.update_xaxes(
        type="log",
        range=[np.log10(0.85), np.log10(peak_stress * 1.18)],
        tickmode="array", tickvals=tickvals,
        ticktext=[f"{v:g}" for v in tickvals],
        title="Vertical effective stress, <i>σ</i>′<sub>v</sub> (kPa)",
    )
    fig.update_yaxes(
        title="Void ratio, <i>e</i>", nticks=7,
        range=[e_static - 0.12 * e_span, e0 + 0.12 * e_span],
    )
    fig.update_layout(
        height=470, margin=dict(l=60, r=35, t=25, b=70),
        legend=dict(orientation="h", y=-0.25, x=0),
    )
    return _style_axes(fig)


def design_void_ratio_figure(e_static, e_t, n_star, m, i_design):
    i_plot_max = max(float(i_design), 1e6)
    i_grid = np.logspace(0, np.log10(i_plot_max), 420)
    e_curve = modified_accumulation(i_grid, e_static, e_t, n_star, m)
    e_nstar = float(modified_accumulation(np.array([n_star]), e_static, e_t, n_star, m)[0])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=i_grid, y=np.full_like(i_grid, e_t), mode="lines",
        name="Terminal void ratio, eT",
        line=dict(width=1.9, color=RED, dash="dash"),
        hovertemplate=f"<b>e<sub>T</sub> = {e_t:.4f}</b><extra>Terminal state</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=i_grid, y=e_curve, mode="lines", name="Design-stage prediction",
        line=dict(width=3.8, color=RED),
        fill="tonexty", fillcolor="rgba(226,74,74,0.10)",
        hovertemplate="i = %{x:,.0f}<br>e = %{y:.4f}<extra>Design prediction</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[n_star], y=[e_nstar], mode="markers", name="50% accumulation",
        marker=dict(size=12, color=RED, symbol="diamond", line=dict(color="white", width=2)),
        hovertemplate=f"<b>N* = {n_star:,.0f} cycles</b><br>e = {e_nstar:.4f}<extra>50% of ΔeT</extra>",
    ))

    fig.add_vline(x=n_star, line_dash="dot", line_color=NAVY, line_width=1.8)
    fig.add_annotation(
        x=n_star, y=e_nstar,
        text=f"<b><i>N</i>* = {n_star:,.0f} cycles</b><br>50% of Δ<i>e</i><sub>T</sub>",
        showarrow=True, arrowhead=2, ax=55, ay=-55,
        bgcolor="rgba(255,255,255,0.96)", bordercolor=NAVY, borderwidth=1.2,
        font=dict(size=14, color=NAVY),
    )
    fig.add_annotation(
        x=i_plot_max / 1.7, y=e_t,
        text=f"<b><i>e</i><sub>T</sub> = {e_t:.4f}</b>",
        showarrow=False, yshift=18,
        bgcolor="rgba(255,255,255,0.96)", bordercolor=RED, borderwidth=1.2,
        font=dict(size=15, color=RED),
    )

    max_decade = int(np.ceil(np.log10(i_plot_max)))
    tickvals = [10 ** p for p in range(0, max_decade + 1)]
    fig.update_xaxes(
        type="log", tickmode="array", tickvals=tickvals,
        ticktext=[f"10<sup>{p}</sup>" if p > 0 else "1" for p in range(0, max_decade + 1)],
        title="Number of repetitive loading cycles, <i>i</i>",
    )
    fig.update_yaxes(title="Void ratio, <i>e</i>", nticks=7)
    fig.update_layout(
        height=470, margin=dict(l=60, r=30, t=25, b=70),
        legend=dict(orientation="h", y=-0.25, x=0),
        hoverdistance=30,
    )
    return _style_axes(fig)


def calibration_figure(fit_results, e_static, e_t_design, n_design, m_design, i_design, show_all_points):
    max_i_mon = max(x["imax"] for x in fit_results)
    i_plot_max = max(float(i_design), max_i_mon, 1e6)
    i_curve = np.logspace(0, np.log10(i_plot_max), 420)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=i_curve, y=modified_accumulation(i_curve, e_static, e_t_design, n_design, m_design),
        mode="lines", name="Design-stage prediction", line=dict(width=3.5, dash="dash", color=RED),
    ))

    latest = fit_results[-1]
    for r in fit_results:
        fig.add_trace(go.Scatter(
            x=i_curve,
            y=monitoring_accumulation(i_curve, r["e1"], r["eT"], r["Nstar"], r["m"]),
            mode="lines", name=f'Monitoring {r["dataset"]}', line=dict(width=2.2),
            hovertemplate=(
                f'<b>Monitoring {r["dataset"]}</b><br>'
                f'e<sub>1</sub> = {r["e1"]:.4f}<br>'
                'i = %{x:,.0f}<br>e = %{y:.4f}<extra></extra>'
            ),
        ))
        if show_all_points or r is latest:
            d = r["df"]
            fig.add_trace(go.Scatter(
                x=d["i"], y=d["e"], mode="markers", name=f'Measured {r["dataset"]}',
                marker=dict(size=5, opacity=0.45), showlegend=show_all_points or r is latest,
            ))

    max_decade = int(np.ceil(np.log10(i_plot_max)))
    tickvals = [10 ** p for p in range(0, max_decade + 1)]
    fig.update_xaxes(
        type="log", tickmode="array", tickvals=tickvals,
        ticktext=[f"10<sup>{p}</sup>" if p > 0 else "1" for p in range(0, max_decade + 1)],
        title="Number of repetitive loading cycles, <i>i</i>",
    )
    fig.update_yaxes(title="Void ratio, <i>e</i>", nticks=7)
    fig.update_layout(
        height=500, margin=dict(l=60, r=30, t=25, b=80),
        legend=dict(orientation="h", y=-0.3, x=0),
    )
    return _style_axes(fig)


def terminal_settlement_evolution_figure(fit_results, design_delta_st_mm):
    fig = go.Figure()
    xvals = [r["imax"] for r in fit_results]
    yvals = [r["delta_ST_mm"] for r in fit_results]
    latest_delta_st = float(yvals[-1])
    stability_threshold = 1.0

    if len(yvals) >= 2 and abs(float(yvals[-2])) > 1e-12:
        latest_change_pct = abs(latest_delta_st - float(yvals[-2])) / abs(float(yvals[-2])) * 100.0
        is_stable = latest_change_pct <= stability_threshold
    else:
        latest_change_pct = None
        is_stable = False

    point_labels = [f'D{r["dataset"]}' for r in fit_results]
    point_labels[-1] = f'D{fit_results[-1]["dataset"]} (Latest)'
    marker_sizes = [10] * len(xvals)
    marker_sizes[-1] = 14
    marker_colors = [BLUE] * len(xvals)
    marker_colors[-1] = GREEN

    fig.add_trace(go.Scatter(
        x=xvals, y=yvals, mode="lines+markers+text",
        text=point_labels, textposition="top center",
        name="Monitoring-based prediction", line=dict(width=3, color=BLUE, shape="spline"),
        marker=dict(size=marker_sizes, color=marker_colors, line=dict(color="white", width=2)),
        hovertemplate="i<sub>max</sub> = %{x:,.0f}<br>ΔS<sub>T</sub> = %{y:.2f} mm<extra></extra>",
    ))

    fig.add_hline(
        y=design_delta_st_mm, line_dash="dash", line_color=RED, line_width=2,
        annotation_text=f"Design-stage Δ<i>S</i><sub>T</sub> = {design_delta_st_mm:.1f} mm",
        annotation_position="bottom right",
    )
    fig.add_hline(
        y=latest_delta_st, line_dash="dot", line_color=GREEN, line_width=2.3,
        annotation_text=f"Monitoring-updated Δ<i>S</i><sub>T</sub> = {latest_delta_st:.1f} mm",
        annotation_position="bottom right",
    )

    if is_stable:
        status_text = (
            f"<b>STABLE</b><br>Latest change = {latest_change_pct:.2f}% ≤ {stability_threshold:.1f}%"
        )
        status_color = GREEN
        status_bg = "rgba(31,122,92,0.10)"
    else:
        if latest_change_pct is None:
            detail = "At least two monitoring results are required."
        else:
            detail = f"Latest change = {latest_change_pct:.2f}% > {stability_threshold:.1f}%"
        status_text = (
            f"<b>INSUFFICIENT</b><br>{detail}<br>Additional monitoring data are required."
        )
        status_color = RED
        status_bg = "rgba(226,74,74,0.10)"

    # Keep the status box in the upper-right empty portion of the chart so it
    # does not overlap the early monitoring points or their labels.
    fig.add_annotation(
        x=0.97, y=0.97, xref="paper", yref="paper",
        text=status_text, showarrow=False,
        xanchor="right", yanchor="top", align="left",
        bgcolor=status_bg, bordercolor=status_color, borderwidth=1.5, borderpad=8,
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

    fig.update_xaxes(
        type="log", tickmode="array", tickvals=tickvals,
        ticktext=[f"10<sup>{p}</sup>" if p != 0 else "1" for p in range(min_decade, max_decade + 1)],
        title="Maximum monitored cycle, <i>i</i><sub>max</sub>",
    )
    fig.update_yaxes(title="Predicted terminal repetitive settlement, Δ<i>S</i><sub>T</sub> (mm)", nticks=7)
    fig.update_layout(
        height=500, margin=dict(l=70, r=30, t=25, b=80),
        legend=dict(orientation="h", y=-0.3, x=0),
    )
    return _style_axes(fig)
