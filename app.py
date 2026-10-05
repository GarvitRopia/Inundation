import io
import os
from dotenv import load_dotenv
from groq import Groq
import pandas as pd
import streamlit as st

load_dotenv()

# 1. Page Configuration
st.set_page_config(
    page_title="Mine Inundation Hazard Dashboard", layout="wide"
)
st.title("Mine Inundation Hazard Dashboard")
st.markdown(
    "AI-driven telemetry monitoring and early hazard prevention system."
)

# 2. Sidebar Configuration
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input(
    "Groq API Key",
    value=os.getenv("GROQ_API_KEY", ""),
    type="password",
    help="Set GROQ_API_KEY in .env or enter it here.",
)

uploaded_file = st.sidebar.file_uploader(
    "Upload Inundation CSV", type=["csv"]
)

if uploaded_file is not None:
  df = pd.read_csv(uploaded_file)
  st.sidebar.success("Custom CSV loaded successfully!")
else:
  st.sidebar.info("Using baseline historical sample.")
  sample_csv = """Date,Seepage_Rate_LPM,Rainfall_mm,Sump_Level_m
2026-09-25,450,15,2.1
2026-09-26,480,25,2.5
2026-09-27,550,45,3.8
2026-09-28,700,60,4.5
2026-09-29,850,85,5.8
2026-09-30,920,110,6.5
"""
  df = pd.read_csv(io.StringIO(sample_csv))

# 3. Data View & Trend Analysis
col1, col2 = st.columns([1, 1])

with col1:
  st.subheader("Historical Inundation Metrics")
  st.dataframe(df, use_container_width=True)

with col2:
  st.subheader("Hazard Trend Analysis")
  plot_df = df.copy()
  if "Date" in plot_df.columns:
    plot_df.set_index("Date", inplace=True)
  numeric_cols = plot_df.select_dtypes(
      include=["float64", "int64"]
  ).columns
  st.line_chart(plot_df[numeric_cols])

# 4. Agentic AI Assessment Section
st.divider()
st.subheader("Agentic Hazard Analysis & Preventive Action")

if st.button("Run AI Risk Assessment"):
      if not api_key:
        st.error(
            "Please provide an API Key in the sidebar to proceed."
        )
      else:
        with st.spinner("Analyzing telemetry trends against mine SOPs..."):
          try:
            client = Groq(api_key=api_key)

            system_prompt = """You are an autonomous Mine Safety Agentic AI specializing in inundation hazard prevention.
Your objective is to analyze real-time environmental metrics (rainfall, seepage rates, sump levels) and determine the hazard risk.

Standard Operating Procedures & Guidelines:
- Seepage Rate > 800 LPM: Critical threshold; inspect retaining sumps and prepare standby dewatering pumps.
- Sump Level > 5.5m: High risk of overflow; activate auxiliary pumping installations and verify garland drain discharge channels.
- Continuous rainfall > 50mm/day: Inspect surface bunds, check barrier pillar stability, and restrict access to lower seam workings.

Output Format:
**Risk Level:** [LOW / MEDIUM / HIGH]
**Trend Analysis:** [1-2 sentences explaining why, citing specific data values]
**Actionable Measures:**
* [Measure 1]
* [Measure 2]
* [Measure 3]"""

            recent_telemetry = df.tail(3).to_string(index=False)
            user_prompt = f"""Here are the latest telemetry readings:
{recent_telemetry}

Evaluate the data against the established thresholds and generate the hazard assessment."""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            ai_output = response.choices[0].message.content
            st.success("Analysis Complete")
            st.markdown(ai_output)

          except Exception as e:
            st.error(f"Error calling Groq API: {e}")