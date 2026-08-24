import numpy as np
import streamlit as st


def apply_style():
    st.markdown("""
    <style>
      :root {
        --navy:#16324F; --blue:#2E6F95; --muted:#667085; --line:#D9E2EC;
        --good:#1F7A5C; --bad:#B42318; --soft:#F8FAFC; --softblue:#EEF5F8;
      }
      .block-container{max-width:1580px;padding-top:2.25rem;padding-bottom:4rem;}
      h1,h2,h3{color:var(--navy);letter-spacing:-0.02em;}
      h2{margin-top:1.45rem!important;}
      .hero{padding:1.35rem 1.45rem 1.05rem;border:1px solid var(--line);border-radius:18px;
            background:linear-gradient(135deg,#F8FAFC 0%,#EEF5F8 100%);margin-bottom:.72rem;text-align:center;}
      .hero-kicker{font-size:.78rem;line-height:1.2;font-weight:850;color:var(--blue);letter-spacing:.15em;margin-bottom:.42rem;}
      .hero-title{font-size:clamp(1.7rem,2.65vw,2.35rem);line-height:1.12;font-weight:850;color:var(--navy);
                  margin-bottom:.32rem;letter-spacing:-0.03em;}
      .hero-subtitle{font-size:clamp(.98rem,1.35vw,1.12rem);font-weight:650;color:#526170;margin-bottom:.38rem;}
      .hero-sub{color:var(--muted);font-size:.92rem;}
      div[data-testid="stImage"]{margin:.08rem 0 .7rem;}
      div[data-testid="stImage"] img{border-radius:18px;box-shadow:0 6px 20px rgba(16,24,40,.055);}

      .overview-stage{border-radius:16px;padding:.72rem .78rem .82rem;margin:.55rem 0 .7rem;}
      .overview-stage.design{background:linear-gradient(90deg,#F6FAFF 0%,#EDF5FF 100%);border:1px solid #D8E7FA;}
      .overview-stage.monitor{background:linear-gradient(90deg,#F5FBF6 0%,#EDF7EF 100%);border:1px solid #D6E8DA;}
      .overview-head{display:flex;align-items:center;gap:.72rem;margin:0 .25rem .62rem;}
      .overview-badge{width:42px;height:42px;border-radius:9px;display:flex;align-items:center;justify-content:center;
                      color:white;font-size:1.08rem;font-weight:850;box-shadow:0 2px 6px rgba(16,24,40,.09);}
      .design .overview-badge{background:#0B2E6D;}.monitor .overview-badge{background:#0B5A2B;}
      .overview-stage-title{font-size:1.12rem;font-weight:850;letter-spacing:.015em;}
      .design .overview-stage-title{color:#0B2E6D;}.monitor .overview-stage-title{color:#0B5A2B;}
      .overview-stage-sub{font-size:.9rem;color:#344054;margin-left:.25rem;}
      .overview-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.72rem;}
      .overview-link{display:block;text-decoration:none!important;color:inherit!important;}
      .overview-card{min-height:116px;background:#FFFFFF;border:1px solid #D7E1EC;border-radius:13px;
                     padding:.8rem .86rem;display:grid;grid-template-columns:54px 1fr 18px;gap:.65rem;align-items:center;
                     box-shadow:0 2px 7px rgba(16,24,40,.035);height:100%;transition:transform .12s ease,box-shadow .12s ease,border-color .12s ease;}
      .overview-link:hover .overview-card{transform:translateY(-2px);box-shadow:0 7px 16px rgba(16,24,40,.08);}
      .design .overview-link:hover .overview-card{border-color:#9BBCE8;}
      .monitor .overview-link:hover .overview-card{border-color:#9BC5A5;}
      .monitor .overview-card{border-color:#D5E4D8;}
      .overview-icon{width:50px;height:50px;border-radius:50%;display:flex;align-items:center;justify-content:center;
                     font-size:1.55rem;font-weight:650;line-height:1;}
      .design .overview-icon{background:#EEF5FF;color:#0B2E6D;}.monitor .overview-icon{background:#ECF7EE;color:#0B5A2B;}
      .overview-card-title{font-size:.94rem;line-height:1.25;font-weight:800;margin-bottom:.28rem;}
      .design .overview-card-title{color:#0B2E6D;}.monitor .overview-card-title{color:#0B5A2B;}
      .overview-card-text{font-size:.79rem;line-height:1.4;color:#344054;}
      .overview-chevron{font-size:1.55rem;font-weight:500;line-height:1;}
      .design .overview-chevron{color:#0B2E6D;}.monitor .overview-chevron{color:#0B5A2B;}

      .stage-title{display:block;width:100%;padding:.58rem .8rem;margin:1.15rem 0 .35rem;
                   border-left:5px solid var(--blue);background:#F3F7FA;border-radius:8px;
                   color:var(--navy);font-size:1.16rem;font-weight:850;letter-spacing:.035em;}
      .input-label{min-height:2.25rem;display:flex;align-items:flex-end;color:#344054;
                   font-size:.91rem;font-weight:500;line-height:1.28;margin:.12rem 0 .28rem;}

      div[data-testid="stNumberInput"] div[data-baseweb="input"],
      div[data-testid="stTextInput"] div[data-baseweb="input"]{background:#FFF7D6!important;border-color:#E7D58A!important;}
      div[data-testid="stNumberInput"] input,
      div[data-testid="stTextInput"] input{background:transparent!important;}
      div[data-testid="stTextInput"] div[data-baseweb="input"]:has(input:disabled){background:#F0F2F6!important;border-color:#E1E5EB!important;}

      .result-card{border:1px solid var(--line);border-radius:12px;background:#FFFFFF;padding:.72rem .9rem;
                   min-height:78px;display:flex;flex-direction:column;justify-content:center;box-shadow:0 1px 2px rgba(16,24,40,.025);}
      .result-label{font-size:.84rem;color:var(--muted);margin-bottom:.18rem;}
      .result-value{font-size:1.22rem;color:var(--navy);font-weight:780;letter-spacing:-0.01em;}
      .result-card.result-blue{border-color:#BFD6FA;background:#F8FBFF;}
      .result-card.result-blue .result-label,.result-card.result-blue .result-value{color:#2563EB;}
      .result-card.result-red{border-color:#F7C2C0;background:#FFF9F8;}
      .result-card.result-red .result-label,.result-card.result-red .result-value{color:#E54848;}
      .response-result{margin:.1rem 0 .55rem;}
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
      .section-anchor{position:relative;top:-1rem;visibility:hidden;}
      @media (max-width:920px){
        .overview-grid{grid-template-columns:1fr;}
        .overview-card{min-height:96px;}
        .overview-stage-sub{display:none;}
      }
      @media (max-width:720px){
        .block-container{padding-top:2rem;}
        .hero{text-align:left;padding:1.2rem .95rem .95rem;}
        div[data-testid="stImage"] img{border-radius:12px;}
        .overview-head{gap:.55rem;}.overview-stage{padding:.65rem;}
        .overview-card{grid-template-columns:46px 1fr 14px;padding:.72rem;}
        .overview-icon{width:44px;height:44px;font-size:1.35rem;}
      }
    </style>
    """, unsafe_allow_html=True)


