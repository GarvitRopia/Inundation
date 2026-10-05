import io
import os
from dotenv import load_dotenv
import httpx
from groq import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    Groq,
    RateLimitError,
)
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
api_key = os.getenv("GROQ_API_KEY")

uploaded_file = st.sidebar.file_uploader(
    "Upload Inundation CSV", type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("Custom CSV loaded successfully!")
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError, ValueError) as error:
        st.sidebar.error(f"Unable to read the CSV: {error}")
        st.stop()
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
        plot_df["Date"] = pd.to_datetime(plot_df["Date"], errors="coerce")
        plot_df.set_index("Date", inplace=True)
    numeric_cols = plot_df.select_dtypes(include="number").columns
    if len(numeric_cols):
        st.line_chart(plot_df[numeric_cols])
    else:
        st.info("Upload a CSV containing at least one numeric measurement column to view trends.")

# 4. Agentic AI Assessment Section
st.divider()
st.subheader("Agentic Hazard Analysis & Preventive Action")

if st.button("Run AI Risk Assessment"):
      if not api_key:
        st.error(
            "GROQ_API_KEY is not configured. Add it to the project's .env file and restart the app."
        )
      else:
        with st.spinner("Analyzing telemetry trends against mine SOPs..."):
          try:
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

            # Ignore stale HTTP(S)_PROXY settings that can prevent the Groq SDK
            # from reaching its API. The connection remains HTTPS-encrypted.
            with httpx.Client(timeout=30.0, trust_env=False) as http_client:
              client = Groq(
                  api_key=api_key,
                  http_client=http_client,
                  max_retries=2,
              )
              response = client.chat.completions.create(
                  model="openai/gpt-oss-20b",
                  messages=[
                      {"role": "system", "content": system_prompt},
                      {"role": "user", "content": user_prompt}
                  ]
              )

            ai_output = response.choices[0].message.content
            st.success("Analysis Complete")
            st.markdown(ai_output)

          except AuthenticationError:
            st.error("Groq rejected the configured API key. Check GROQ_API_KEY in .env.")
          except APIConnectionError:
            st.error("Could not reach Groq. Check your internet connection and try again.")
          except RateLimitError:
            st.error("Groq rate limit reached. Please wait a moment and try again.")
          except APIStatusError as error:
            st.error(f"Groq returned an API error (HTTP {error.status_code}). Please try again.")
          except Exception:
            st.error("An unexpected error occurred while running the risk assessment.")
