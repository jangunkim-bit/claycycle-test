import numpy as np
import streamlit as st


def apply_style():
    st.markdown("""
    <style>
      :root {
        --navy:#16324F; --blue:#2E6F95; --muted:#667085; --line:#D9E2EC;
        --good:#1F7A5C; --bad:#B42318; --soft:#F8FAFC; --softblue:#EEF5F8;
        --red:#D94B4B; --green:#2F7D5A;
      }
      .block-container{max-width:1580px;padding-top:1.35rem;padding-bottom:4rem;}
      h1,h2,h3{color:var(--navy);letter-spacing:-0.02em;}
      h2{margin-top:1.45rem!important;}
      .hero{padding:1.2rem 1.45rem 1.05rem;border:1px solid var(--line);border-radius:18px;
            background:linear-gradient(135deg,#F8FAFC 0%,#EEF5F8 100%);margin-bottom:.72rem;text-align:center;}
      .hero-kicker{font-size:.78rem;line-height:1;font-weight:850;color:var(--blue);letter-spacing:.14em;
                   margin-bottom:.38rem;}
      .hero-title{font-size:clamp(1.7rem,2.65vw,2.35rem);line-height:1.12;font-weight:850;color:var(--navy);
                  margin-bottom:.32rem;letter-spacing:-0.03em;}
      .hero-subtitle{font-size:clamp(.98rem,1.35vw,1.12rem);font-weight:650;color:#526170;margin-bottom:.38rem;}
      .hero-sub{color:var(--muted);font-size:.92rem;}

      .workflow-shell{border:1px solid var(--line);border-radius:18px;background:#FFFFFF;padding:1rem 1rem .72rem;
                      margin-bottom:1.25rem;box-shadow:0 1px 3px rgba(16,24,40,.035);}
      .workflow-grid{display:grid;grid-template-columns:1fr 34px 1fr 34px 1fr 34px 1fr;gap:.45rem;align-items:stretch;}
      .flow-card{border:1px solid #E5EBF1;border-radius:14px;background:#FCFDFE;padding:.82rem .82rem .72rem;
                 min-height:205px;display:flex;flex-direction:column;justify-content:flex-start;}
      .flow-number{font-size:.72rem;font-weight:850;color:var(--blue);letter-spacing:.08em;text-transform:uppercase;margin-bottom:.18rem;}
      .flow-title{font-size:.94rem;font-weight:800;color:var(--navy);line-height:1.2;min-height:2.35rem;}
      .flow-caption{font-size:.78rem;line-height:1.35;color:var(--muted);margin-top:.36rem;}
      .flow-arrow{display:flex;align-items:center;justify-content:center;color:var(--navy);font-size:1.8rem;font-weight:800;}

      .soil-visual{position:relative;height:82px;margin:.58rem .18rem .12rem;}
      .soil-load{position:absolute;left:50%;top:0;transform:translateX(-50%);font-size:1.55rem;color:var(--red);font-weight:800;line-height:1;}
      .soil-dsigma{position:absolute;left:calc(50% + 29px);top:6px;color:var(--red);font-size:.78rem;font-weight:750;}
      .soil-slab{position:absolute;left:22%;right:22%;top:31px;height:10px;background:#8795A5;border-radius:2px;}
      .soil-layer{position:absolute;left:8%;right:8%;top:42px;height:38px;border-radius:4px 4px 7px 7px;
                  background:linear-gradient(180deg,#E8D5B9,#D8B994);border:1px solid #C7A77F;display:flex;
                  align-items:center;justify-content:center;color:#5C4A35;font-size:.68rem;font-weight:750;text-align:center;}

      .mini-chart{height:88px;margin:.42rem .08rem .05rem;border-left:1px solid #8996A5;border-bottom:1px solid #8996A5;position:relative;}
      .mini-chart svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible;}
      .axis-e{position:absolute;left:-14px;top:-7px;font-size:.68rem;font-style:italic;color:#344054;}
      .axis-i{position:absolute;right:-2px;bottom:-18px;font-size:.68rem;font-style:italic;color:#344054;}
      .curve-label-top{position:absolute;left:3px;top:2px;font-size:.64rem;color:#667085;}
      .curve-label-bottom{position:absolute;left:3px;bottom:4px;font-size:.64rem;color:#667085;}
      .nstar-label{position:absolute;left:57%;bottom:-18px;font-size:.64rem;color:#344054;}

      .settlement-box{margin:.55rem .04rem .08rem;border:1px solid #D7E2EC;border-radius:11px;background:#F7FAFC;padding:.62rem .45rem;text-align:center;}
      .settlement-row{display:flex;align-items:center;justify-content:center;gap:.35rem;flex-wrap:wrap;}
      .s-chip{border:1px solid #A8C6DE;background:#F1F7FB;border-radius:8px;padding:.28rem .5rem;color:var(--navy);font-weight:780;font-size:.8rem;}
      .s-chip.red{border-color:#E7B3B3;background:#FFF5F5;color:#B93838;}
      .s-total{display:inline-block;margin-top:.44rem;background:var(--navy);color:#fff;border-radius:8px;padding:.3rem .75rem;font-weight:780;font-size:.8rem;}
      .question-line{font-size:.7rem;color:#485768;margin-top:.34rem;line-height:1.35;}

      .update-pill{margin:.5rem .03rem 0;border:1px solid #AFCFBE;border-radius:9px;background:#F1FAF5;color:#256645;
                   padding:.4rem .52rem;text-align:center;font-size:.74rem;font-weight:760;}
      .workflow-feedback{margin-top:.72rem;border-top:1px solid #E7EDF3;padding-top:.58rem;text-align:center;
                         color:var(--blue);font-size:.8rem;font-weight:680;letter-spacing:.005em;}
      .workflow-feedback span{color:var(--muted);font-weight:520;margin-left:.25rem;}

      @media (max-width:1100px){
        .workflow-grid{grid-template-columns:1fr 26px 1fr;}
        .workflow-grid .flow-card:nth-of-type(3){grid-column:1;}
        .workflow-grid .flow-card:nth-of-type(4){grid-column:3;}
        .workflow-grid .flow-arrow:nth-of-type(6){display:none;}
      }
      @media (max-width:720px){
        .workflow-grid{display:block;}
        .flow-card{min-height:auto;margin-bottom:.55rem;}
        .flow-arrow{transform:rotate(90deg);height:24px;font-size:1.35rem;}
        .hero{padding:1rem .9rem .9rem;text-align:left;}
      }

      .stage-title{display:block;width:100%;padding:.58rem .8rem;margin:1.15rem 0 .35rem;
                   border-left:5px solid var(--blue);background:#F3F7FA;border-radius:8px;
                   color:var(--navy);font-size:1.16rem;font-weight:850;letter-spacing:.035em;}
      .input-label{min-height:2.25rem;display:flex;align-items:flex-end;color:#344054;
                   font-size:.91rem;font-weight:500;line-height:1.28;margin:.12rem 0 .28rem;}
      .result-card{border:1px solid var(--line);border-radius:12px;background:#FFFFFF;padding:.72rem .9rem;
                   min-height:78px;display:flex;flex-direction:column;justify-content:center;box-shadow:0 1px 2px rgba(16,24,40,.025);}
      .result-label{font-size:.84rem;color:var(--muted);margin-bottom:.18rem;}
      .result-value{font-size:1.22rem;color:var(--navy);font-weight:780;letter-spacing:-0.01em;}
      .status-good{background:#ECFDF3;color:var(--good);border:1px solid #ABEFC6;border-radius:12px;
                   padding:.8rem 1rem;font-weight:700;}
      .status-bad{background:#FEF3F2;color:var(--bad);border:1px solid #FECDCA;border-radius:12px;
                  padding:.8rem 1rem;font-weight:700;}
      .eng-comment{border-left:4px solid var(--blue);background:#F8FAFC;border-radius:10px;
                   padding:.9rem 1.05rem;margin-bottom:.7rem;color:#1F2937;}
      div[data-testid="stMetric"]{border:1px solid var(--line);border-radius:12px;padding:.72rem .85rem;background:#FFF;}
      div[data-testid="stFileUploader"]{border:1px solid var(--line);border-radius:12px;padding:.55rem;background:#FBFCFD;}
      div[data-testid="stNumberInput"], div[data-testid="stTextInput"]{margin-bottom:.15rem;}
      .stButton>button{border-radius:10px;font-weight:700;}
      .assessment-wrap{width:100%;overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:#fff;}
      table.assessment{width:100%;border-collapse:collapse;font-size:.91rem;}
      table.assessment th{background:#F1F5F9;color:#344054;font-weight:700;padding:.72rem .75rem;
                          border-bottom:1px solid var(--line);text-align:left;white-space:nowrap;}
      table.assessment td{padding:.68rem .75rem;border-bottom:1px solid #E7EDF3;vertical-align:middle;}
      table.assessment tr:last-child td{border-bottom:none;}
      td.category{font-weight:760;color:var(--navy);background:#F8FAFC;width:120px;text-align:center;}
      td.symbol{white-space:nowrap;color:#344054;}
      td.result{white-space:nowrap;font-weight:650;color:#101828;}
      .graph-result{margin-top:-.35rem;margin-bottom:.6rem;}
    </style>
    """, unsafe_allow_html=True)


