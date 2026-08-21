import numpy as np
import plotly.graph_objects as go
from calc_core import modified_accumulation


def static_response_figure(sigma_v0, delta_sigma, eb, e_static, cc):
    sig_min = max(1.0, sigma_v0 / 10.0)
    sig_max = max(sigma_v0 + delta_sigma, sigma_v0) * 1.5
    sig = np.logspace(np.log10(sig_min), np.log10(sig_max), 180)
    e_sig = eb - cc * np.log10(sig / sigma_v0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sig, y=e_sig, mode="lines", name="NC compression line", line=dict(width=3)))
    fig.add_trace(go.Scatter(x=[sigma_v0], y=[eb], mode="markers+text", name="Baseline state",
                             text=["eb"], textposition="top center", marker=dict(size=10)))
    fig.add_trace(go.Scatter(x=[sigma_v0 + delta_sigma], y=[e_static], mode="markers+text",
                             name="Peak static state", text=["estatic"], textposition="top center",
                             marker=dict(size=10)))
    fig.update_xaxes(type="log", title="Vertical effective stress, σ′v (kPa)")
    fig.update_yaxes(title="Void ratio, e")
    fig.update_layout(height=470, margin=dict(l=30, r=20, t=30, b=30), legend=dict(orientation="h", y=-0.2))
    return fig


def design_void_ratio_figure(e_static, e_t, n_star, m, i_design):
    i_plot_max = max(float(i_design), 1e6)
    i_grid = np.logspace(0, np.log10(i_plot_max), 360)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=i_grid, y=modified_accumulation(i_grid, e_static, e_t, n_star, m),
                             mode="lines", name="Design-stage prediction", line=dict(width=3)))
    fig.add_hline(y=e_t, line_dash="dash", annotation_text="eT", annotation_position="bottom right")
    fig.add_vline(x=n_star, line_dash="dot", annotation_text="N*", annotation_position="top")
    fig.update_xaxes(type="log", title="Number of repetitive loading cycles, i")
    fig.update_yaxes(title="Void ratio, e")
    fig.update_layout(height=470, margin=dict(l=30, r=20, t=30, b=30), legend=dict(orientation="h", y=-0.2))
    return fig


def calibration_figure(fit_results, e_static, e_t_design, n_design, m_design, i_design, show_all_points):
    max_i_mon = max(x["imax"] for x in fit_results)
    i_curve = np.logspace(0, np.log10(max(float(i_design), max_i_mon, 1e6)), 360)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=i_curve, y=modified_accumulation(i_curve, e_static, e_t_design, n_design, m_design),
        mode="lines", name="Design-stage prediction", line=dict(width=4, dash="dash"),
    ))
    latest = fit_results[-1]
    for r in fit_results:
        fig.add_trace(go.Scatter(
            x=i_curve, y=modified_accumulation(i_curve, e_static, r["eT"], r["Nstar"], r["m"]),
            mode="lines", name=f'Monitoring {r["dataset"]}', line=dict(width=2),
        ))
        if show_all_points or r is latest:
            d = r["df"]
            fig.add_trace(go.Scatter(x=d["i"], y=d["e"], mode="markers", name=f'Measured {r["dataset"]}',
                                     marker=dict(size=5, opacity=0.45), showlegend=show_all_points or r is latest))
    fig.update_xaxes(type="log", title="Number of repetitive loading cycles, i")
    fig.update_yaxes(title="Void ratio, e")
    fig.update_layout(height=500, margin=dict(l=30, r=20, t=30, b=30), legend=dict(orientation="h", y=-0.22))
    return fig


def terminal_settlement_evolution_figure(fit_results, design_delta_st_mm):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[r["imax"] for r in fit_results], y=[r["delta_ST_mm"] for r in fit_results],
        mode="lines+markers+text", text=[f'D{r["dataset"]}' for r in fit_results],
        textposition="top center", name="Monitoring-based prediction", line=dict(width=3), marker=dict(size=9),
    ))
    fig.add_hline(y=design_delta_st_mm, line_dash="dash", annotation_text="Design-stage ΔST",
                  annotation_position="top right")
    fig.update_xaxes(type="log", title="Maximum monitored cycle, imax")
    fig.update_yaxes(title="Predicted terminal repetitive settlement, ΔST (mm)")
    fig.update_layout(height=500, margin=dict(l=30, r=20, t=30, b=30), legend=dict(orientation="h", y=-0.22))
    return fig
