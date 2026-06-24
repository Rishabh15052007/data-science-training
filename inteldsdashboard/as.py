import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------
# 1. CANVAS CONFIGURATION
# ------------------------------------
st.set_page_config(
    page_title="Intel Hardware Dashboard",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, simple card styles for the summary boxes (Background left default clean white)
st.markdown("""
    <style>
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .kpi-lbl { font-size: 11px; font-weight: 600; text-transform: uppercase; color: #64748b; }
    .kpi-val { font-size: 22px; font-weight: 700; color: #0f172a; margin-top: 5px; }
    .kpi-sub-row { display: flex; justify-content: space-between; font-size: 11px; color: #475569; margin-top: 10px; border-top: 1px solid #e2e8f0; padding-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------
# 2. DATA PROCESSING PIPELINE
# ------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("inteldsdashboard/intelds_cleaned.csv")
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
    st.error("Missing data repository file. Please verify folder paths.")
    st.stop()

# ------------------------------------
# 3. INTERACTIVE SIDEBAR FILTERS
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

# Filter Application
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
# 4. MAIN LAYOUT
# ------------------------------------
st.title("💻 Intel Silicon Infrastructure Analytics Portal")
st.write("---")

# SUMMARY METRICS MATRICES
st.markdown("### 🔢 Summary Value Metrics Block")
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
        <div class="kpi-val">${avg_rev:,.2f}</div>
        <div class="kpi-sub-row"><span>MAX: ${max_rev:,.2f}</span><span>MIN: ${min_rev:,.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">⚡ Thermal Design Envelopes (TDP)</div>
        <div class="kpi-val">{avg_tdp:.1f} W</div>
        <div class="kpi-sub-row"><span>MAX: {max_tdp:.0f}W</span><span>MIN: {min_tdp:.0f}W</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-lbl">🎛️ Physical Computing Cores Matrix</div>
        <div class="kpi-val">{avg_cores:.1f} Cores</div>
        <div class="kpi-sub-row"><span>MAX: {max_cores:.0f} C</span><span>MIN: {min_cores:.0f} C</span></div>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# ------------------------------------
# 5. CHARTS AND GRAPHICS ONLY
# ------------------------------------
if not filtered_df.empty:
    
    # 1. PIE CHART
    st.subheader("🍕 Pie Chart: Share of Units Sold by Processor Series")
    pie_data = filtered_df.groupby('Series')['Units Sold'].sum().reset_index()
    fig_pie = px.pie(pie_data, names='Series', values='Units Sold', template='plotly_white')
    st.plotly_chart(fig_pie, use_container_width=True)
    st.write("---")

    # 2. LINE CHART & 3. BAR GRAPH (SIDE-BY-SIDE)
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("📈 Line Chart: Revenue Performance Trend Over Time")
        time_data = filtered_df.groupby('Date')['Total Revenue (USD)'].sum().reset_index()
        fig_line = px.line(time_data, x='Date', y='Total Revenue (USD)', labels={'Total Revenue (USD)': 'Revenue ($)'}, template='plotly_white')
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col_g2:
        st.subheader("📊 Bar Graph: Gross Revenue Contributions by Region")
        bar_data = filtered_df.groupby('Region')['Total Revenue (USD)'].sum().reset_index()
        fig_bar = px.bar(bar_data, x='Region', y='Total Revenue (USD)', labels={'Total Revenue (USD)': 'Gross Yield ($)'}, template='plotly_white')
        st.plotly_chart(fig_bar, use_container_width=True)

    st.write("---")

    # 4. DOTTED GRAPH (SCATTER PLOT)
    st.subheader("📍 Dotted Graph (Scatter Plot): Physical Cores vs TDP Envelopes")
    fig_scatter = px.scatter(
        filtered_df, x='Cores', y='TDP (Watts)', color='Series', hover_name='Model',
        labels={'Cores': 'Core Count', 'TDP (Watts)': 'TDP (Watts)'}, template='plotly_white'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

else:
    st.info("⚠️ Workspace empty. Adjust filter options to reload.")
