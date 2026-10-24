import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path


# =========================================================
# 1. PROJECT PATHS AND BRAND TOKENS
# =========================================================
# Resolve paths relative to the project root in both local and container runs.
# In this deployment, this file lives at dashboard/app_vercel.py.
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = BASE_DIR / "data" / "processed" / "wildfire_cleaned.csv"
HOTSPOT_DIR = BASE_DIR / "data" / "processed" / "grid_hotspots_output"
CLUSTER_DIR = BASE_DIR / "data" / "processed" / "ml_hotspot_clusters"

# Rose-gold and silver brand accents. Background, surface, text, and border
# Custom CSS intentionally avoids fixed page/card fills; Streamlit's native
# theme paints backgrounds and text so its three-dot Light/Dark selector works.
ROSE = "#B76E79"
ROSE_DARK = "#6D4149"
LIGHT_ROSE = "#F0C6B8"
SILVER = "#C0C0C0"
SILVER_ACCENT = "#E5E7EB"

st.set_page_config(
    page_title="Wildfire Intelligence | Analytics Console",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

CLUSTER_COLORS = {
    "0": "#C0C0C0",
    "1": "#F0C6B8",
    "2": "#B76E79",
    "3": "#6D4149",
}


# =========================================================
# 2. CENTRALIZED, LIVE STREAMLIT-THEME-AWARE CSS
# =========================================================
st.markdown(
    """
    <style>
      :root {
        --brand-black: #080808;
        --brand-charcoal: #1C1C1C;
        --brand-elevated: #21191C;
        --brand-silver: #C0C0C0;
        --brand-silver-accent: #E5E7EB;
        --brand-rose: #B76E79;
        --brand-rose-light: #F0C6B8;
        --brand-rose-dark: #6D4149;
        --brand-border: #353033;
        --transition-ui: 220ms ease;
      }

      /* IMPORTANT: don't paint global backgrounds or body text here.
         Streamlit's native three-dot Light/Dark selector owns these colors.
         Custom sections below are transparent and inherit foreground colors. */
      html, body, [class*="css"] {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
      }
      [data-testid="stHeader"] { background: transparent !important; }
      [data-testid="stToolbar"] { right: 1.1rem; }
      .block-container { max-width: 1500px; padding: 2.35rem clamp(1rem, 3vw, 2rem) 3rem; }

      h1, h2, h3, h4 { letter-spacing: -0.025em; }
      h1 { font-weight: 700 !important; }
      h2, h3 { font-weight: 650 !important; }
      a { text-decoration-thickness: 1px; text-underline-offset: 3px; }
      hr { border-color: rgba(128,128,128,.35); margin: 1.25rem 0; }

      /* Sidebar styling only: leave its fill and text colors to Streamlit. */
      section[data-testid="stSidebar"] { border-right: 1px solid rgba(128,128,128,.28); }
      section[data-testid="stSidebar"] > div { padding-top: 1rem; }
      section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { line-height: 1.6; }
      .sidebar-kicker { font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; font-weight: 750; }
      .sidebar-title { font-size: 1.12rem; font-weight: 700; margin-top: .35rem; }
      .sidebar-copy { font-size: .82rem; line-height: 1.6; margin-top: .3rem; opacity: .82; }
      .data-note-title { font-weight: 650; }

      /* Hero: complete visible outline, transparent fill so Light/Dark both work. */
      .hero-panel {
        display: block; position: relative; box-sizing: border-box; width: 100%; min-width: 0;
        overflow: hidden; background: transparent;
        border: 1px solid rgba(183,110,121,.62); border-top: 2px solid rgba(183,110,121,.72);
        border-radius: 16px; padding: clamp(1.65rem, 3vw, 2.6rem);
        margin: .8rem 0 1.5rem; isolation: isolate;
      }
      .hero-panel:after {
        content: ""; position: absolute; z-index: -1; right: -105px; top: -145px;
        width: 330px; height: 330px; border: 1px solid rgba(183,110,121,.22);
        border-radius: 50%; pointer-events: none;
      }
      .hero-kicker {
        display: inline-flex; align-items: center; gap: .45rem; padding: .35rem .65rem;
        margin-bottom: .9rem; border: 1px solid rgba(183,110,121,.62); border-radius: 999px;
        color: inherit; font-size: .72rem; font-weight: 750;
        letter-spacing: .11em; text-transform: uppercase;
      }
      .hero-title {
        display: block; width: 100%; max-width: 100%; margin: 0; padding: 0;
        color: inherit; font-size: clamp(1.75rem, 3vw, 2.8rem);
        line-height: 1.14; font-weight: 750; letter-spacing: -.04em;
        overflow-wrap: anywhere; text-wrap: pretty;
      }
      .hero-title .accent { color: inherit; text-decoration: underline; text-decoration-color: #B76E79; text-decoration-thickness: 3px; text-underline-offset: 5px; }
      .hero-copy { max-width: 860px; margin: .95rem 0 0; line-height: 1.75; opacity: .84; }
      .hero-meta { display:flex; flex-wrap:wrap; gap:.55rem; margin-top:1.25rem; }
      .hero-chip {
        display:inline-flex; align-items:center; gap:.45rem; padding:.45rem .7rem;
        border-radius:8px; background: transparent; border:1px solid rgba(128,128,128,.35);
        color: inherit; font-size:.82rem;
      }

      /* Metric cards stay transparent to inherit the selected native theme. */
      div[data-testid="stMetric"] {
        background: transparent !important; border: 1px solid rgba(128,128,128,.32);
        border-radius: 14px; padding: 1.1rem 1.15rem; min-height: 122px;
        transition: transform var(--transition-ui), border-color var(--transition-ui);
      }
      div[data-testid="stMetric"]:hover { border-color: #B76E79; transform: translateY(-2px); }
      div[data-testid="stMetricLabel"] { font-size: .82rem; }
      div[data-testid="stMetricValue"] { font-weight: 700; letter-spacing: -.035em; }
      div[data-testid="stMetricDelta"] { font-weight: 600; }

      /* Tabs remain transparent; Streamlit paints each theme's native surfaces. */
      .stTabs [data-baseweb="tab-list"] {
        gap: .4rem; background: transparent; border-bottom: 1px solid rgba(128,128,128,.32);
        padding: .4rem 0; flex-wrap: wrap;
      }
      .stTabs [data-baseweb="tab"] {
        color: inherit; border-radius: 8px; padding: .65rem 1rem; background: transparent;
        transition: border-color var(--transition-ui), color var(--transition-ui);
      }
      .stTabs [data-baseweb="tab"]:hover { border-color: rgba(183,110,121,.5); }
      .stTabs [data-baseweb="tab"][aria-selected="true"] {
        box-shadow: inset 0 -2px 0 #B76E79;
      }
      .stTabs [data-baseweb="tab-highlight"] { background: #B76E79; }

      /* Silver primary buttons and transparent rose-gold secondary buttons. */
      .stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
        border-radius: 9px; min-height: 2.55rem; font-weight: 650;
        transition: background var(--transition-ui), border-color var(--transition-ui), color var(--transition-ui), transform var(--transition-ui);
      }
      .stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"] {
        color: #080808; background: #C0C0C0; border: 1px solid #C0C0C0;
      }
      .stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
        color: #080808; background: #E5E7EB; border-color: #E5E7EB; transform: translateY(-1px);
      }
      .stButton > button:not([kind="primary"]), .stDownloadButton > button {
        color: inherit; background: transparent; border: 1px solid #6D4149;
      }
      .stButton > button:not([kind="primary"]):hover, .stDownloadButton > button:hover {
        color: inherit; background: rgba(183,110,121,.09); border-color: #B76E79; transform: translateY(-1px);
      }
      .stButton > button:active, .stDownloadButton > button:active { transform: translateY(0); }
      .stButton > button:disabled, .stDownloadButton > button:disabled { opacity: .45; cursor: not-allowed; transform: none; }
      button:focus-visible, a:focus-visible, input:focus-visible, textarea:focus-visible {
        outline: 2px solid #B76E79 !important; outline-offset: 3px !important;
        box-shadow: 0 0 0 3px rgba(183,110,121,.18) !important;
      }

      /* Let native widget fills and text follow the selected Streamlit theme. */
      [data-baseweb="select"] > div, [data-baseweb="input"] > div,
      [data-baseweb="textarea"] > div, [data-testid="stDateInput"] input {
        border-radius: 9px !important;
      }
      [data-baseweb="select"] > div:hover, [data-baseweb="input"] > div:hover,
      [data-baseweb="textarea"] > div:hover { border-color: #B76E79 !important; }
      [data-testid="stMultiSelect"] [data-baseweb="tag"] { background: #6D4149 !important; color: #FFF5F2 !important; }

      [data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid rgba(128,128,128,.32); border-radius: 12px; overflow: hidden; }
      [data-testid="stExpander"] { border: 1px solid rgba(128,128,128,.32); border-radius: 12px; }
      [data-testid="stAlert"] { border-radius: 12px; border: 1px solid rgba(183,110,121,.45); }
      [data-testid="stNotification"] { border-radius: 12px; }
      code { color: #B76E79 !important; }
      .section-heading { margin: .25rem 0 .85rem; font-size: 1.1rem; font-weight: 650; letter-spacing: -.015em; }
      .section-description { line-height: 1.7; margin-top: -.35rem; opacity: .84; }
      .status-note { padding: .8rem 1rem; background: transparent; border: 1px solid rgba(128,128,128,.32); border-radius: 10px; font-size: .86rem; line-height: 1.6; }
      .footer-note { border-top:1px solid rgba(128,128,128,.32); margin-top:1.8rem; padding-top:1.1rem; font-size:.8rem; line-height:1.65; opacity:.84; }
      .footer-brand { font-weight: 650; }
      [data-testid="stSpinner"] > div { border-top-color: #B76E79 !important; }
      ::selection { background: #6D4149; color: #FFF5F2; }

      @media (max-width: 768px) {
        .block-container { padding: 1.75rem .85rem 2rem; }
        .hero-panel { padding: 1.3rem; border-radius: 13px; margin-top: .55rem; }
        .hero-title { font-size: clamp(1.55rem, 6vw, 2.15rem); line-height: 1.15; }
        .hero-meta { gap: .4rem; }
        .hero-chip { font-size: .76rem; padding: .4rem .55rem; }
        .stTabs [data-baseweb="tab-list"] { gap: .2rem; }
        .stTabs [data-baseweb="tab"] { padding: .55rem .7rem; font-size: .84rem; }
        div[data-testid="stMetric"] { padding: .85rem; min-height: 108px; }
      }
      @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; scroll-behavior: auto !important; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. APP HEADER / HERO
# =========================================================
st.markdown(
    """
    <section class="hero-panel">
      <div class="hero-kicker">✦ Wildfire analytics console</div>
      <h1 class="hero-title">Wildfire Intelligence <span class="accent">Dashboard</span></h1>
      <p class="hero-copy">
        A focused view of NASA FIRMS detections, geographic hotspots, seasonal patterns,
        and Spark MLlib clusters across California for 2024–2025.
      </p>
      <div class="hero-meta">
        <span class="hero-chip">◈ NASA FIRMS · VIIRS</span>
        <span class="hero-chip">▦ Apache Spark 3.5</span>
        <span class="hero-chip">✳ Spark MLlib · K-Means</span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 4. DATA ACCESS
# =========================================================
@st.cache_data(show_spinner=False)
def load_csv(path):
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_parquet(path):
    # Read Spark's Parquet part files directly. The dashboard only needs the
    # precomputed aggregations, so the public dashboard does not need to start
    # a JVM/Spark session at runtime.
    folder = Path(path)
    parquet_files = sorted(folder.glob("part-*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"No Parquet part files found in {folder}")
    frames = [pd.read_parquet(file) for file in parquet_files]
    return pd.concat(frames, ignore_index=True)


required_paths = [CSV_FILE, HOTSPOT_DIR, CLUSTER_DIR]
missing_paths = [path for path in required_paths if not os.path.exists(path)]

if missing_paths:
    st.error("Some required project files or folders are missing.")
    for path in missing_paths:
        st.code(path)
    st.stop()

with st.spinner("Loading wildfire data and Spark results…"):
    try:
        fires = load_csv(CSV_FILE)
        hotspots = load_parquet(HOTSPOT_DIR)
        clusters = load_parquet(CLUSTER_DIR)
    except Exception as error:
        st.error(f"Could not load project data: {error}")
        st.stop()


# =========================================================
# 5. DATA PREPARATION
# =========================================================
fires["acq_date"] = pd.to_datetime(fires["acq_date"], errors="coerce")
fires["frp"] = pd.to_numeric(fires["frp"], errors="coerce")
fires = fires.dropna(subset=["latitude", "longitude", "acq_date"]).copy()

hotspots = hotspots.copy()
clusters = clusters.copy()

hotspots["latitude_center"] = hotspots["grid_lat"] + 0.05
hotspots["longitude_center"] = hotspots["grid_lon"] + 0.05
clusters["latitude_center"] = clusters["grid_lat"] + 0.05
clusters["longitude_center"] = clusters["grid_lon"] + 0.05
clusters["cluster_label"] = clusters["cluster_id"].astype(str)


# =========================================================
# 6. SIDEBAR CONTROLS
# =================================================n
st.sidebar.markdown(
    """
    <div style="padding:.35rem 0 1.1rem">
      <div class="sidebar-kicker">WILDFIRE INTELLIGENCE</div>
      <div class="sidebar-title">Control panel</div>
      <div class="sidebar-copy">Explore historic detections and model outputs.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("### Filters")

available_years = sorted(fires["acq_date"].dt.year.dropna().unique().tolist())
selected_years = st.sidebar.multiselect(
    "Acquisition year",
    options=available_years,
    default=available_years,
    help="This filter updates the historical trend charts and the detection-record table.",
)

if selected_years:
    filtered_fires = fires[fires["acq_date"].dt.year.isin(selected_years)].copy()
else:
    filtered_fires = fires.iloc[0:0].copy()

st.sidebar.markdown(
    """
    <div class="status-note" style="margin-top:1.25rem">
      <strong class="data-note-title">Data note</strong><br>
      Satellite detections are indicators of possible fire activity, not confirmed incidents or fire perimeters.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 7. KPI OVERVIEW
# =========================================================
st.markdown('<div class="section-heading">Project overview</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-description">Key figures from the selected historical records and existing Spark outputs.</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
mean_frp = filtered_fires["frp"].mean() if not filtered_fires.empty else float("nan")

col1.metric("Fire detections", f"{len(filtered_fires):,}")
col2.metric("Geographic grid cells", f"{len(hotspots):,}")
col3.metric("MLlib clusters", f"{clusters['cluster_id'].nunique():,}")
col4.metric("Average FRP", f"{mean_frp:.2f} MW" if pd.notna(mean_frp) else "N/A")

st.caption(
    "FRP means Fire Radiative Power. Grid-cell and clustering totals reflect the full prepared dataset; year filters apply to historical records."
)


# =========================================================
# 8. PLOTLY STYLE HELPERS
# =========================================================
def style_chart(fig, height=420):
    # Keep layout backgrounds/text theme-driven. st.plotly_chart(theme="streamlit")
    # applies the currently selected native Light/Dark theme at render time.
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=12),
        title=dict(font=dict(size=17), x=0.02, xanchor="left"),
        height=height,
        margin=dict(l=18, r=18, t=64, b=24),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(128,128,128,0.35)",
            borderwidth=1,
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(128,128,128,0.22)",
        linecolor="rgba(128,128,128,0.45)",
        zerolinecolor="rgba(128,128,128,0.35)",
    )
    fig.update_yaxes(
        gridcolor="rgba(128,128,128,0.22)",
        linecolor="rgba(128,128,128,0.45)",
        zerolinecolor="rgba(128,128,128,0.35)",
    )
    return fig


def style_geo(fig, height=650):
    # Leave land/ocean fills unset so Plotly's Streamlit theme can supply them.
    fig.update_geos(
        projection_type="mercator",
        lonaxis_range=[-125, -114],
        lataxis_range=[32, 42],
        showland=True,
        showocean=True,
        showcoastlines=True,
        coastlinecolor="#8B7D81",
        showcountries=True,
        countrycolor="rgba(128,128,128,0.55)",
        showsubunits=True,
        subunitcolor="#B76E79",
        showframe=True,
        framecolor="rgba(128,128,128,0.45)",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=12),
        title=dict(font=dict(size=17), x=0.02, xanchor="left"),
        height=height,
        margin=dict(l=10, r=10, t=64, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(128,128,128,0.35)",
            borderwidth=1,
        ),
    )
    return fig


# =========================================================
# 9. DASHBOARD TABS
# =================================================nover

overview_tab, hotspot_tab, cluster_tab, data_tab = st.tabs(
    ["Historical trends", "Hotspot map", "MLlib clusters", "Data explorer"]
)


# =========================================================
# TAB 1: HISTORICAL TRENDS
# =========================================================
with overview_tab:
    st.markdown('<div class="section-heading">Detection activity over time</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">Explore monthly and annual patterns in the selected acquisition years.</div>',
        unsafe_allow_html=True,
    )

    if filtered_fires.empty:
        st.info("Select at least one acquisition year in the sidebar to view historical trends.")
    else:
        monthly = (
            filtered_fires.assign(month=filtered_fires["acq_date"].dt.to_period("M").astype(str))
            .groupby("month")
            .size()
            .reset_index(name="detections")
            .sort_values("month")
        )
        trend_fig = px.line(
            monthly,
            x="month",
            y="detections",
            markers=True,
            title="Monthly fire detections",
            labels={"month": "Month", "detections": "Detections"},
        )
        trend_fig.update_traces(line=dict(color=ROSE, width=2.5), marker=dict(color=ROSE_DARK, size=6, line=dict(color=LIGHT_ROSE, width=1)))
        style_chart(trend_fig, 420)
        trend_fig.update_layout(hovermode="x unified", xaxis_tickangle=-35)
        st.plotly_chart(trend_fig, use_container_width=True, theme="streamlit", config={"displaylogo": False, "responsive": True})

        yearly = (
            filtered_fires.assign(year=filtered_fires["acq_date"].dt.year)
            .groupby("year")
            .size()
            .reset_index(name="detections")
        )
        annual_fig = px.bar(
            yearly,
            x="year",
            y="detections",
            text="detections",
            title="Detections by year",
            labels={"year": "Year", "detections": "Detections"},
        )
        annual_fig.update_traces(marker_color=ROSE, marker_line_color=ROSE_DARK, marker_line_width=1, textposition="outside")
        style_chart(annual_fig, 360)
        st.plotly_chart(annual_fig, use_container_width=True, theme="streamlit", config={"displaylogo": False, "responsive": True})

        st.markdown('<div class="section-heading">Fire radiative power</div>', unsafe_allow_html=True)
        frp_data = filtered_fires.dropna(subset=["frp"])
        if not frp_data.empty:
            frp_fig = px.histogram(
                frp_data,
                x="frp",
                nbins=40,
                title="Distribution of FRP measurements",
                labels={"frp": "Fire Radiative Power (MW)", "count": "Record count"},
            )
            frp_fig.update_traces(marker_color=ROSE, marker_line_color=ROSE_DARK, marker_line_width=0.5)
            style_chart(frp_fig, 360)
            st.plotly_chart(frp_fig, use_container_width=True, theme="streamlit", config={"displaylogo": False, "responsive": True})


# =========================================================
# TAB 2: GEOGRAPHIC HOTSPOT MAP
# =========================================================
with hotspot_tab:
    st.markdown('<div class="section-heading">Geographic hotspot distribution</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">Each marker represents the center of a 0.1° grid cell. Marker size and color represent detection count.</div>',
        unsafe_allow_html=True,
    )

    min_detections = int(hotspots["detections"].min())
    max_detections = int(hotspots["detections"].max())
    if min_detections < max_detections:
        detection_threshold = st.slider(
            "Minimum detections per grid cell",
            min_value=min_detections,
            max_value=max_detections,
            value=min_detections,
            help="Increase the threshold to focus on cells with more detections.",
        )
    else:
        detection_threshold = min_detections

    visible_hotspots = hotspots[hotspots["detections"] >= detection_threshold].copy()
    st.caption(f"Displaying {len(visible_hotspots):,} of {len(hotspots):,} grid cells.")

    if visible_hotspots.empty:
        st.warning("No grid cells match this filter. Lower the minimum-detection threshold.")
    else:
        map_fig = px.scatter_geo(
            visible_hotspots,
            lat="latitude_center",
            lon="longitude_center",
            color="detections",
            size="detections",
            size_max=20,
            color_continuous_scale=[LIGHT_ROSE, ROSE, ROSE_DARK],
            hover_data={
                "grid_lat": ":.2f",
                "grid_lon": ":.2f",
                "detections": True,
                "average_frp": ":.2f",
                "latitude_center": False,
                "longitude_center": False,
            },
            title="Detection density by geographic grid cell",
            labels={
                "detections": "Detections",
                "average_frp": "Average FRP (MW)",
                "grid_lat": "Grid latitude",
                "grid_lon": "Grid longitude",
            },
        )
        style_geo(map_fig, 680)
        map_fig.update_layout(coloraxis_colorbar=dict(title=dict(text="Detections")))
        st.plotly_chart(map_fig, use_container_width=True, theme="streamlit", config={"displaylogo": False, "responsive": True})

        st.markdown('<div class="section-heading">Highest-count grid cells</div>', unsafe_allow_html=True)
        top_hotspots = (
            hotspots.nlargest(10, "detections")[["grid_lat", "grid_lon", "detections", "average_frp"]]
            .reset_index(drop=True)
        )
        st.dataframe(
            top_hotspots,
            use_container_width=True,
            hide_index=True,
            column_config={
                "grid_lat": st.column_config.NumberColumn("Grid latitude", format="%.2f°"),
                "grid_lon": st.column_config.NumberColumn("Grid longitude", format="%.2f°"),
                "detections": st.column_config.NumberColumn("Detections", format="%,d"),
                "average_frp": st.column_config.NumberColumn("Average FRP (MW)", format="%.2f"),
            },
        )


# =========================================================
# TAB 3: MLlib CLUSTERS
# =========================================================
with cluster_tab:
    st.markdown('<div class="section-heading">K-Means cluster analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">Cluster labels summarize similarities across location, detection count, and average FRP. Labels are not validated fire-risk categories.</div>',
        unsafe_allow_html=True,
    )

    cluster_summary = (
        clusters.groupby("cluster_id")
        .agg(
            grid_cells=("cluster_id", "size"),
            avg_detections=("detections", "mean"),
            max_detections=("detections", "max"),
            mean_frp=("average_frp", "mean"),
        )
        .reset_index()
        .sort_values("cluster_id")
    )

    st.dataframe(
        cluster_summary.rename(
            columns={
                "cluster_id": "Cluster",
                "grid_cells": "Grid cells",
                "avg_detections": "Average detections",
                "max_detections": "Max detections in a cell",
                "mean_frp": "Mean FRP (MW)",
            }
        ).round(2),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cluster": st.column_config.NumberColumn("Cluster", format="%d"),
            "Grid cells": st.column_config.NumberColumn("Grid cells", format="%,d"),
            "Average detections": st.column_config.NumberColumn("Average detections", format="%.2f"),
            "Max detections in a cell": st.column_config.NumberColumn("Max detections in a cell", format="%,d"),
            "Mean FRP (MW)": st.column_config.NumberColumn("Mean FRP (MW)", format="%.2f"),
        },
    )

    dist_fig = px.bar(
        cluster_summary,
        x="cluster_id",
        y="grid_cells",
        text="grid_cells",
        color="cluster_id",
        title="Grid-cell distribution by cluster",
        labels={"cluster_id": "Cluster ID", "grid_cells": "Grid cells"},
        # Uses theme-specific chartCategoricalColors from .streamlit/config.toml.
    )
    dist_fig.update_traces(marker_line_color=ROSE_DARK, marker_line_width=1, textposition="outside")
    style_chart(dist_fig, 360)
    st.plotly_chart(dist_fig, use_container_width=True, theme="streamlit", config={"displaylogo": False, "responsive": True})

    cluster_fig = px.scatter_geo(
        clusters,
        lat="latitude_center",
        lon="longitude_center",
        color="cluster_label",
        color_discrete_map=CLUSTER_COLORS,
        size="detections",
        size_max=18,
        hover_data={
            "cluster_label": True,
            "detections": True,
            "average_frp": ":.2f",
            "latitude_center": False,
            "longitude_center": False,
        },
        title="Geographic distribution of MLlib clusters",
        labels={"cluster_label": "Cluster", "detections": "Detections", "average_frp": "Average FRP (MW)"},
    )
    style_geo(cluster_fig, 650)
    cluster_fig.update_layout(legend_title_text="MLlib cluster")
    st.plotly_chart(cluster_fig, use_container_width=True, theme="streamlit", config={"displaylogo": False, "responsive": True})

    st.markdown(
        '<div class="status-note">Interpretation note: K-Means cluster IDs are arbitrary statistical labels. Validate against additional evidence before using them for response priority.</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# TAB 4: DATA EXPLORER
# =========================================================
with data_tab:
    st.markdown('<div class="section-heading">Cleaned detection records</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-description">Browse the cleaned NASA FIRMS records and download the rows included by your year filter.</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Records available under the selected year filter: {len(filtered_fires):,}")
    st.dataframe(filtered_fires, use_container_width=True, hide_index=True)
    csv_download = filtered_fires.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered detections (CSV)",
        data=csv_download,
        file_name="filtered_wildfire_detections.csv",
        mime="text/csv",
        help="Downloads only records matching the selected acquisition years.",
    )


# =========================================================
# 10. FOOTER
# =========================================================
st.markdown(
    """
    <div class="footer-note">
      <strong class="footer-brand">Wildfire Intelligence · INT315 Cluster Computing</strong><br>
      Source: NASA FIRMS VIIRS active-fire detections. This prototype supports historical analysis and geographic exploration;
      satellite detections are not confirmed wildfire incidents or fire perimeters, and this dashboard is not an operational
      emergency-dispatch system.
    </div>
    """,
    unsafe_allow_html=True,
)