def hero():
    st.markdown("""
    <div class="hero">
      <div class="hero-kicker">CLAYCYCLE</div>
      <div class="hero-title">Long-Term Settlement Assessment</div>
      <div class="hero-subtitle">Normally Consolidated Clays under Repetitive Loading</div>
      <div class="hero-sub">Design-stage prediction, serviceability assessment, and monitoring-based calibration in one workflow.</div>
    </div>

    <div class="workflow-shell">
      <div class="workflow-grid">
        <div class="flow-card">
          <div class="flow-number">01 · Loading</div>
          <div class="flow-title">Repetitive Loading on Soft Clay</div>
          <div class="soil-visual">
            <div class="soil-load">↕</div>
            <div class="soil-dsigma">Δσ</div>
            <div class="soil-slab"></div>
            <div class="soil-layer">Normally consolidated clay</div>
          </div>
          <div class="flow-caption">Define the ground condition and repetitive loading condition.</div>
        </div>

        <div class="flow-arrow">→</div>

        <div class="flow-card">
          <div class="flow-number">02 · Prediction</div>
          <div class="flow-title">Long-Term Repetitive Response</div>
          <div class="mini-chart">
            <span class="axis-e">e</span><span class="axis-i">i</span>
            <span class="curve-label-top">e<sub>static</sub></span><span class="curve-label-bottom">e<sub>T</sub></span>
            <span class="nstar-label">N*</span>
            <svg viewBox="0 0 220 88" preserveAspectRatio="none" aria-hidden="true">
              <line x1="0" y1="72" x2="220" y2="72" stroke="#D9A0A0" stroke-width="1" stroke-dasharray="4,4" />
              <path d="M12,15 C34,40 57,52 84,59 C116,67 151,70 210,72" fill="none" stroke="#D94B4B" stroke-width="2.2" />
              <line x1="128" y1="47" x2="128" y2="88" stroke="#9AA7B5" stroke-width="1" stroke-dasharray="3,3" />
            </svg>
          </div>
          <div class="flow-caption">Predict terminal response and accumulation rate using <i>e</i><sub>T</sub>, <i>N</i>*, and <i>m</i>.</div>
        </div>

        <div class="flow-arrow">→</div>

        <div class="flow-card">
          <div class="flow-number">03 · Assessment</div>
          <div class="flow-title">Settlement Assessment</div>
          <div class="settlement-box">
            <div class="settlement-row">
              <span class="s-chip"><i>S</i><sub>static</sub></span>
              <strong>+</strong>
              <span class="s-chip red">Δ<i>S</i><sub>T</sub></span>
            </div>
            <div class="s-total"><i>S</i><sub>total</sub></div>
            <div class="question-line">How much settlement?<br>How fast does it accumulate?</div>
          </div>
          <div class="flow-caption">Evaluate design-life settlement and the allowable-settlement criterion.</div>
        </div>

        <div class="flow-arrow">→</div>

        <div class="flow-card">
          <div class="flow-number">04 · Updating</div>
          <div class="flow-title">Monitoring-Based Update</div>
          <div class="mini-chart">
            <span class="axis-e">e</span><span class="axis-i">i</span>
            <svg viewBox="0 0 220 88" preserveAspectRatio="none" aria-hidden="true">
              <path d="M12,16 C35,33 58,47 88,57 C121,67 160,72 210,76" fill="none" stroke="#2E6F95" stroke-width="2.1" />
              <circle cx="14" cy="17" r="3.6" fill="#2E6F95"/><circle cx="37" cy="34" r="3.6" fill="#2E6F95"/>
              <circle cx="61" cy="47" r="3.6" fill="#2E6F95"/><circle cx="91" cy="58" r="3.6" fill="#2E6F95"/>
              <circle cx="124" cy="67" r="3.6" fill="#2E6F95"/><circle cx="164" cy="72" r="3.6" fill="#2E6F95"/>
              <circle cx="208" cy="76" r="3.6" fill="#2E6F95"/>
            </svg>
          </div>
          <div class="update-pill">Update <i>e</i><sub>T</sub>, <i>N</i>*, <i>m</i> · Model calibration</div>
          <div class="flow-caption">Use measured <i>i</i>–<i>e</i> data to refine the long-term prediction.</div>
        </div>
      </div>
      <div class="workflow-feedback">DESIGN → PREDICT → ASSESS → UPDATE <span>Monitoring feedback refines the long-term settlement prediction.</span></div>
    </div>
    """, unsafe_allow_html=True)


