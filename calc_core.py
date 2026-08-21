import numpy as np
import pandas as pd
from scipy.optimize import least_squares


def predict_delta_eT_pysr(e_b, stress_ratio):
    """Final PySR Equation ID 3 used in the manuscript."""
    return 0.045 * stress_ratio * (e_b ** 2.22)


def modified_accumulation(i, e_start, e_t, n_star, m):
    """Design-stage form used in the current framework."""
    i = np.asarray(i, dtype=float)
    return e_t + (e_start - e_t) / (1.0 + np.power(np.maximum(i, 1e-12) / n_star, m))


def monitoring_accumulation(i, e1, e_t, n_star, m):
    """
    Monitoring fitting form of the modified accumulation model.

    The first measured loading-phase void ratio e1 is fixed for each monitoring
    dataset and only eT, N*, and m are fitted:

        ei = eT + (e1-eT) [1 + ((i-1)/N*)^m]^-1

    This makes the fitted curve pass exactly through e1 at i=1 and follows the
    model form reported in Cha's dissertation for progressive fitting.
    """
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
    clean = clean[(clean["i"] >= 1) & np.isfinite(clean["e"])]
    clean = clean.sort_values("i").drop_duplicates(subset="i", keep="last")
    if len(clean) < 4:
        raise ValueError("At least four valid i-e observations are required for free fitting of eT, N*, and m.")
    return clean


def fit_monitoring_dataset(df):
    """
    Free nonlinear least-squares fit of eT, N*, and m for one monitoring dataset.

    - e1 is fixed to the first measured void ratio.
    - eT is searched within 0.5*e_last < eT < e_last, consistent with the
      parameter-search range described in Cha's dissertation.
    - m is free within 0.01-1.0.
    - Multiple starting points are tested; the solution with the minimum RMSE
      is retained. No monotonic or trend constraint is imposed across datasets.
    """
    i = df["i"].to_numpy(dtype=float)
    e = df["e"].to_numpy(dtype=float)
    e1 = float(e[0])
    e_last = float(e[-1])
    i_max = float(np.max(i))

    if e_last >= e1:
        raise ValueError("Monitoring data must show an overall decrease in void ratio from e1 to the latest observation.")

    eps = max(1e-8, abs(e_last) * 1e-8)
    lower_e_t = max(0.001, 0.5 * e_last)
    upper_e_t = e_last - eps
    if upper_e_t <= lower_e_t:
        lower_e_t = max(0.001, 0.25 * e_last)

    lower_n = 1e-3
    upper_n = max(1e8, i_max * 1e5)
    lower = np.array([lower_e_t, lower_n, 0.01], dtype=float)
    upper = np.array([upper_e_t, upper_n, 1.0], dtype=float)

    # Broad, physically neutral multistart grid. Early short windows are allowed
    # to select small m and very large N* if that minimizes RMSE.
    e_fracs = [0.55, 0.70, 0.85, 0.97]
    n_mults = [0.5, 2.0, 10.0, 100.0, 1000.0]
    m_starts = [0.05, 0.15, 0.35, 0.55, 0.85]

    best = None
    best_rmse = np.inf

    def residuals(params):
        e_t, n_star, m = params
        return monitoring_accumulation(i, e1, e_t, n_star, m) - e

    for e_frac in e_fracs:
        e0_guess = np.clip(e_last * e_frac, lower[0] + eps, upper[0] - eps)
        for n_mult in n_mults:
            n0_guess = np.clip(max(i_max * n_mult, 1.0), lower[1] * 10, upper[1] / 10)
            for m0 in m_starts:
                x0 = np.array([e0_guess, n0_guess, m0], dtype=float)
                try:
                    result = least_squares(
                        residuals,
                        x0=x0,
                        bounds=(lower, upper),
                        method="trf",
                        loss="linear",
                        x_scale="jac",
                        ftol=1e-12,
                        xtol=1e-12,
                        gtol=1e-12,
                        max_nfev=20000,
                    )
                except Exception:
                    continue

                if not result.success or not np.all(np.isfinite(result.x)):
                    continue

                pred = monitoring_accumulation(i, e1, *result.x)
                rmse = float(np.sqrt(np.mean((pred - e) ** 2)))
                if rmse < best_rmse:
                    best_rmse = rmse
                    best = result.x.copy()

    if best is None:
        raise RuntimeError("Nonlinear least-squares fitting did not converge to a valid solution.")

    e_t, n_star, m = best
    return {
        "e1": e1,
        "eT": float(e_t),
        "Nstar": float(n_star),
        "m": float(m),
        "RMSE": best_rmse,
        "imax": i_max,
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
