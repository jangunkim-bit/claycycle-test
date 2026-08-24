import numpy as np
import pandas as pd
from scipy.optimize import least_squares


def predict_delta_eT_pysr(e_b, stress_ratio):
    """Final PySR Equation ID 3 used in the manuscript."""
    return 0.045 * stress_ratio * (e_b ** 2.22)


def modified_accumulation(i, e_static, e_t, n_star, m):
    """Design-stage modified accumulation model."""
    i = np.asarray(i, dtype=float)
    return e_t + (e_static - e_t) / (1.0 + np.power(np.maximum(i, 1e-12) / n_star, m))


def monitoring_accumulation(i, e1, e_t, n_star, m):
    """Monitoring form with the measured void ratio at i=1 fixed as e1."""
    i = np.asarray(i, dtype=float)
    x = np.maximum(i - 1.0, 0.0)
    return e_t + (e1 - e_t) / (1.0 + np.power(x / n_star, m))


def accumulation_ratio(i, n_star, m):
    i = np.asarray(i, dtype=float)
    return np.power(i, m) / (np.power(i, m) + n_star**m)


def cycle_at_ratio(r, n_star, m):
    if not (0.0 < r < 1.0):
        return np.nan
    return n_star * (r / (1.0 - r)) ** (1.0 / m)


def cycles_to_time_text(cycles, frequency_mhz):
    if not np.isfinite(cycles) or frequency_mhz <= 0:
        return "—"
    seconds = cycles / (frequency_mhz / 1000.0)
    if seconds < 3600:
        return f"{seconds / 60:.2f} min"
    if seconds < 86400:
        return f"{seconds / 3600:.2f} h"
    return f"{seconds / 86400:.2f} days"


def read_monitoring_file(uploaded_file):
    name = uploaded_file.name.lower()
    df = pd.read_csv(uploaded_file) if name.endswith(".csv") else pd.read_excel(uploaded_file)
    if df.shape[1] < 2:
        raise ValueError("The file must contain at least two columns: i and e.")
    cols_lower = {str(c).strip().lower(): c for c in df.columns}
    i_col = cols_lower.get("i", df.columns[0])
    e_col = cols_lower.get("e", df.columns[1])
    clean = df[[i_col, e_col]].copy()
    clean.columns = ["i", "e"]
    clean["i"] = pd.to_numeric(clean["i"], errors="coerce")
    clean["e"] = pd.to_numeric(clean["e"], errors="coerce")
    clean = clean.dropna()
    clean = clean[(clean["i"] > 0) & np.isfinite(clean["e"])]
    clean = clean.sort_values("i").drop_duplicates(subset="i", keep="last")
    if len(clean) < 4:
        raise ValueError("At least four valid i-e observations are required for free fitting of eT, N*, and m.")
    if not np.any(np.isclose(clean["i"].to_numpy(dtype=float), 1.0, rtol=0.0, atol=1e-9)):
        raise ValueError("Monitoring data must contain the measured void ratio at i = 1 (e1).")
    return clean


def fit_monitoring_dataset(df, e_static=None):
    """
    PR #6-speed monitoring fit with the measured e1 fixed.

    e1 is read directly from the row where i = 1. Only eT, N*, and m are
    optimized using one nonlinear least-squares fit. The legacy e_static
    argument is accepted for compatibility with the existing app call but is
    not used as the monitoring-curve starting void ratio.
    """
    i = df["i"].to_numpy(dtype=float)
    e = df["e"].to_numpy(dtype=float)

    e1_mask = np.isclose(i, 1.0, rtol=0.0, atol=1e-9)
    if not np.any(e1_mask):
        raise ValueError("Monitoring data must contain i = 1 so e1 can be fixed from the measured data.")
    e1 = float(e[np.flatnonzero(e1_mask)[0]])

    observed_min = float(np.min(e))
    observed_max = float(np.max(e))
    spread = max(observed_max - observed_min, 1e-4)

    lower_e_t = max(0.001, observed_min - max(1.0, 5.0 * spread))
    upper_e_t = observed_min - 1e-8
    if upper_e_t <= lower_e_t:
        lower_e_t = max(0.001, upper_e_t * 0.5)

    lower = np.array([lower_e_t, 1e-3, 0.05], dtype=float)
    upper = np.array([upper_e_t, max(float(np.max(i)) * 1e5, 1e6), 2.0], dtype=float)
    x0 = np.array([
        np.clip(observed_min - max(0.01, 0.25 * spread), lower[0] + 1e-8, upper[0] - 1e-8),
        np.clip(float(np.median(np.maximum(i - 1.0, 1e-3))), lower[1] * 10, upper[1] / 10),
        0.5,
    ])

    def residuals(params):
        e_t, n_star, m = params
        return monitoring_accumulation(i, e1, e_t, n_star, m) - e

    result = least_squares(
        residuals,
        x0=x0,
        bounds=(lower, upper),
        method="trf",
        loss="linear",
        max_nfev=50000,
    )
    if not result.success:
        raise RuntimeError(result.message)

    e_t, n_star, m = result.x
    pred = monitoring_accumulation(i, e1, e_t, n_star, m)
    rmse = float(np.sqrt(np.mean((pred - e) ** 2)))
    return {
        "e1": e1,
        "eT": float(e_t),
        "Nstar": float(n_star),
        "m": float(m),
        "RMSE": rmse,
        "imax": float(np.max(i)),
        "df": df,
    }


