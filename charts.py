import numpy as np
import plotly.graph_objects as go
from calc_core import modified_accumulation

BLUE = "#2563EB"
RED = "#E24A4A"
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


def static_response_figure(sigma_v0, delta_sigma, e0, eb, e_static, cc, sigma_ref=1.0):
    sig_min = max(1.0, sigma_ref)
    sig_max = max(sigma_v0 + delta_sigma, sigma_v0) * 1.35
    sig = np.logspace(np.log10(sig_min), np.log10(sig_max), 220)
    e_sig = e0 - cc * np.log10(sig / sigma_ref)

    fig = go.Figure()
    # Soft blue fill below the compression line for a cleaner engineering-dashboard look.
    fig.add_trace(go.Scatter(
        x=sig, y=e_sig, mode="lines", name="Static compression line",
        line=dict(width=3.5, color=BLUE, shape="spline"),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.055)",
        hovertemplate="σ′v = %{x:.1f} kPa<br>e = %{y:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[sigma_v0], y=[eb], mode="markers", name="Baseline state",
        marker=dict(size=12, color=BLUE, line=dict(color="white", width=2)),
        hovertemplate="e<sub>b</sub> = %{y:.4f}<extra>Baseline</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[sigma_v0 + delta_sigma], y=[e_static], mode="markers", name="Peak static state",
        marker=dict(size=12, color=NAVY, line=dict(color="white", width=2)),
        hovertemplate="e<sub>static</sub> = %{y:.4f}<extra>Peak static</extra>",
    ))
    fig.add_annotation(
        x=sigma_v0, y=eb, text=f"<b><i>e</i><sub>b</sub> = {eb:.4f}</b>",
        showarrow=True, arrowhead=2, ax=-45, ay=-42,
        bgcolor="rgba(255,255,255,0.94)", bordercolor=BLUE, borderwidth=1,
        font=dict(size=13, color=NAVY),
    )
    fig.add_annotation(
        x=sigma_v0 + delta_sigma, y=e_static,
        text=f"<b><i>e</i><sub>static</sub> = {e_static:.4f}</b>",
        showarrow=True, arrowhead=2, ax=45, ay=42,
        bgcolor="rgba(255,255,255,0.94)", bordercolor=NAVY, borderwidth=1,
        font=dict(size=13, color=NAVY),
    )

    decade_min = int(np.floor(np.log10(sig_min)))
    decade_max = int(np.ceil(np.log10(sig_max)))
    tickvals = []
    for d in range(decade_min, decade_max + 1):
        for mult in [1, 2, 5]:
            v = mult * (10 ** d)
            if sig_min <= v <= sig_max:
                tickvals.append(v)

    fig.update_xaxes(
        type="log", tickmode="array", tickvals=tickvals,
        ticktext=[f"{v:g}" for v in tickvals],
        title="Vertical effective stress, <i>σ</i>′<sub>v</sub> (kPa)",
    )
    fig.update_yaxes(title="Void ratio, <i>e</i>", nticks=7)
    fig.update_layout(
        height=470, margin=dict(l=60, r=30, t=25, b=70),
        legend=dict(orientation="h", y=-0.25, x=0),
    )
    return _style_axes(fig)


def design_void_ratio_figure(e_static, e_t, n_star, m, i_design):
    i_plot_max = max(float(i_design), 1e6)
    i_grid = np.logspace(0, np.log10(i_plot_max), 420)
    e_curve = modified_accumulation(i_grid, e_static, e_t, n_star, m)
    e_nstar = float(modified_accumulation(np.array([n_star]), e_static, e_t, n_star, m)[0])

    fig = go.Figure()
    # Terminal-state baseline, then filled prediction curve.
    fig.add_trace(go.Scatter(
        x=i_grid, y=np.full_like(i_grid, e_t), mode="lines",
        line=dict(width=0), hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=i_grid, y=e_curve, mode="lines", name="Design-stage prediction",
        line=dict(width=3.8, color=RED, shape="spline"),
        fill="tonexty", fillcolor="rgba(226,74,74,0.10)",
        hovertemplate="i = %{x:,.0f}<br>e = %{y:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[n_star], y=[e_nstar], mode="markers", name="50% accumulation",
        marker=dict(size=12, color=RED, symbol="diamond", line=dict(color="white", width=2)),
        hovertemplate="N* = %{x:,.0f} cycles<br>e = %{y:.4f}<extra></extra>",
    ))

    fig.add_hline(y=e_t, line_dash="dash", line_color=RED, line_width=1.8)
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
            x=i_curve, y=modified_accumulation(i_curve, e_static, r["eT"], r["Nstar"], r["m"]),
            mode="lines", name=f'Monitoring {r["dataset"]}', line=dict(width=2.2),
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
    fig.add_trace(go.Scatter(
        x=xvals, y=yvals, mode="lines+markers+text",
        text=[f'D{r["dataset"]}' for r in fit_results], textposition="top center",
        name="Monitoring-based prediction", line=dict(width=3, color=BLUE, shape="spline"),
        marker=dict(size=10, color=BLUE, line=dict(color="white", width=2)),
    ))
    fig.add_hline(
        y=design_delta_st_mm, line_dash="dash", line_color=RED, line_width=2,
        annotation_text="Design-stage Δ<i>S</i><sub>T</sub>", annotation_position="top right",
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
