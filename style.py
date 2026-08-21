import streamlit as st


def apply_style():
    st.markdown("""
    <style>
      :root {--navy:#16324F;--blue:#2E6F95;--muted:#667085;--line:#D9E2EC;--good:#1F7A5C;--bad:#B42318;}
      .block-container{max-width:1500px;padding-top:2rem;padding-bottom:4rem;}
      h1,h2,h3{color:var(--navy);letter-spacing:-0.02em;}
      .hero{padding:1.3rem 1.5rem 1.1rem;border:1px solid var(--line);border-radius:18px;
            background:linear-gradient(135deg,#F8FAFC 0%,#EEF5F8 100%);margin-bottom:1.4rem;}
      .hero-title{font-size:2.05rem;line-height:1.2;font-weight:760;color:var(--navy);margin-bottom:.35rem;}
      .hero-sub{color:var(--muted);font-size:1rem;}
      .section-tag{display:inline-block;padding:.24rem .64rem;border-radius:999px;background:#EAF1F6;
                   color:var(--blue);font-weight:700;font-size:.82rem;margin-bottom:.35rem;}
      .status-good{background:#ECFDF3;color:var(--good);border:1px solid #ABEFC6;border-radius:12px;
                   padding:.8rem 1rem;font-weight:700;}
      .status-bad{background:#FEF3F2;color:var(--bad);border:1px solid #FECDCA;border-radius:12px;
                  padding:.8rem 1rem;font-weight:700;}
      .eng-comment{border-left:4px solid var(--blue);background:#F8FAFC;border-radius:10px;
                   padding:.9rem 1.05rem;margin-bottom:.7rem;color:#1F2937;}
      div[data-testid="stMetric"]{border:1px solid var(--line);border-radius:12px;padding:.72rem .85rem;background:#FFF;}
      div[data-testid="stFileUploader"]{border:1px solid var(--line);border-radius:12px;padding:.55rem;background:#FBFCFD;}
      .stButton>button{border-radius:10px;font-weight:700;}
    </style>
    """, unsafe_allow_html=True)


def hero():
    st.markdown("""
    <div class="hero">
      <div class="hero-title">Long-Term Settlement Assessment of Normally Consolidated Clays under Repetitive Loading</div>
      <div class="hero-sub">Design-stage prediction, serviceability assessment, and monitoring-based calibration in one workflow.</div>
    </div>
    """, unsafe_allow_html=True)
