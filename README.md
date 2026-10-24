Wildfire Intelligence Dashboard
An interactive dashboard for exploring satellite-based fire detections across California during 2024–2025. The project uses NASA FIRMS VIIRS data and presents processed geographic summaries and Spark MLlib clustering results in a browser-based interface.

Live dashboard: https://wildfire-intelligence-dashboard.vercel.app  
GitHub repository: https://github.com/ANA01SHARMA/wildfire-intelligence-dashboard

Project Overview
Satellite datasets can contain tens of thousands of thermal detections. Before these records are useful for exploration, they need to be cleaned, grouped, and summarized. This project uses Apache Spark to process historical fire-detection data and provides an interactive dashboard for reviewing the resulting geographic patterns.

The dashboard is intended for historical analysis and exploration. Satellite detections indicate possible fire activity; they are not, by themselves, confirmed wildfire incidents or fire perimeters. The dashboard is not an operational emergency-dispatch system.
Dataset
- Source: NASA Fire Information for Resource Management System (FIRMS)
- Satellite/instrument: NOAA-21 VIIRS, 375 m active-fire product
- Study area: California, United States
- Study period: January 2024–December 2025
- Original dataset: 83,323 rows and 15 attributes
- Main analysis dataset: 70,874 records classified as type 0 (presumed vegetation fires)
- Source portal: https://firms.modaps.eosdis.nasa.gov/download/
The records include fields such as latitude, longitude, acquisition date and time, confidence, brightness, and Fire Radiative Power (FRP).
Key Results
The current dashboard displays the following project metrics:
- Fire detections: 70,874
- Geographic grid cells: 2,067
- K-Means clusters: 4
- Average Fire Radiative Power (FRP): 21.93 MW
These values describe the processed dataset and dashboard output; they should not be interpreted as verified wildfire counts, severity classes, or response priorities.
Dashboard Features
- Geographic hotspot map for exploring the distribution of detections
- Year-based exploration for 2024 and 2025
- Detection-threshold control for examining different subsets of the data
- Summary metrics and visualizations for fire detections and FRP
- Geographic grid summaries and Spark MLlib cluster visualization
- Data Explorer table with CSV download for the selected records
Technologies
- Apache Spark 3.5.9 / PySpark: distributed processing of historical data
- Spark MLlib: K-Means clustering
- Python 3.10: dashboard and data workflow
- Pandas and PyArrow: loading and handling cleaned CSV and Parquet outputs
- Plotly: interactive charts and geographic visualizations
- Streamlit: dashboard interface
- Git and GitHub: source control
- Vercel: dashboard deployment
The broader project work also includes a Kafka and Spark Structured Streaming experiment and a Scala GraphX resource-network experiment. Those components should be added to this GitHub repository as source files if this repository is being used as the complete, reproducible Cluster Computing submission.
Repository Layout
The current GitHub snapshot is organized around the deployed dashboard and its prepared data:
.
├── .streamlit/
├── dashboard/
│   └── app_vercel.py
├── data/
│   └── processed/
│       ├── wildfire_cleaned.csv
│       ├── grid_hotspots_output/
│       └── ml_hotspot_clusters/
├── .gitignore
├── Dockerfile.vercel
├── requirements-vercel.txt
└── README.md
The folder listing above reflects the dashboard-focused repository layout. Add the actual cleaning script, Spark processing script, Kafka streaming code, and Scala GraphX source files before describing the repository as containing all project implementation code.
Run the Dashboard Locally
Run these commands from the repository root in an environment with Python 3.10 installed. The processed CSV and Parquet files expected by the application must be present under data/processed/.
python -m venv .venv
Activate the virtual environment, then install the listed dependencies:

Windows Command Prompt
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-vercel.txt
streamlit run dashboard/app_vercel.py
PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-vercel.txt
streamlit run dashboard/app_vercel.py
Streamlit will print a local URL in the terminal, usually http://localhost:8501.
Project Workflow
1. Obtain historical active-fire detections from NASA FIRMS.
2. Inspect and clean the dataset, then retain type 0 records for the main analysis.
3. Use Apache Spark to generate geographic summaries and analysis outputs.
4. Apply Spark MLlib K-Means clustering to the geographic data.
5. Store the prepared outputs as CSV and Parquet files.
6. Load the prepared data in Streamlit and display it through interactive maps, charts, filters, and tables.
7. Deploy the dashboard on Vercel.
Limitations
- Satellite detections are indicators of potential fire activity and may include observations that are not confirmed wildfires.
- K-Means cluster identifiers are statistical group labels, not official fire-risk or severity categories.
- The dashboard analyzes historical data and is not a real-time alerting or emergency-dispatch service.
- Resource-allocation decisions require further validation, additional operational data, and review by responsible agencies.
References
- NASA FIRMS: https://firms.modaps.eosdis.nasa.gov/
- NASA FIRMS Archive Download: https://firms2.modaps.eosdis.nasa.gov/download/
- Apache Spark: https://spark.apache.org/docs/3.5.9/
- Streamlit: https://docs.streamlit.io/
- Plotly: https://plotly.com/python/