def assessment_from_parameters(h_b_m, e_b, e_static, e_t, n_star, m,
                               s_static_mm, i_design, f_mhz, s_allow_mm):
    delta_e_t = e_static - e_t
    delta_s_t_mm = h_b_m * delta_e_t / (1.0 + e_b) * 1000.0
    r_design = float(accumulation_ratio(i_design, n_star, m))
    s_terminal_total = s_static_mm + delta_s_t_mm
    s_design_total = s_static_mm + delta_s_t_mm * r_design
    i50 = cycle_at_ratio(0.5, n_star, m)
    i90 = cycle_at_ratio(0.9, n_star, m)

    if delta_s_t_mm <= 0:
        i_allow, allow_text = np.nan, "Not applicable"
    else:
        eta_allow = (s_allow_mm - s_static_mm) / delta_s_t_mm
        if eta_allow <= 0:
            i_allow, allow_text = 0.0, "Already reached at the end of static loading"
        elif eta_allow >= 1:
            i_allow, allow_text = np.inf, "Not reached before the terminal state"
        else:
            i_allow = cycle_at_ratio(eta_allow, n_star, m)
            allow_text = f"{i_allow:,.0f} cycles"

    return {
        "Sstatic_mm": s_static_mm,
        "delta_eT": delta_e_t,
        "delta_ST_mm": delta_s_t_mm,
        "ST_total_mm": s_terminal_total,
        "Sdesign_total_mm": s_design_total,
        "Rdesign": r_design,
        "i50": i50,
        "t50": cycles_to_time_text(i50, f_mhz),
        "i90": i90,
        "t90": cycles_to_time_text(i90, f_mhz),
        "Sallow_mm": s_allow_mm,
        "iallow": i_allow,
        "iallow_text": allow_text,
        "tallow": cycles_to_time_text(i_allow, f_mhz) if np.isfinite(i_allow) else "—",
        "exceedance_mm": s_design_total - s_allow_mm,
        "satisfied": s_design_total <= s_allow_mm,
    }


def fmt_cycles(x):
    return "—" if not np.isfinite(x) else f"{x:,.0f} cycles"


def make_assessment_table(a):
    status = "Satisfied" if a["satisfied"] else "Not satisfied"
    return pd.DataFrame([
        ["How much", "Static consolidation settlement", "Sstatic", f'{a["Sstatic_mm"]:,.1f} mm'],
        ["How much", "Terminal repetitive settlement", "ΔST (i = ∞)", f'{a["delta_ST_mm"]:,.1f} mm'],
        ["How much", "Terminal total settlement", "ST(total)", f'{a["ST_total_mm"]:,.1f} mm'],
        ["How much", "Design-life total settlement", "Sdesign(total)", f'{a["Sdesign_total_mm"]:,.1f} mm'],
        ["How fast", "50% accumulation", "iR=0.5, tR=0.5", f'{fmt_cycles(a["i50"])}, {a["t50"]}'],
        ["How fast", "90% accumulation", "iR=0.9, tR=0.9", f'{fmt_cycles(a["i90"])}, {a["t90"]}'],
        ["Serviceability", "Allowable settlement", "Sallow", f'{a["Sallow_mm"]:,.1f} mm'],
        ["Serviceability", "Allowable-settlement reach", "iallow, tallow", f'{a["iallow_text"]}, {a["tallow"]}'],
        ["Serviceability", "Design-life assessment", "Sdesign(total) ≤ Sallow", status],
        ["Serviceability", "Exceedance at design life", "Sdesign − Sallow", f'{a["exceedance_mm"]:,.1f} mm'],
    ], columns=["Category", "Evaluation", "Symbol", "Result"])
