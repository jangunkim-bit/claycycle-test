import numpy as np
import pandas as pd
import streamlit as st

from calc_core import (
    assessment_from_parameters,
    fit_monitoring_dataset,
    read_monitoring_file,
)
from charts import (
    calibration_figure,
    design_void_ratio_figure,
    static_response_figure,
    terminal_settlement_evolution_figure,
)
from style import (
    apply_style,
    hero,
    input_label,
    render_assessment_table,
    result_card,
)


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
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown("**Ground condition**")
        input_label('Initial clay-layer thickness, <i>H</i><sub>0</sub> (m)')
        h0 = st.number_input("H0 hidden", min_value=0.1, value=2.0, step=0.1, label_visibility="collapsed", key="h0")

        input_label('Initial void ratio, <i>e</i><sub>0</sub>')
        e0 = st.number_input("e0 hidden", min_value=0.05, value=1.6214, step=0.01, format="%.4f", label_visibility="collapsed", key="e0")

        input_label('Baseline void ratio, <i>e</i><sub>b</sub>')
        eb = st.number_input("eb hidden", min_value=0.05, value=1.2627, step=0.01, format="%.4f", label_visibility="collapsed", key="eb")

    with c2:
        st.markdown("**Static response**")
        input_label('Compression index, <i>C</i><sub>c</sub>')
        cc = st.number_input("Cc hidden", min_value=0.001, value=0.400, step=0.01, format="%.3f", label_visibility="collapsed", key="cc")

        input_label('Initial vertical effective stress, <i>σ</i>′<sub>v0</sub> (kPa)')
        sigma_v0 = st.number_input("sigma hidden", min_value=1.0, value=100.0, step=10.0, label_visibility="collapsed", key="sigma_v0")

        input_label('Stress amplitude, Δ<i>σ</i> (kPa)')
        delta_sigma = st.number_input("delta sigma hidden", min_value=0.1, value=300.0, step=10.0, label_visibility="collapsed", key="delta_sigma")

    with c3:
        st.markdown("**Repetitive loading**")
        input_label('Loading frequency, <i>f</i> (mHz)')
        f_mhz = st.number_input("frequency hidden", min_value=0.001, value=125.0, step=1.0, format="%.3f", label_visibility="collapsed", key="frequency")

        input_label('Design number of cycles, <i>i</i><sub>design</sub>')
        i_design = st.number_input("design cycles hidden", min_value=1, value=1_000_000, step=1000, label_visibility="collapsed", key="i_design")

        input_label('Soil state')
        st.text_input("soil state hidden", value="Normally consolidated clay (OCR = 1.0)", disabled=True, label_visibility="collapsed", key="soil_state")

    # Static quantities are evaluated before rendering the design-criterion column.
    e_static = eb - cc * np.log10((sigma_v0 + delta_sigma) / sigma_v0)
    h_b = h0 * (1.0 + eb) / (1.0 + e0)
    h_peak = h0 * (1.0 + e_static) / (1.0 + e0)
    s_static_mm = (h0 - h_peak) * 1000.0

    with c4:
        st.markdown("**Design criterion**")
        input_label('Allowable settlement factor, <i>S</i><sub>allow</sub> / <i>S</i><sub>static</sub>')
        allow_factor = st.number_input("allow factor hidden", min_value=1.0, value=1.50, step=0.05, label_visibility="collapsed", key="allow_factor")

        s_allow_mm = allow_factor * s_static_mm
        input_label('Allowable settlement, <i>S</i><sub>allow</sub> (mm)')
        st.number_input("allow settlement hidden", value=float(s_allow_mm), disabled=True, format="%.1f", label_visibility="collapsed", key="s_allow_display")

        input_label('Δ<i>e</i><sub>T</sub> from PySR Equation ID 3')
        delta_eT_design = st.number_input(
            "delta eT hidden", min_value=0.0001, value=0.2268, step=0.005, format="%.4f",
            label_visibility="collapsed", key="delta_eT_design",
            help="Temporary manual input in this prototype. It will be replaced by the exact PySR Equation ID 3 expression.",
        )

stress_ratio = delta_sigma / sigma_v0
e_t_design = e_static - delta_eT_design
m_design = 0.5
n_design = 177.7 * eb + 70.7 * stress_ratio + 46.59

design_assessment = assessment_from_parameters(
    h_b, eb, e_static, e_t_design, n_design, m_design,
    s_static_mm, i_design, f_mhz, s_allow_mm,
)