def stage_title(number, text):
    roman = {"01": "I", "02": "II"}.get(str(number), str(number))
    st.markdown(f'<div class="stage-title">{roman} · {text}</div>', unsafe_allow_html=True)


def input_label(html):
    st.markdown(f'<div class="input-label">{html}</div>', unsafe_allow_html=True)


def result_card(label_html, value_text):
    st.markdown(
        f'<div class="result-card"><div class="result-label">{label_html}</div>'
        f'<div class="result-value">{value_text}</div></div>',
        unsafe_allow_html=True,
    )


def _fmt_cycles(x):
    return "—" if not np.isfinite(x) else f"{x:,.0f} cycles"


def _assessment_rows(a):
    status = "Satisfied" if a["satisfied"] else "Not satisfied"
    return [
        ("How much", "Static consolidation settlement", "<i>S</i><sub>static</sub>", f'{a["Sstatic_mm"]:,.1f} mm'),
        ("How much", "Terminal repetitive settlement", "Δ<i>S</i><sub>T</sub> (<i>i</i> = ∞)", f'{a["delta_ST_mm"]:,.1f} mm'),
        ("How much", "Terminal total settlement", "<i>S</i><sub>T(total)</sub>", f'{a["ST_total_mm"]:,.1f} mm'),
        ("How much", "Design-life total settlement", "<i>S</i><sub>design(total)</sub>", f'{a["Sdesign_total_mm"]:,.1f} mm'),
        ("How fast", "50% accumulation", "<i>i</i><sub>R=0.5</sub>, <i>t</i><sub>R=0.5</sub>", f'{_fmt_cycles(a["i50"])}, {a["t50"]}'),
        ("How fast", "90% accumulation", "<i>i</i><sub>R=0.9</sub>, <i>t</i><sub>R=0.9</sub>", f'{_fmt_cycles(a["i90"])}, {a["t90"]}'),
        ("Serviceability", "Allowable settlement", "<i>S</i><sub>allow</sub>", f'{a["Sallow_mm"]:,.1f} mm'),
        ("Serviceability", "Allowable-settlement reach", "<i>i</i><sub>allow</sub>, <i>t</i><sub>allow</sub>", f'{a["iallow_text"]}, {a["tallow"]}'),
        ("Serviceability", "Design-life assessment", "<i>S</i><sub>design(total)</sub> ≤ <i>S</i><sub>allow</sub>", status),
        ("Serviceability", "Exceedance at design life", "<i>S</i><sub>design</sub> − <i>S</i><sub>allow</sub>", f'{a["exceedance_mm"]:,.1f} mm'),
    ]


