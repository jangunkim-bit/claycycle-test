import numpy as np
import plotly.graph_objects as go
from calc_core import modified_accumulation


def _style_axes(fig):
    fig.update_xaxes(
        showline=True, linewidth=1.2, linecolor="#344054", mirror=True,
        ticks="outside", ticklen=6, tickwidth=1.1, tickcolor="#344054",
        showticklabels=True, tickfont=dict(size=12, color="#344054"),
        showgrid=True, gridcolor="#E7EDF3", gridwidth=1, zeroline=False,
        title_font=dict(size=13, color="#344054"),
    )
    fig.update_yaxes(
        showline=True, linewidth=1.2, linecolor="#344054", mirror=True,
        ticks="outside", ticklen=6, tickwidth=1.1, tickcolor="#344054",
        showticklabels=True, tickfont=dict(size=12, color="#344054"),
        showgrid=True, gridcolor="#E7EDF3", gridwidth=1, zeroline=False,
        title_font=dict(size=13, color="#344054"),
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", hovermode="closest",
        font=dict(family="Arial, sans-serif", size=12, color="#344054"),
    )
    return fig


def static_response_figure(sigma_v0, delta_sigma, eb, e_static, cc):
    sig_min = max(1.0, sigma_v0 / 10.0)
    sig_max = max(sigma_v0 + delta_sigma, sigma_v0) * 1.5
    sig = np.logspace(np.log10(sig_min), np.log10(sig_max), 180)
    e_sig = eb - cc * np.log10(sig / sigma_v0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sig, y=e_sig, mode="lines", name="NC compression line", line=dict(width=3)
    ))
    fig.add_trace(go.Scatter(
        x=[sigma_v0], y=[eb], mode="markers+text", name="Baseline state",
        text=["<i>e</i><sub>b</sub>"], textposition="top center", marker=dict(size=10)
    ))
    fig.add_trace(go.Scatter(
        x=[sigma_v0 + delta_sigma], y=[e_static], mode="markers+text", name="Peak static state",
        text=["<i>e</i><sub>static</sub>"], textposition="top center", marker=dict(size=10)
    ))

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
        height=455, margin=dict(l=55, r=25, t=20, b=65),
        legend=dict(orientation="h", y=-0.24, x=0),
    )
    return _style_axes(fig)


def design_void_ratio_figure(e_static, e_t, n_star, m, i_design):
    i_plot_max = max(float(i_design), 1e6)
    i_grid = np.logspace(0, np.log10(i_plot_max), 360)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=i_grid, y=modified_accumulation(i_grid, e_static, e_t, n_star, m),
        mode="lines", name="Design-stage prediction", line=dict(width=3)
    ))
    fig.add_hline(
        y=e_t, line_dash="dash", annotation_text="<i>e</i><sub>T</sub>",
        annotation_position="bottom right"
    )
    fig.add_vline(
        x=n_star, line_dash="dot", annotation_text="<i>N</i>*",
        annotation_position="top"
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
        height=455, margin=dict(l=55, r=25, t=20, b=65),
        legend=dict(orientation="h", y=-0.24, x=0),
    )
    return _style_axes(fig)


def calibration_figure(fit_results, e_static, e_t_design, n_design, m_design, i_design, show_all_points):
    max_i_mon = max(x["imax"] for x in fit_results)
    i_plot_max = max(float(i_design), max_i_mon, 1e6)
    i_curve = np.logspace(0, np.log10(i_plot_max), 360)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=i_curve, y=modified_accumulation(i_curve, e_static, e_t_design, n_design, m_design),
        mode="lines", name="Design-stage prediction", line=dict(width=4, dash="dash")
    ))

    latest = fit_results[-1]
    for r in fit_results:
        fig.add_trace(go.Scatter(
            x=i_curve, y=modified_accumulation(i_curve, e_static, r["eT"], r["Nstar"], r["m"]),
            mode="lines", name=f'Monitoring {r["dataset"]}', line=dict(width=2)
        ))
        if show_all_points or r is latest:
            d = r["df"]
            fig.add_trace(go.Scatter(
                x=d["i"], y=d["e"], mode="markers", name=f'Measured {r["dataset"]}',
                marker=dict(size=5, opacity=0.45), showlegend=show_all_points or r is latest
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
        height=485, margin=dict(l=55, r=25, t=20, b=75),
        legend=dict(orientation="h", y=-0.28, x=0),
    )
    return _style_axes(fig)


def terminal_settlement_evolution_figure(fit_results, design_delta_st_mm):
    fig = go.Figure()
    xvals = [r["imax"] for r in fit_results]
    yvals = [r["delta_ST_mm"] for r in fit_results]
    fig.add_trace(go.Scatter(
        x=xvals, y=yvals, mode="lines+markers+text",
        text=[f'D{r["dataset"]}' for r in fit_results], textposition="top center",
        name="Monitoring-based prediction", line=dict(width=3), marker=dict(size=9)
    ))
    fig.add_hline(
        y=design_delta_st_mm, line_dash="dash",
        annotation_text="Design-stage Δ<i>S</i><sub>T</sub>", annotation_position="top right"
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
        height=485, margin=dict(l=65, r=25, t=20, b=75),
        legend=dict(orientation="h", y=-0.28, x=0),
    )
    return _style_axes(fig)