m1, m2, m3, m4, m5 = st.columns(5, gap="small")
with m1:
    result_card('Stress amplitude ratio, Δ<i>σ</i> / <i>σ</i>′<sub>v0</sub>', f"{stress_ratio:.3f}")
with m2:
    result_card('Static void ratio, <i>e</i><sub>static</sub>', f"{e_static:.4f}")
with m3:
    result_card('Baseline layer thickness, <i>H</i><sub>b</sub>', f"{h_b:.4f} m")
with m4:
    result_card('Characteristic cycle number, <i>N</i>*', f"{n_design:,.0f}")
with m5:
    result_card('Curvature parameter, <i>m</i>', f"{m_design:.2f}")

# -----------------------------------------------------------------------------
# 2. Design-stage prediction
# -----------------------------------------------------------------------------
st.header("2. Design-Stage Long-Term Response Prediction")
left, right = st.columns(2, gap="large")
with left:
    st.subheader("2-1. Static Response")
    st.plotly_chart(
        static_response_figure(sigma_v0, delta_sigma, eb, e_static, cc),
        use_container_width=True,
    )
    st.markdown('<div class="graph-result">', unsafe_allow_html=True)
    result_card('Static consolidation settlement, <i>S</i><sub>static</sub>', f'{s_static_mm:,.1f} mm')
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.subheader("2-2. Repetitive Response")
    st.plotly_chart(
        design_void_ratio_figure(e_static, e_t_design, n_design, m_design, i_design),
        use_container_width=True,
    )
    st.markdown('<div class="graph-result">', unsafe_allow_html=True)
    result_card('Terminal repetitive settlement, Δ<i>S</i><sub>T</sub> (<i>i</i> = ∞)', f'{design_assessment["delta_ST_mm"]:,.1f} mm')
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Design-stage assessment
# -----------------------------------------------------------------------------
st.header("3. Design-Stage Settlement Assessment")
st.caption("Key design-stage results: how much, how fast, and serviceability.")
render_assessment_table(design_assessment)
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
        st.subheader("5-1. Calibrated Repetitive Response")
        st.plotly_chart(
            calibration_figure(
                fit_results, e_static, e_t_design, n_design, m_design, i_design, show_all_points
            ),
            use_container_width=True,
        )

    with g4:
        st.subheader("5-2. Terminal Settlement Updating")
        st.plotly_chart(
            terminal_settlement_evolution_figure(fit_results, design_assessment["delta_ST_mm"]),
            use_container_width=True,
        )

    st.markdown("#### 5-3. Monitoring Calibration Results")
    rows = []
    for r in fit_results:
        rows.append(
            f'<tr><td>Data {r["dataset"]}</td><td>{r["imax"]:,.0f}</td>'
            f'<td>{r["eT"]:.5f}</td><td>{r["Nstar"]:,.1f}</td><td>{r["m"]:.4f}</td>'
            f'<td>{r["RMSE"]:.6f}</td><td>{r["delta_ST_mm"]:.1f}</td></tr>'
        )
    calibration_html = (
        '<div class="assessment-wrap"><table class="assessment"><thead><tr>'
        '<th>Monitoring data</th><th><i>i</i><sub>max</sub> (cycles)</th>'
        '<th><i>e</i><sub>T</sub></th><th><i>N</i>*</th><th><i>m</i></th>'
        '<th>RMSE</th><th>Δ<i>S</i><sub>T</sub> (mm)</th>'
        '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'
    )
    st.markdown(calibration_html, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 6. Monitoring-calibrated assessment
    # -------------------------------------------------------------------------
    st.header("6. Monitoring-Calibrated Settlement Assessment")
    latest = fit_results[-1]
    calibrated = assessment_from_parameters(
        h_b, eb, e_static, latest["eT"], latest["Nstar"], latest["m"],
        s_static_mm, i_design, f_mhz, s_allow_mm,
    )
    render_assessment_table(design_assessment, calibrated)

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
        f"The latest calibration uses monitoring data up to <i>i</i> = {latest['imax']:,.0f} cycles and gives "
        f"<i>e</i><sub>T</sub> = {latest['eT']:.5f}, <i>N</i>* = {latest['Nstar']:.1f}, "
        f"<i>m</i> = {latest['m']:.4f}, and RMSE = {latest['RMSE']:.6f}. "
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
