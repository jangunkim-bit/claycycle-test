import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Long-Term Settlement Assessment",
    page_icon="📈",
    layout="centered",
)

st.title("Long-Term Settlement Assessment of Normally Consolidated Clays under Repetitive Loading")
st.caption("Web-based implementation of the proposed framework")

max_cycles = st.slider(
    "Maximum number of cycles",
    min_value=1000,
    max_value=1000000,
    value=100000,
    step=1000,
)

cycles = [1, 10, 100, 1000, 10000, 100000, 1000000]
settlement = [3, 12, 29, 48, 61, 68, 71]

df = pd.DataFrame({"Cycles": cycles, "Settlement (mm)": settlement})
df = df[df["Cycles"] <= max_cycles]

st.subheader("Example repetitive-loading settlement curve")
st.line_chart(df, x="Cycles", y="Settlement (mm)")

st.dataframe(df, use_container_width=True)

st.success("If you can see this page after deployment, the GitHub → Streamlit workflow works.")
