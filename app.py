import numpy as np
import streamlit as st

from calc_core import (
    assessment_from_parameters,
    fit_monitoring_dataset,
    predict_delta_eT_pysr,
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
    stage_title,
)


st.set_page_config(page_title="Long-Term Settlement Assessment", page_icon="📈", layout="wide")
nav_request = st.query_params.get("nav", "")
monitoring_ready = bool(st.session_state.get("fit_results", []))
apply_style()
hero(monitoring_ready=monitoring_ready)

# -----------------------------------------------------------------------------
# 01. DESIGN STAGE
# -----------------------------------------------------------------------------
stage_title("01", "DESIGN STAGE")
st.markdown('<div id="design-input" class="section-anchor"></div>', unsafe_allow_html=True)
st.header("1. Design Input Parameters")
st.caption("Enter the ground condition, repetitive loading condition, and design criterion.")

with st.container(border=True):
    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.markdown("### Ground condition")
        input_label('Initial clay-layer thickness, <i>H</i><sub>0</sub> (m)')
        h0 = st.number_input(
            "H0 hidden", min_value=0.1, value=2.0, step=0.1,
            label_visibility="collapsed", key="h0"
        )

        input_label('Initial void ratio at <i>σ</i>′<sub>v</sub> = 1 kPa, <i>e</i><sub>0</sub>')
        e0 = st.number_input(
            "e0 hidden", min_value=0.05, value=1.9547, step=0.01, format="%.4f",
            label_visibility="collapsed", key="e0"
        )

        input_label('Compression index, <i>C</i><sub>c</sub>')
        cc = st.number_input(
            "Cc hidden", min_value=0.001, value=0.346, step=0.01, format="%.3f",
            label_visibility="collapsed", key="cc"
        )

    with c2:
        st.markdown("### Repetitive loading condition")
        input_label('Initial vertical effective stress, <i>σ</i>′<sub>v0</sub> (kPa)')
        sigma_v0 = st.number_input(
            "sigma hidden", min_value=1.0, value=100.0, step=10.0,
            label_visibility="collapsed", key="sigma_v0"
        )

        input_label('Stress amplitude, Δ<i>σ</i> (kPa)')
        delta_sigma = st.number_input(
            "delta sigma hidden", min_value=0.1, value=300.0, step=10.0,
            label_visibility="collapsed", key="delta_sigma"
        )

        input_label('Loading frequency, <i>f</i> (mHz)')
        f_mhz = st.number_input(
            "frequency hidden", min_value=0.001, value=125.0, step=1.0, format="%.3f",
            label_visibility="collapsed", key="frequency"
        )

    with c3:
        st.markdown("### Design criterion")
        input_label('Design number of cycles, <i>i</i><sub>design</sub>')
        i_design_text = st.text_input(
            "design cycles hidden", value="1,000,000",
            label_visibility="collapsed", key="i_design_text"
        )
        try:
            i_design = int(float(i_design_text.replace(",", "").strip()))
            if i_design < 1:
                raise ValueError
        except ValueError:
            st.error("Enter a valid positive number of design cycles, e.g., 1,000,000.")
            i_design = 1_000_000

        input_label('Allowable settlement, <i>S</i><sub>allow</sub> (mm)')
        s_allow_mm = st.number_input(
            "allow settlement hidden", min_value=0.0, value=562.4, step=10.0, format="%.1f",
            label_visibility="collapsed", key="s_allow_mm"
        )

        input_label('Soil state')
        st.text_input(
            "soil state hidden", value="Normally consolidated clay (OCR = 1.0)",
            disabled=True, label_visibility="collapsed", key="soil_state"
        )

# -----------------------------------------------------------------------------
# Automatic design-stage calculations
# -----------------------------------------------------------------------------
sigma_ref = 1.0
gamma_sat = 19.0
gamma_w = 9.81
gamma_sub = gamma_sat - gamma_w
sigma_initial = max(gamma_sub * (h0 / 2.0), 1e-6)
e_initial = e0 - cc * np.log10(sigma_initial / sigma_ref)

stress_ratio = delta_sigma / sigma_v0
eb = e0 - cc * np.log10(sigma_v0 / sigma_ref)
e_static = e0 - cc * np.log10((sigma_v0 + delta_sigma) / sigma_ref)

h_b = h0 * (1.0 + eb) / (1.0 + e_initial)
h_peak = h0 * (1.0 + e_static) / (1.0 + e_initial)
s_static_mm = (h0 - h_peak) * 1000.0

delta_eT_design = predict_delta_eT_pysr(eb, stress_ratio)
e_t_design = e_static - delta_eT_design
m_design = 0.5
n_design = 177.7 * eb + 70.7 * stress_ratio + 46.59

design_assessment = assessment_from_parameters(
    h_b, eb, e_static, e_t_design, n_design, m_design,
    s_static_mm, i_design, f_mhz, s_allow_mm,
)

