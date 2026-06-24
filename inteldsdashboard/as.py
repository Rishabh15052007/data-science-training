import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------
# 1. CANVAS CONFIGURATION & EXECUTIVE THEME
# ------------------------------------
st.set_page_config(
    page_title="Intel Engineering Analytics Portal",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Executive Slate Styling Framework
st.markdown("""
    <style>
    /* Clean neutral canvas framework */
    .main { background-color: #f8fafc; color: #1e293b; }
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] .stMarkdown h3 { color: #38bdf8 !important; }
    [data-testid="stSidebar"] label { color: #cbd5e1 !important; font-weight: 500; }
    
    /* Structured KPI Block Components */
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }
    .kpi-lbl { font-size: 12px; font-weight: 600; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px; }
    .kpi-val { font-size: 26px; font-weight: 700; color: #0f172a; margin-top: 5px; }
    .kpi-sub-row { display: flex; justify-content: space-between; font-size: 12px; color: #475569; margin-top: 12px; border-top: 1px solid #e2e8f0; padding-top: 8px; }
    .val-high { color: #16a34a; font-weight: 600; }
    .val-low { color: #dc2626; font-weight: 600; }
    
    h3 { color: #0f172a !important; font-weight: 700 !important; font-size: 18px !important; margin-bottom: 15px !important; }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------
# 2. ROBUST DATA PROCESSING PIPELINE
# ------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("intelds_cleaned.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Units Sold'] = df['Units Sold'].fillna(0)
    df['Total Revenue (USD)'] = df['Total Revenue (USD)'].fillna(0)
    df['TDP (Watts)'] = df['TDP (Watts)'].fillna(0)
    df['Cores'] = df['Cores'].fillna(0)
    df['Year'] = df['Year'].fillna(df['Date'].dt.year)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Missing 'intelds_cleaned.csv' data repository file within this root folder layout context.")
    st.stop()

# ------------------------------------
# 3. INTERACTIVE CONTROL SIDEBAR PANEL
# ------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/c/c9/Intel-logo.svg", width=90)
st.sidebar.markdown("### 🎛️ Workspace Controls")

search_model = st.sidebar.text_input("Model Directory Search", placeholder="e.g., Core i9, Xeon")

years = sorted(df['Year'].dropna().unique())
selected_years = st.sidebar.multiselect("Production Year Matrix", options=years, default=years)

regions = sorted(df['Region'].dropna().unique())
selected_regions = st.sidebar.multiselect("Geographic Sales Domains", options=regions, default=regions)

segments = sorted(df['Segment'].dropna().unique())
selected_segments = st.sidebar.multiselect("Architecture Market Segment", options=segments, default=segments)

series_list = sorted(df['Series'].dropna().unique())
selected_series = st.sidebar.multiselect("Silicon Variant Series", options=series_list, default=series_list)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Physical Hardware Thresholds")
min_tdp, max_tdp = int(df['TDP (Watts)'].min()), int(df['TDP (Watts)'].max())
tdp_range = st.sidebar.slider("Thermal Envelope Range (Watts)", min_tdp, max_tdp, (min_tdp, max_tdp))

min_cores, max_cores = int(df['Cores'].min()), int(df['Cores'].max())
cores_range = st.sidebar.slider("Processor Cores Bounds", min_cores, max_cores, (min_cores, max_cores))

# Query Engine Execution
filtered_df = df[
    (df['Year'].isin(selected_years)) &
    (df['Region'].isin(selected_regions)) &
    (df['Segment'].isin(selected_segments)) &
    (df['Series'].isin(selected_series)) &
    (df['TDP (Watts)'].between(tdp_range[0], tdp_range[1])) &
    (df['Cores'].between(cores_range[0], cores_range[1]))
]

if search_model:
    filtered_df = filtered_df[filtered_df['Model'].str.contains(search_model, case=False, na=False)]

# ------------------------------------
# 4. MAIN TELEMETRY DASHBOARD FRAME
# ------------------------------------
st.title("💻 Intel Silicon Infrastructure Command Analytics")
st.markdown("A clean, highly scannable platform examining yield revenues, lithography nodes, and physical thermal metrics distributions.")
st.write("---")

# ------------------------------------
# 5. MAX, MIN, AVG DYNAMIC CARD BLOCKS
# ------------------------------------
st.markdown("### 🔢 Architectural Aggregation Matrix")
col_k1, col_k2, col_k3 = st.columns(3)

if not filtered_df.empty:
    avg_rev, max_rev, min_rev = filtered_df['Total Revenue (USD)'].mean(), filtered_df['Total Revenue (USD)'].max(), filtered_df['Total Revenue (USD)'].min()
    avg_tdp, max_tdp, min_tdp = filtered_df['TDP (Watts)'].mean(), filtered_df['TDP (Watts)'].max(), filtered_df['TDP (Watts)'].min()
    avg_cores, max_cores, min_cores = filtered_df['Cores'].mean(), filtered_df['Cores'].max(), filtered_df['Cores'].min()
else:
    avg_rev = max_rev = min_rev = avg_tdp = max_tdp = min_tdp = avg_cores = max_cores = min_cores = 0

with col_k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">💰 Commercial Financial Revenue</div>
        <div class="kpi-val">${avg_rev:,.2f} <span style="font-size:12px; color:#64748b; font-weight:normal;">(Avg)</span></div>
        <div class="kpi-sub-row">
            <span>MAX CAP: <span class="val-high">${max_rev:,.2f}</span></span>
            <span>MIN: <span class="val-low">${min_rev:,.2f}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">⚡ Thermal Design Envelopes (TDP)</div>
        <div class="kpi-val">{avg_tdp:.1f} W <span style="font-size:12px; color:#64748b; font-weight:normal;">(Avg)</span></div>
        <div class="kpi-sub-row">
            <span>MAX VALUE: <span class="val-high">{max_tdp:.0f}W</span></span>
            <span>MIN VALUE: <span class="val-low">{min_tdp:.0f}W</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">🎛️ Physical Computing Cores Matrix</div>
        <div class="kpi-val">{avg_cores:.1f} Cores <span style="font-size:12px; color:#64748b; font-weight:normal;">(Avg)</span></div>
        <div class="kpi-sub-row">
            <span>MAX DENSITY: <span class="val-high">{max_cores:.0f} Cores</span></span>
            <span>MIN: <span class="val-low">{min_cores:.0f} Cores</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# ------------------------------------
# 6. GRAPHICS & VISUALIZATION TRACKS
# ------------------------------------
if not filtered_df.empty:
    
    # ROW 1: LINE CHART & BAR GRAPH
    r1_g1, r1_g2 = st.columns(2)
    with r1_g1:
        st.subheader("📈 Revenue Performance Trajectory Over Time")
        time_data = filtered_df.groupby('Date')['Total Revenue (USD)'].sum().reset_index()
        fig_line = px.line(time_data, x='Date', y='Total Revenue (USD)', labels={'Total Revenue (USD)': 'Revenue ($)'}, template='plotly_white', color_discrete_sequence=['#0284c7'])
        st.plotly_chart(fig_line, use_container_width=True)
        
    with r1_g2:
        st.subheader("📊 Volumetric Gross Revenue Allocations by Region")
        bar_data = filtered_df.groupby('Region')['Total Revenue (USD)'].sum().reset_index()
        fig_bar = px.bar(bar_data, x='Region', y='Total Revenue (USD)', labels={'Total Revenue (USD)': 'Gross Yield ($)'}, template='plotly_white', color_discrete_sequence=['#475569'])
        st.plotly_chart(fig_bar, use_container_width=True)

    st.write("---")

    # ROW 2: CONTRAST PIE CHARTS
    r2_g1, r2_g2 = st.columns(2)
    with r2_g1:
        st.subheader("🍕 Volumetric Product Share by Infrastructure Segment")
        pie_data1 = filtered_df.groupby('Segment')['Units Sold'].sum().reset_index()
        fig_pie1 = px.pie(pie_data1, names='Segment', values='Units Sold', template='plotly_white', color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_pie1, use_container_width=True)
        
    with r2_g2:
        st.subheader("🔬 Production Allocation Yield Across Fabrication Lithography Nodes")
        pie_data2 = filtered_df.groupby('Lithography (nm)')['Units Sold'].sum().reset_index()
        fig_pie2 = px.pie(pie_data2, names='Lithography (nm)', values='Units Sold', template='plotly_white', color_discrete_sequence=px.colors.sequential.Slate_r)
        st.plotly_chart(fig_pie2, use_container_width=True)

    st.write("---")

    # ROW 3: SCATTER DOT PLOT MATRIX
    st.subheader("📍 Dotted Scatter Grid: Core Architectural Configurations vs TDP Envelopes")
    fig_scatter = px.scatter(
        filtered_df, x='Cores', y='TDP (Watts)', color='Series', hover_name='Model',
        labels={'Cores': 'Core Count Metrics', 'TDP (Watts)': 'TDP (Thermal Watts)'},
        template='plotly_white', color_discrete_sequence=px.colors.qualitative.Safe
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.write("---")
    st.subheader("📋 System Database Slices Data Table Ledger")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("⚠️ Workspace empty. Adjust your active sidebar multi-selection parameters to reload your graphs panel layout blocks.")