def render_assessment_table(design, calibrated=None):
    design_rows = _assessment_rows(design)
    calibrated_rows = _assessment_rows(calibrated) if calibrated is not None else None
    counts = {"How much": 4, "How fast": 2, "Serviceability": 4}
    seen = set()

    if calibrated is None:
        head = "<tr><th>Category</th><th>Evaluation</th><th>Symbol</th><th>Result</th></tr>"
    else:
        head = "<tr><th>Category</th><th>Evaluation</th><th>Symbol</th><th>Design-stage</th><th>Monitoring-calibrated</th></tr>"

    body = []
    for idx, row in enumerate(design_rows):
        category, evaluation, symbol, design_result = row
        cells = []
        if category not in seen:
            cells.append(f'<td class="category" rowspan="{counts[category]}">{category}</td>')
            seen.add(category)
        cells.append(f"<td>{evaluation}</td>")
        cells.append(f'<td class="symbol">{symbol}</td>')
        cells.append(f'<td class="result">{design_result}</td>')
        if calibrated_rows is not None:
            cells.append(f'<td class="result">{calibrated_rows[idx][3]}</td>')
        body.append("<tr>" + "".join(cells) + "</tr>")

    html = '<div class="assessment-wrap"><table class="assessment"><thead>' + head + "</thead><tbody>" + "".join(body) + "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)