st.markdown("#### Automatically calculated design-state parameters")
r1, r2, r3, r4 = st.columns(4, gap="small")
r5, r6, r7 = st.columns(3, gap="small")
with r1:
    result_card('Baseline void ratio, <i>e</i><sub>b</sub>', f"{eb:.4f}")
with r2:
    result_card('Static void ratio, <i>e</i><sub>static</sub>', f"{e_static:.4f}")
with r3:
    result_card('Stress amplitude ratio, Δ<i>σ</i> / <i>σ</i>′<sub>v0</sub>', f"{stress_ratio:.3f}")
with r4:
    result_card('PySR prediction, Δ<i>e</i><sub>T</sub>', f"{delta_eT_design:.4f}")
with r5:
    result_card('Baseline layer thickness, <i>H</i><sub>b</sub>', f"{h_b:.4f} m")
with r6:
    result_card('Characteristic cycle number, <i>N</i>*', f"{n_design:,.0f}")
with r7:
    result_card('Curvature parameter, <i>m</i>', f"{m_design:.2f}")

st.caption(
    "The reference void ratio e₀ is defined at σ′v = 1 kPa, so eᵦ and e_static are independent of H₀. "
    "For layer-thickness and static-settlement conversion, the in-situ initial void ratio is evaluated internally "
    "at the mid-depth self-weight effective stress."
)

