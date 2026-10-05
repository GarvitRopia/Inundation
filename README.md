# Mine Inundation Hazard Dashboard

A Streamlit dashboard for monitoring mine inundation telemetry and generating AI-assisted hazard assessments. It displays historical measurements, charts numerical trends, and evaluates recent readings against safety thresholds for seepage, rainfall, and sump level.

The dashboard includes a baseline sample dataset and also accepts a custom CSV file.

## Prerequisites

- Python 3.10 or later
- A Groq API key

## Setup

Clone or download this project, then open a terminal in the project folder.


Install all required packages from `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

## Configure the API key

Create a file named `.env` in the project root (the same folder as `app.py`) and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Do not add quotes unless they are part of the key. The `.env` file is ignored by Git, so the key will not be committed with the project.

## Run the dashboard

Start the application with:

```powershell
python -m streamlit run app.py
```

Streamlit will print a local URL, normally [http://localhost:8501](http://localhost:8501). Open it in a browser.

## Using the dashboard

1. Use the included baseline data, or upload a CSV from the sidebar.
2. For the intended hazard assessment, include columns such as `Date`, `Seepage_Rate_LPM`, `Rainfall_mm`, and `Sump_Level_m`.
3. Review the data table and trend chart.
4. Select **Run AI Risk Assessment** to receive a risk level, trend analysis, and suggested preventive measures.

## Project files

- `app.py` - Streamlit dashboard and Groq assessment integration.
- `requirements.txt` - Python dependencies.
- `.env` - local Groq API key configuration; create this file yourself and keep it private.
