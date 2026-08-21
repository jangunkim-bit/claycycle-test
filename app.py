import numpy as np
import pandas as pd
import streamlit as st

from calc_core import (
    assessment_from_parameters,
    fit_monitoring_dataset,
    make_assessment_table,
    read_monitoring_file,
)
from charts import (
    calibration_figure,
    design_void_ratio_figure,
    static_response_figure,
    terminal_settlement_evolution_figure,
)
from style import apply_style, hero


st.set_page_config(page_title="Long-Term Settlement Assessment", page_icon="📈", layout="wide")
apply_style()
hero()

# -----------------------------------------------------------------------------
# 1. Design input
# -----------------------------------------------------------------------------
st.markdown('<span class="section-tag">01 · DESIGN STAGE</span>', unsafe_allow_html=True)
st.header("1. Design Input Parameters")
st.caption("Enter the ground condition, repetitive loading condition, and serviceability criterion.")

with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**Ground condition**")
        h0 = st.number_input("Initial clay-layer thickness, H0 (m)", min_value=0.1, value=2.0, step=0.1)
        e0 = st.number_input("Initial void ratio, e0", min_value=0.05, value=1.6214, step=0.01, format="%.4f")
        eb = st.number_input("Baseline void ratio, eb", min_value=0.05, value=1.2627, step=0.01, format="%.4f")
    with c2:
        st.markdown("**Static response**")
        cc = st.number_input("Compression index, Cc", min_value=0.001, value=0.346, step=0.01, format="%.3f")
        sigma_v0 = st.number_input("Initial vertical effective stress, σ′v0 (kPa)", min_value=1.0, value=100.0, step=10.0)
        delta_sigma = st.number_input("Stress amplitude, Δσ (kPa)", min_value=0.1, value=300.0, step=10.0)
    with c3:
        st.markdown("**Repetitive loading**")
        f_mhz = st.number_input("Loading frequency, f (mHz)", min_value=0.001, value=125.0, step=1.0, format="%.3f")
        i_design = st.number_input("Design number of cycles, idesign", min_value=1, value=1_000_000, step=1000)
        st.text_input("Soil state", value="Normally consolidated clay (OCR = 1.0)", disabled=True)
    with c4:
        st.markdown("**Design criterion**")
        allow_factor = st.number_input("Allowable settlement factor, Sallow / Sstatic", min_value=1.0, value=1.30, step=0.05)
        st.markdown("**Prototype equation input**")
        delta_eT_design = st.number_input(
            "ΔeT from PySR Equation ID 3",
            min_value=0.0001,
            value=0.2268,
            step=0.005,
            format="%.4f",
            help="Temporary manual input in this prototype. It will be replaced by the exact PySR Equation ID 3 expression.",
        )

stress_ratio = delta_sigma / sigma_v0
e_static = eb - cc * np.log10((sigma_v0 + delta_sigma) / sigma_v0)
h_b = h0 * (1.0 + eb) / (1.0 + e0)
h_peak = h0 * (1.0 + e_static) / (1.0 + e0)
s_static_mm = (h0 - h_peak) * 1000.0
s_allow_mm = allow_factor * s_static_mm

e_t_design = e_static - delta_eT_design
m_design = 0.5
n_design = 177.7 * eb + 70.7 * stress_ratio + 46.59

design_assessment = assessment_from_parameters(
    h_b, eb, e_static, e_t_design, n_design, m_design,
    s_static_mm, i_design, f_mhz, s_allow_mm,
)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Δσ / σ′v0", f"{stress_ratio:.3f}")
m2.metric("estatic", f"{e_static:.4f}")
m3.metric("Hb", f"{h_b:.4f} m")
m4.metric("N*", f"{n_design:,.0f}")
m5.metric("m", f"{m_design:.2f}")

# -----------------------------------------------------------------------------
# 2. Design-stage prediction
# -----------------------------------------------------------------------------
st.header("2. Design-Stage Long-Term Response Prediction")
left, right = st.columns(2, gap="large")
with left:
    st.subheader("2-1. Static Consolidation Response and Reference State Determination")
    st.plotly_chart(
        static_response_figure(sigma_v0, delta_sigma, eb, e_static, cc),
        use_container_width=True,
    )