# -----------------------------------------------------------------------------
# 2. Design-stage prediction
# -----------------------------------------------------------------------------
st.markdown('<div id="design-response" class="section-anchor"></div>', unsafe_allow_html=True)
st.header("2. Design-Stage Long-Term Response Prediction")
left, right = st.columns(2, gap="large")
with left:
    st.subheader("2-1. Static Response")
    st.markdown('<div class="response-result">', unsafe_allow_html=True)
    result_card(
        'Static consolidation settlement, <i>S</i><sub>static</sub>',
        f'{s_static_mm:,.1f} mm',
        tone="blue",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.plotly_chart(
        static_response_figure(
            sigma_v0, delta_sigma, e0, eb, e_static, cc
        ),
        use_container_width=True,
    )

with right:
    st.subheader("2-2. Repetitive Response")
    st.markdown('<div class="response-result">', unsafe_allow_html=True)
    result_card(
        'Terminal repetitive settlement, Δ<i>S</i><sub>T</sub> (<i>i</i> = ∞)',
        f'{design_assessment["delta_ST_mm"]:,.1f} mm',
        tone="red",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.plotly_chart(
        design_void_ratio_figure(e_static, e_t_design, n_design, m_design, i_design),
        use_container_width=True,
    )

# -----------------------------------------------------------------------------
# 3. Design-stage assessment
# -----------------------------------------------------------------------------
st.markdown('<div id="design-assessment" class="section-anchor"></div>', unsafe_allow_html=True)
st.header("3. Design-Stage Settlement Assessment")
st.caption("Key design-stage results: how much, how fast, and serviceability.")
render_assessment_table(design_assessment)
if design_assessment["satisfied"]:
    st.markdown('<div class="status-good">✓ Design-life serviceability criterion is satisfied.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-bad">✕ Design-life serviceability criterion is not satisfied.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 02. MONITORING STAGE
# -----------------------------------------------------------------------------
stage_title("02", "MONITORING STAGE")
st.markdown('<div id="monitoring-input" class="section-anchor"></div>', unsafe_allow_html=True)
st.header("4. Monitoring Data Input")
if nav_request in {"5", "6"} and not monitoring_ready:
    st.warning("Monitoring data are required first. Please upload at least one dataset and run Monitoring Calibration to activate Sections 5 and 6.")
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
    st.session_state.pop("selected_monitoring_dataset", None)

fit_results = st.session_state.get("fit_results", [])
fit_errors = st.session_state.get("fit_errors", [])
for msg in fit_errors:
    st.warning(msg)

# -----------------------------------------------------------------------------
# 5. Monitoring-based updating
# -----------------------------------------------------------------------------
if fit_results:
    fit_results = sorted(fit_results, key=lambda x: x["imax"])
    dataset_ids = [int(r["dataset"]) for r in fit_results]
    selected_dataset = st.session_state.get("selected_monitoring_dataset")
    if selected_dataset not in dataset_ids:
        selected_dataset = dataset_ids[-1]
        st.session_state["selected_monitoring_dataset"] = selected_dataset

    st.markdown('<div id="monitoring-calibration" class="section-anchor"></div>', unsafe_allow_html=True)
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
        st.caption("Click any D-point to use that monitoring stage as the active update. The longest dataset is selected by default.")
        selection_event = st.plotly_chart(
            terminal_settlement_evolution_figure(
                fit_results,
                design_assessment["delta_ST_mm"],
                selected_dataset=selected_dataset,
            ),
            use_container_width=True,
            key="terminal_settlement_updating_chart",
            on_select="rerun",
            selection_mode="points",
        )

        clicked_dataset = None
        try:
            selected_points = selection_event.selection.points
        except AttributeError:
            selected_points = selection_event.get("selection", {}).get("points", []) if selection_event else []

        if selected_points:
            customdata = selected_points[0].get("customdata")
            if isinstance(customdata, (list, tuple)):
                customdata = customdata[0] if customdata else None
            try:
                clicked_dataset = int(customdata)
            except (TypeError, ValueError):
                clicked_dataset = None

        if clicked_dataset in dataset_ids and clicked_dataset != selected_dataset:
            st.session_state["selected_monitoring_dataset"] = clicked_dataset
            st.rerun()

    selected_dataset = st.session_state.get("selected_monitoring_dataset", dataset_ids[-1])
    selected = next(r for r in fit_results if int(r["dataset"]) == int(selected_dataset))
    selected_is_latest = int(selected_dataset) == dataset_ids[-1]
    selected_label = "Latest" if selected_is_latest else "Selected"

    st.markdown("#### 5-3. Monitoring Calibration Results")
    st.caption(
        f"Active monitoring stage: Data {selected_dataset} ({selected_label}), "
        f"i_max = {selected['imax']:,.0f} cycles."
    )
    rows = []
    for r in fit_results:
        active_tag = " <b>(Active)</b>" if int(r["dataset"]) == int(selected_dataset) else ""
        rows.append(
            f'<tr><td>Data {r["dataset"]}{active_tag}</td><td>{r["imax"]:,.0f}</td>'
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

    st.markdown('<div id="monitoring-assessment" class="section-anchor"></div>', unsafe_allow_html=True)
    st.header("6. Monitoring-Calibrated Settlement Assessment")
    st.caption(
        f"Assessment using Data {selected_dataset} ({selected_label}) calibrated parameters "
        f"up to i = {selected['imax']:,.0f} cycles."
    )
    calibrated = assessment_from_parameters(
        h_b, eb, e_static, selected["eT"], selected["Nstar"], selected["m"],
        s_static_mm, i_design, f_mhz, s_allow_mm,
    )
    render_assessment_table(design_assessment, calibrated)

    if calibrated["satisfied"]:
        st.markdown('<div class="status-good">✓ Monitoring-calibrated design-life serviceability criterion is satisfied.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-bad">✕ Monitoring-calibrated design-life serviceability criterion is not satisfied.</div>', unsafe_allow_html=True)

    st.header("Engineering Comments")
    design_dst = design_assessment["delta_ST_mm"]
    calib_dst = calibrated["delta_ST_mm"]
    change_pct = ((calib_dst - design_dst) / design_dst * 100.0) if abs(design_dst) > 1e-12 else np.nan
    stage_wording = "latest" if selected_is_latest else f"selected Data {selected_dataset}"

    if np.isfinite(change_pct) and change_pct > 5:
        comment1 = (
            f"The {stage_wording} monitoring-based terminal repetitive settlement is {calib_dst:.1f} mm, "
            f"{abs(change_pct):.1f}% larger than the design-stage estimate. The long-term repetitive "
            "settlement demand should therefore be updated using the monitoring-calibrated response."
        )
    elif np.isfinite(change_pct) and change_pct < -5:
        comment1 = (
            f"The {stage_wording} monitoring-based terminal repetitive settlement is {calib_dst:.1f} mm, "
            f"{abs(change_pct):.1f}% smaller than the design-stage estimate, indicating a lower long-term "
            "repetitive settlement demand than initially predicted."
        )
    else:
        comment1 = (
            f"The {stage_wording} monitoring-based terminal repetitive settlement ({calib_dst:.1f} mm) remains close "
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
        f"The active calibration uses monitoring Data {selected_dataset} up to <i>i</i> = {selected['imax']:,.0f} cycles and gives "
        f"<i>e</i><sub>T</sub> = {selected['eT']:.5f}, <i>N</i>* = {selected['Nstar']:.1f}, "
        f"<i>m</i> = {selected['m']:.4f}, and RMSE = {selected['RMSE']:.6f}. "
        "Graph 5-2 can be used interactively to compare the monitoring-updated prediction at different monitoring stages."
    )

    st.markdown(f'<div class="eng-comment"><b>1. Terminal response.</b> {comment1}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="eng-comment"><b>2. Serviceability.</b> {comment2}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="eng-comment"><b>3. Monitoring interpretation.</b> {comment3}</div>', unsafe_allow_html=True)
else:
    st.info("Upload at least one i-e dataset in Section 4 and click **Run Monitoring Calibration** to activate Sections 5 and 6.")

st.divider()
st.caption(
    "The reference void ratio e0 is defined at σ′v = 1 kPa. Baseline and static void ratios are calculated from the "
    "compression relation and are independent of H0. For thickness and settlement conversion, the in-situ initial void "
    "ratio is evaluated internally at the mid-depth self-weight effective stress. Terminal void ratio change is predicted "
    "using PySR Equation ID 3. Monitoring calibration uses each dataset's measured e1 at i = 1 and freely fits eT, N*, and m."
)