def hero(monitoring_ready=False):
    st.markdown("""
    <div class="hero">
      <div class="hero-kicker">CLAY CYCLE</div>
      <div class="hero-title">Long-Term Settlement Assessment</div>
      <div class="hero-subtitle">Normally Consolidated Clays under Repetitive Loading</div>
      <div class="hero-sub">Design-stage prediction, serviceability assessment, and monitoring-based calibration in one workflow.</div>
    </div>
    """, unsafe_allow_html=True)
    st.image("assets/claycycle_overview.svg", use_container_width=True)
    st.markdown("""
    <div class="overview-stage design">
      <div class="overview-head">
        <div class="overview-badge">I</div>
        <div class="overview-stage-title">DESIGN STAGE</div>
        <div class="overview-stage-sub">Predict long-term settlement before construction</div>
      </div>
      <div class="overview-grid">
        <a class="overview-link" href="#design-input"><div class="overview-card">
          <div class="overview-icon">▤</div>
          <div><div class="overview-card-title">1. Design Input Parameters</div><div class="overview-card-text">Soil and loading conditions for design-stage prediction.</div></div>
          <div class="overview-chevron">›</div>
        </div></a>
        <a class="overview-link" href="#design-response"><div class="overview-card">
          <div class="overview-icon">↗</div>
          <div><div class="overview-card-title">2. Design-Stage Long-Term Response Prediction</div><div class="overview-card-text">Predict <i>e</i><sub>T</sub>, <i>N</i>*, <i>m</i> and <i>e</i>–<i>i</i> (or settlement) behavior under repetitive loading.</div></div>
          <div class="overview-chevron">›</div>
        </div></a>
        <a class="overview-link" href="#design-assessment"><div class="overview-card">
          <div class="overview-icon">✓</div>
          <div><div class="overview-card-title">3. Design-Stage Settlement Assessment</div><div class="overview-card-text">Evaluate static settlement, additional settlement and serviceability.</div></div>
          <div class="overview-chevron">›</div>
        </div></a>
      </div>
    </div>
    <div class="overview-stage monitor">
      <div class="overview-head">
        <div class="overview-badge">II</div>
        <div class="overview-stage-title">MONITORING STAGE</div>
        <div class="overview-stage-sub">Update prediction using monitoring data</div>
      </div>
      <div class="overview-grid">
        <a class="overview-link" href="#monitoring-input"><div class="overview-card">
          <div class="overview-icon">⇧</div>
          <div><div class="overview-card-title">4. Monitoring Data Input</div><div class="overview-card-text">Input monitored <i>i</i>–<i>e</i> data during construction or operation.</div></div>
          <div class="overview-chevron">›</div>
        </div></a>
        <a class="overview-link" href="#monitoring-calibration"><div class="overview-card">
          <div class="overview-icon">⚙</div>
          <div><div class="overview-card-title">5. Monitoring-Based Calibration of Model Parameters</div><div class="overview-card-text">Calibrate <i>e</i><sub>T</sub>, <i>N</i>*, <i>m</i> using monitoring data (Model Calibration).</div></div>
          <div class="overview-chevron">›</div>
        </div></a>
        <a class="overview-link" href="#monitoring-assessment"><div class="overview-card">
          <div class="overview-icon">✓</div>
          <div><div class="overview-card-title">6. Monitoring-Calibrated Settlement Assessment</div><div class="overview-card-text">Re-evaluate settlement and serviceability with updated parameters.</div></div>
          <div class="overview-chevron">›</div>
        </div></a>
      </div>
    </div>
    """, unsafe_allow_html=True)


def stage_title(number, text):
    roman = {"01": "I", "02": "II"}.get(str(number), str(number))
    st.markdown(f'<div class="stage-title">{roman} · {text}</div>', unsafe_allow_html=True)


def input_label(html):
    st.markdown(f'<div class="input-label">{html}</div>', unsafe_allow_html=True)


def result_card(label_html, value_text, tone=None):
    tone_class = f" result-{tone}" if tone in {"blue", "red"} else ""
    st.markdown(
        f'<div class="result-card{tone_class}"><div class="result-label">{label_html}</div>'
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
