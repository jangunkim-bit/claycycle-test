import numpy as np
import pandas as pd
from scipy.optimize import least_squares


_PROGRESSIVE_FIT_STATE = None


def predict_delta_eT_pysr(e_b, stress_ratio):
    """Final PySR Equation ID 3 used in the manuscript."""
    return 0.045 * stress_ratio * (e_b ** 2.22)


def modified_accumulation(i, e_start, e_t, n_star, m):
    """Design-stage form used in the current framework."""
    i = np.asarray(i, dtype=float)
    return e_t + (e_start - e_t) / (1.0 + np.power(np.maximum(i, 1e-12) / n_star, m))


def monitoring_accumulation(i, e1, e_t, n_star, m):
    """Monitoring form with the first measured void ratio e1 fixed."""
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


def fit_monitoring_dataset(df, e_static=None, initial_guess=None):
    """
    Fast progressive nonlinear least-squares fit of eT, N*, and m.

    - The measured e1 at i = 1 is fixed for each monitoring dataset.
    - eT, N*, and m remain free fitting parameters.
    - No monotonic trend is imposed on eT, N*, m, or ΔST.
    - Monitoring Data 1 uses one broad physically reasonable initial guess.
    - Later stages automatically use the previous-stage optimum when i_max grows.
    - A second generic initial guess is attempted only if the primary fit fails.

    The legacy e_static argument is accepted for backward compatibility and is
    intentionally not used in monitoring fitting.
    """
    global _PROGRESSIVE_FIT_STATE

    i = df["i"].to_numpy(dtype=float)
    e = df["e"].to_numpy(dtype=float)
    e1 = float(e[0])
    e_last = float(e[-1])
    i_max = float(np.max(i))

    if e_last >= e1:
        raise ValueError("Monitoring data must show an overall decrease in void ratio from e1 to the latest observation.")

    # If the app starts a new calibration sequence, the first window normally
    # has an i_max not larger than the final window from the previous run.
    if initial_guess is None and _PROGRESSIVE_FIT_STATE is not None:
        same_series = abs(e1 - _PROGRESSIVE_FIT_STATE.get("e1", e1)) <= max(1e-6, abs(e1) * 1e-5)
        is_next_window = i_max > _PROGRESSIVE_FIT_STATE.get("imax", np.inf)
        if same_series and is_next_window:
            initial_guess = _PROGRESSIVE_FIT_STATE
        else:
            _PROGRESSIVE_FIT_STATE = None

    eps = max(1e-8, abs(e_last) * 1e-8)
    lower_e_t = max(0.001, 0.5 * e_last)
    upper_e_t = e_last - eps
    if upper_e_t <= lower_e_t:
        lower_e_t = max(0.001, 0.25 * e_last)

    lower = np.array([lower_e_t, 1e-3, 0.01], dtype=float)
    upper = np.array([upper_e_t, max(1e7, i_max * 1e4), 1.0], dtype=float)

    def residuals(params):
        return monitoring_accumulation(i, e1, *params) - e

    if initial_guess is not None:
        try:
            x0 = np.array([
                np.clip(float(initial_guess["eT"]), lower[0] + eps, upper[0] - eps),
                np.clip(float(initial_guess["Nstar"]), lower[1] * 10, upper[1] / 10),
                np.clip(float(initial_guess["m"]), lower[2] + 1e-4, upper[2] - 1e-4),
            ], dtype=float)
        except Exception:
            initial_guess = None

    if initial_guess is None:
        # First-window start: deliberately broad, not a constraint. The optimizer
        # is free to move toward low m, large N*, and low eT if the short i-e
        # record supports that solution.
        x0 = np.array([
            np.clip(0.72 * e_last, lower[0] + eps, upper[0] - eps),
            np.clip(max(50.0 * i_max, 100.0), lower[1] * 10, upper[1] / 10),
            0.20,
        ], dtype=float)

    def run_fit(start):
        result = least_squares(
            residuals,
            x0=start,
            bounds=(lower, upper),
            method="trf",
            loss="linear",
            x_scale="jac",
            ftol=1e-8,
            xtol=1e-8,
            gtol=1e-8,
            max_nfev=3000,
        )
        if not result.success or not np.all(np.isfinite(result.x)):
            raise RuntimeError(result.message)
        pred = monitoring_accumulation(i, e1, *result.x)
        rmse = float(np.sqrt(np.mean((pred - e) ** 2)))
        return result.x, rmse

    try:
        best, best_rmse = run_fit(x0)
    except Exception:
        # One backup attempt only; this keeps web execution close to PR #6 speed.
        fallback = np.array([
            np.clip(0.90 * e_last, lower[0] + eps, upper[0] - eps),
            np.clip(max(i_max, 1.0), lower[1] * 10, upper[1] / 10),
            0.50,
        ], dtype=float)
        try:
            best, best_rmse = run_fit(fallback)
        except Exception as exc:
            raise RuntimeError("Nonlinear least-squares fitting did not converge to a valid solution.") from exc

    e_t, n_star, m = best
    fit = {
        "e1": e1,
        "eT": float(e_t),
        "Nstar": float(n_star),
        "m": float(m),
        "RMSE": best_rmse,
        "imax": i_max,
        "df": df,
    }
    _PROGRESSIVE_FIT_STATE = {
        "e1": e1,
        "eT": float(e_t),
        "Nstar": float(n_star),
        "m": float(m),
        "imax": i_max,
    }
    return fit


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
