import streamlit as st


ASSESSMENT_URL = "https://claycycle-test-yuzvjhrnacpcq85po2juns.streamlit.app"

st.set_page_config(
    page_title="ClayCycle | Long-Term Settlement Assessment",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #f6f8fb;
        color: #17324d;
    }
    .block-container {
        max-width: 1180px;
        padding-top: 2.0rem;
        padding-bottom: 3rem;
    }
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    .hero {
        background: linear-gradient(135deg, #ffffff 0%, #f5f8fc 63%, #eef4fb 100%);
        border: 1px solid #d8e2ec;
        border-radius: 22px;
        padding: 34px 38px 30px 38px;
        box-shadow: 0 12px 34px rgba(20, 50, 80, 0.08);
        margin-bottom: 18px;
    }
    .brand {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        color: #2563eb;
        background: #edf4ff;
        border: 1px solid #cfe0ff;
        border-radius: 999px;
        padding: 7px 12px;
        margin-bottom: 14px;
    }
    .hero h1 {
        margin: 0;
        color: #16324f;
        font-size: clamp(2.2rem, 4.2vw, 4.0rem);
        line-height: 1.02;
        letter-spacing: -0.035em;
    }
    .subtitle {
        margin-top: 12px;
        font-size: 1.16rem;
        color: #536579;
        font-weight: 500;
    }
    .one-line {
        margin-top: 13px;
        color: #738196;
        font-size: 0.98rem;
        max-width: 850px;
        line-height: 1.55;
    }
    .flow-wrap {
        margin-top: 28px;
        display: grid;
        grid-template-columns: 1fr 34px 1fr 34px 1fr 34px 1fr;
        align-items: stretch;
        gap: 9px;
    }
    .flow-card {
        min-height: 150px;
        border-radius: 16px;
        border: 1px solid #dbe4ee;
        padding: 17px 16px 15px 16px;
        background: #ffffff;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .flow-card.red {
        border-color: #f4c9c5;
        background: #fff9f8;
    }
    .flow-card.blue {
        border-color: #cdddfb;
        background: #f8fbff;
    }
    .kicker {
        font-size: 0.71rem;
        font-weight: 800;
        letter-spacing: 0.11em;
        color: #718096;
        text-transform: uppercase;
    }
    .flow-title {
        margin-top: 6px;
        font-size: 1.02rem;
        font-weight: 800;
        color: #16324f;
    }
    .flow-small {
        margin-top: 7px;
        color: #66778b;
        font-size: 0.80rem;
        line-height: 1.38;
    }
    .arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        color: #8ea0b4;
        font-size: 1.55rem;
        font-weight: 600;
    }
    .soil-icon {
        margin-top: 10px;
        position: relative;
        height: 48px;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #d4dde7;
        background:
            linear-gradient(to bottom,
                #dbeafe 0 19%,
                #d7c2a4 19% 39%,
                #c8ae89 39% 59%,
                #bfa077 59% 79%,
                #af8e66 79% 100%);
    }
    .load-arrow {
        text-align: center;
        color: #e24a4a;
        font-weight: 800;
        margin-top: -2px;
        font-size: 0.83rem;
    }
    .curve-box {
        margin-top: 7px;
        height: 61px;
        border-left: 1px solid #9eacba;
        border-bottom: 1px solid #9eacba;
        position: relative;
    }
    .curve-line {
        position: absolute;
        left: 8%;
        right: 5%;
        top: 11px;
        height: 37px;
        border-bottom: 3px solid #e24a4a;
        border-radius: 0 0 75% 0;
        transform: skewY(11deg);
    }
    .terminal {
        position: absolute;
        right: 4%;
        bottom: 7px;
        color: #e24a4a;
        font-size: 0.72rem;
        font-weight: 800;
    }
    .metric {
        margin-top: 11px;
        font-size: 1.38rem;
        font-weight: 900;
        color: #16324f;
    }
    .monitor-lines {
        margin-top: 10px;
        display: flex;
        gap: 4px;
        align-items: end;
        height: 48px;
    }
    .monitor-lines span {
        flex: 1;
        display: block;
        background: #2563eb;
        border-radius: 3px 3px 0 0;
        opacity: 0.88;
    }
    .monitor-lines span:nth-child(1){height:18px;opacity:.32}
    .monitor-lines span:nth-child(2){height:28px;opacity:.45}
    .monitor-lines span:nth-child(3){height:35px;opacity:.58}
    .monitor-lines span:nth-child(4){height:40px;opacity:.72}
    .monitor-lines span:nth-child(5){height:42px;opacity:.88}
    .stage-row {
        margin-top: 19px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
    }
    .stage {
        border-radius: 14px;
        padding: 13px 17px;
        font-size: 0.88rem;
        line-height: 1.45;
    }
    .stage.design {
        background: #fff4f2;
        border: 1px solid #f3c3be;
        color: #8d3730;
    }
    .stage.monitor {
        background: #f1f6ff;
        border: 1px solid #c8dafb;
        color: #285493;
    }
    .stage b {
        display: block;
        font-size: 0.77rem;
        letter-spacing: .08em;
        margin-bottom: 3px;
    }
    .tagline {
        text-align: center;
        margin: 24px 0 4px 0;
        font-size: 1.08rem;
        font-weight: 800;
        color: #16324f;
    }
    .tagline span { color: #2563eb; }
    .section-card {
        background: white;
        border: 1px solid #dde5ed;
        border-radius: 18px;
        padding: 24px 27px;
        margin-top: 16px;
    }
    .section-card h3 {
        margin-top: 0;
        color: #16324f;
    }
    .section-card p {
        color: #66778b;
        line-height: 1.65;
        margin-bottom: 0;
    }
    .feature-grid {
        display:grid;
        grid-template-columns: repeat(3,1fr);
        gap:12px;
        margin-top:14px;
    }
    .feature {
        border:1px solid #e0e7ef;
        border-radius:13px;
        padding:16px;
        background:#fbfcfe;
    }
    .feature b { color:#16324f; }
    .feature div { color:#748397;font-size:.86rem;margin-top:4px;line-height:1.45; }
    div.stLinkButton > a {
        width: 100%;
        min-height: 52px;
        border-radius: 12px;
        background: #16324f;
        color: white !important;
        border: 1px solid #16324f;
        font-weight: 800;
        font-size: 1rem;
    }
    div.stLinkButton > a:hover {
        background: #214768;
        border-color: #214768;
    }
    @media (max-width: 850px) {
        .flow-wrap { grid-template-columns: 1fr; }
        .arrow { transform: rotate(90deg); min-height: 18px; }
        .stage-row, .feature-grid { grid-template-columns: 1fr; }
        .hero { padding: 26px 20px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="brand">CLAYCYCLE</div>
        <h1>Long-Term Settlement Assessment</h1>
        <div class="subtitle">Normally Consolidated Clays under Repetitive Loading</div>
        <div class="one-line">
            A research-based engineering tool for design-stage prediction of long-term settlement and
            monitoring-based updating using measured repetitive-loading response.
        </div>

        <div class="flow-wrap">
            <div class="flow-card blue">
                <div>
                    <div class="kicker">01 · Design</div>
                    <div class="flow-title">Ground + Loading</div>
                    <div class="flow-small">Clay state, stress condition, loading frequency, and design criterion.</div>
                </div>
                <div>
                    <div class="load-arrow">↓ Δσ &nbsp;&nbsp; ↑</div>
                    <div class="soil-icon"></div>
                </div>
            </div>
            <div class="arrow">→</div>
            <div class="flow-card red">
                <div>
                    <div class="kicker">Predict</div>
                    <div class="flow-title">Long-Term e–i Response</div>
                    <div class="flow-small">Terminal state and cycle-dependent accumulation.</div>
                </div>
                <div class="curve-box"><div class="curve-line"></div><div class="terminal">e<sub>T</sub></div></div>
            </div>
            <div class="arrow">→</div>
            <div class="flow-card red">
                <div>
                    <div class="kicker">Assess</div>
                    <div class="flow-title">Settlement & Serviceability</div>
                    <div class="flow-small">Evaluate how much settlement occurs and how fast it accumulates.</div>
                </div>
                <div class="metric">S<sub>static</sub> + ΔS<sub>T</sub></div>
            </div>
            <div class="arrow">→</div>
            <div class="flow-card blue">
                <div>
                    <div class="kicker">02 · Monitoring</div>
                    <div class="flow-title">Calibrate + Update</div>
                    <div class="flow-small">Use measured i–e data to update e<sub>T</sub>, N*, m, and settlement prediction.</div>
                </div>
                <div class="monitor-lines"><span></span><span></span><span></span><span></span><span></span></div>
            </div>
        </div>

        <div class="stage-row">
            <div class="stage design"><b>DESIGN STAGE</b>Predict terminal response, accumulation rate, design-life settlement, and serviceability.</div>
            <div class="stage monitor"><b>MONITORING STAGE</b>Calibrate the response with field/laboratory i–e data and update the long-term assessment.</div>
        </div>
        <div class="tagline">Predict <span>how much</span>, <span>how fast</span>, and update with monitoring.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.link_button("Open Assessment Tool", ASSESSMENT_URL, use_container_width=True)

st.markdown(
    """
    <div class="section-card">
        <h3>What this tool does</h3>
        <div class="feature-grid">
            <div class="feature"><b>Design-stage prediction</b><div>Evaluates static settlement, terminal repetitive settlement, and design-life total settlement.</div></div>
            <div class="feature"><b>Accumulation assessment</b><div>Quantifies characteristic cycle number, accumulation rate, and allowable-settlement reach.</div></div>
            <div class="feature"><b>Monitoring-based updating</b><div>Calibrates long-term repetitive response from uploaded i–e monitoring datasets.</div></div>
        </div>
    </div>

    <div class="section-card">
        <h3>Research basis</h3>
        <p>
            ClayCycle implements the long-term settlement assessment framework developed for normally consolidated
            clays subjected to repetitive loading. The web tool is intended to provide a transparent and reproducible
            workflow linking design-stage prediction with monitoring-based calibration.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