with right:
    st.subheader("2-2. Long-Term Void Ratio Response under Repetitive Loading")
    st.plotly_chart(
        design_void_ratio_figure(e_static, e_t_design, n_design, m_design, i_design),
        use_container_width=True,
    )

# -----------------------------------------------------------------------------
# 3. Design-stage assessment
# -----------------------------------------------------------------------------
st.header("3. Design-Stage Settlement Assessment")
st.caption("Key design-stage results: how much, how fast, and serviceability.")
st.dataframe(make_assessment_table(design_assessment), use_container_width=True, hide_index=True)
if design_assessment["satisfied"]:
    st.markdown('<div class="status-good">✓ Design-life serviceability criterion is satisfied.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-bad">✕ Design-life serviceability criterion is not satisfied.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. Monitoring input
# -----------------------------------------------------------------------------
st.markdown('<span class="section-tag">02 · MONITORING STAGE</span>', unsafe_allow_html=True)
st.header("4. Monitoring Data Input")
st.caption("Upload 1–10 monitoring datasets in i-e format. One dataset is sufficient to run the calibration.")

uploaded = []
u1, u2 = st.columns(2, gap="large")
for idx in range(10):
    target = u1 if idx < 5 else u2
    with target:
        uploaded.append(st.file_uploader(
            f"Monitoring Data {idx + 1}",
            type=["xlsx", "xls", "csv"],
            key=f"monitor_{idx+1}",
            help="Expected columns: i and e. If headers differ, the first two columns are used.",
        ))

show_all_points = st.checkbox("Show all measured points in Graph 3", value=False)
run_calibration = st.button("Run Monitoring Calibration", type="primary", use_container_width=True)

if run_calibration:
    fit_results, errors = [], []
    for idx, uploaded_file in enumerate(uploaded, start=1):
        if uploaded_file is None:
            continue
        try:
            df_mon = read_monitoring_file(uploaded_file)
            fit = fit_monitoring_dataset(df_mon, e_static)
            fit["dataset"] = idx
            fit["filename"] = uploaded_file.name
            fit["delta_ST_mm"] = h_b * (e_static - fit["eT"]) / (1.0 + eb) * 1000.0
            fit_results.append(fit)
        except Exception as exc:
            errors.append(f"Monitoring Data {idx}: {exc}")
    st.session_state["fit_results"] = fit_results
    st.session_state["fit_errors"] = errors

fit_results = st.session_state.get("fit_results", [])
fit_errors = st.session_state.get("fit_errors", [])
for msg in fit_errors:
    st.warning(msg)

# -----------------------------------------------------------------------------
# 5. Monitoring-based updating
# -----------------------------------------------------------------------------
if fit_results:
    fit_results = sorted(fit_results, key=lambda x: x["imax"])
    st.header("5. Monitoring-Based Calibration and Long-Term Prediction Updating")
    g3, g4 = st.columns(2, gap="large")

    with g3:
        st.subheader("5-1. Calibration of Long-Term Void Ratio Response Using Monitoring Data")
        st.plotly_chart(
            calibration_figure(
                fit_results, e_static, e_t_design, n_design, m_design, i_design, show_all_points
            ),
            use_container_width=True,
        )

    with g4:
        st.subheader("5-2. Evolution of Predicted Terminal Repetitive Settlement with Monitoring Duration")
        st.plotly_chart(
            terminal_settlement_evolution_figure(fit_results, design_assessment["delta_ST_mm"]),
            use_container_width=True,
        )

    st.markdown("#### 5-3. Summary of Monitoring-Based Calibration Results")
    calibration_table = pd.DataFrame([
        {
            "Monitoring data": f'Data {r["dataset"]}',
            "imax (cycles)": f'{r["imax"]:,.0f}',
            "eT": f'{r["eT"]:.5f}',
            "N*": f'{r["Nstar"]:,.1f}',
            "m": f'{r["m"]:.4f}',
            "RMSE": f'{r["RMSE"]:.6f}',
            "ΔST (mm)": f'{r["delta_ST_mm"]:.1f}',
        }
        for r in fit_results
    ])
    st.dataframe(calibration_table, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # 6. Monitoring-calibrated assessment
    # -------------------------------------------------------------------------
    st.header("6. Monitoring-Calibrated Settlement Assessment")
    latest = fit_results[-1]
    calibrated = assessment_from_parameters(
        h_b, eb, e_static, latest["eT"], latest["Nstar"], latest["m"],
        s_static_mm, i_design, f_mhz, s_allow_mm,
    )

    design_table = make_assessment_table(design_assessment)
    calibrated_table = make_assessment_table(calibrated)
    comparison = design_table[["Category", "Evaluation", "Symbol"]].copy()
    comparison["Design-stage"] = design_table["Result"]
    comparison["Monitoring-calibrated"] = calibrated_table["Result"]
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    if calibrated["satisfied"]:
        st.markdown('<div class="status-good">✓ Monitoring-calibrated design-life serviceability criterion is satisfied.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-bad">✕ Monitoring-calibrated design-life serviceability criterion is not satisfied.</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Engineering comments
    # -------------------------------------------------------------------------
    st.header("Engineering Comments")
    design_dst = design_assessment["delta_ST_mm"]
    calib_dst = calibrated["delta_ST_mm"]
    change_pct = ((calib_dst - design_dst) / design_dst * 100.0) if abs(design_dst) > 1e-12 else np.nan

    if np.isfinite(change_pct) and change_pct > 5:
        comment1 = (
            f"The latest monitoring-based terminal repetitive settlement is {calib_dst:.1f} mm, "
            f"{abs(change_pct):.1f}% larger than the design-stage estimate. The long-term repetitive "
            "settlement demand should therefore be updated using the monitoring-calibrated response."
        )
    elif np.isfinite(change_pct) and change_pct < -5:
        comment1 = (
            f"The latest monitoring-based terminal repetitive settlement is {calib_dst:.1f} mm, "
            f"{abs(change_pct):.1f}% smaller than the design-stage estimate, indicating a lower long-term "
            "repetitive settlement demand than initially predicted."
        )
    else:
        comment1 = (
            f"The latest monitoring-based terminal repetitive settlement ({calib_dst:.1f} mm) remains close "
            f"to the design-stage estimate ({design_dst:.1f} mm), indicating limited change in the terminal prediction."
        )

    if calibrated["satisfied"]:
        comment2 = (
            f"At {i_design:,.0f} design cycles, the monitoring-calibrated total settlement is "
            f"{calibrated['Sdesign_total_mm']:.1f} mm, within the allowable settlement of {s_allow_mm:.1f} mm."
        )
    else:
        comment2 = (
            f"At {i_design:,.0f} design cycles, the monitoring-calibrated total settlement is "
            f"{calibrated['Sdesign_total_mm']:.1f} mm and exceeds the allowable settlement of {s_allow_mm:.1f} mm "
            f"by {calibrated['exceedance_mm']:.1f} mm. Adjustment of repetitive loading conditions, ground "
            "improvement, or foundation modification should be considered."
        )

    comment3 = (
        f"The latest calibration uses monitoring data up to i = {latest['imax']:,.0f} cycles and gives "
        f"eT = {latest['eT']:.5f}, N* = {latest['Nstar']:.1f}, m = {latest['m']:.4f}, and RMSE = {latest['RMSE']:.6f}. "
        "Graph 4 can be used to judge whether the predicted terminal repetitive settlement stabilizes as the monitoring duration increases."
    )

    st.markdown(f'<div class="eng-comment"><b>1. Terminal response.</b> {comment1}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="eng-comment"><b>2. Serviceability.</b> {comment2}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="eng-comment"><b>3. Monitoring interpretation.</b> {comment3}</div>', unsafe_allow_html=True)
else:
    st.info("Upload at least one i-e dataset in Section 4 and click **Run Monitoring Calibration** to activate Sections 5 and 6.")

st.divider()
st.caption(
    "Prototype for research use. Monitoring calibration performs nonlinear least-squares free fitting of eT, N*, and m. "
    "The design-stage ΔeT input is temporary and will be replaced by the exact PySR Equation ID 3 expression in the final version."
)
