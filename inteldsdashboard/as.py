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
# 4. MAIN LAYOUT & GRID HEADERS
# ------------------------------------
st.title("💻 Intel Silicon Infrastructure Analytics Portal")
st.write("---")

if not filtered_df.empty:
    
    # 🔢 ROW 1: THE THREE CARD METRICS SIDE-BY-SIDE
    col_k1, col_k2, col_k3 = st.columns(3)
    
    avg_rev = filtered_df['Total Revenue (USD)'].mean()
    avg_tdp = filtered_df['TDP (Watts)'].mean()
    avg_cores = filtered_df['Cores'].mean()

    with col_k1:
        st.metric(label="💰 Avg Financial Revenue", value=f"${avg_rev:,.2f}")
    with col_k2:
        st.metric(label="⚡ Avg Thermal Envelope (TDP)", value=f"{avg_tdp:.1f} W")
    with col_k3:
        st.metric(label="🎛️ Avg Computing Cores", value=f"{avg_cores:.1f} Cores")
        
    st.write("---")

    # 📊 ROW 2: PIE CHART & LINE CHART SIDE-BY-SIDE
    col_row2_left, col_row2_right = st.columns(2)
    
    with col_row2_left:
        st.markdown("### 🍕 Share of Units Sold by Processor Series")
        pie_data = filtered_df.groupby('Series')['Units Sold'].sum().reset_index()
        fig_pie = px.pie(pie_data, names='Series', values='Units Sold', template='plotly_white')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_row2_right:
        st.markdown("### 📈 Revenue Performance Trend Over Time")
        time_data = filtered_df.groupby('Date')['Total Revenue (USD)'].sum().reset_index()
        fig_line = px.line(time_data, x='Date', y='Total Revenue (USD)', labels={'Total Revenue (USD)': 'Revenue ($)'}, template='plotly_white')
        st.plotly_chart(fig_line, use_container_width=True)

    st.write("---")

    # 📊 ROW 3: BAR GRAPH & DOTTED PLOT SIDE-BY-SIDE
    col_row3_left, col_row3_right = st.columns(2)
    
    with col_row3_left:
        st.markdown("### 📊 Gross Revenue Contributions by Region")
        bar_data = filtered_df.groupby('Region')['Total Revenue (USD)'].sum().reset_index()
        fig_bar = px.bar(bar_data, x='Region', y='Total Revenue (USD)', labels={'Total Revenue (USD)': 'Gross Yield ($)'}, template='plotly_white')
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_row3_right:
        st.markdown("### 📍 Cores vs TDP Configuration Matrix (Dotted Graph)")
        fig_scatter = px.scatter(
            filtered_df, x='Cores', y='TDP (Watts)', color='Series', hover_name='Model',
            labels={'Cores': 'Core Count', 'TDP (Watts)': 'TDP (Watts)'}, template='plotly_white'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.write("---")
    st.markdown("### 📋 Filtered System Data Ledger")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("⚠️ Workspace empty. Adjust filter options to reload.")
