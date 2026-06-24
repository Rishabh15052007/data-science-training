import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------
# 1. CRISP LIGHT WORKSPACE INITIALIZATION
# ------------------------------------
st.set_page_config(
    page_title="Intel Silicon Architecture Analytics",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Overriding backgrounds completely for a premium, clean presentation
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }
    .stMarkdown h3 {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        margin-top: 10px !important;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------
# 2. DATA LOADING PIPELINE
# ------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("inteldsdashboard/intelds_cleaned.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Units Sold'] = df['Units Sold'].fillna(0)
    df['Total Revenue (USD)'] = df['Total Revenue (USD)'].fillna(0)
    df['TDP (Watts)'] = df['TDP (Watts)'].fillna(0)
    df['Cores'] = df['Cores'].fillna(0)
    df['Unit Price (USD)'] = df['Unit Price (USD)'].fillna(0)
    df['Year'] = df['Year'].fillna(df['Date'].dt.year)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Missing data repository file. Please verify folder paths.")
    st.stop()

# ------------------------------------
# 3. SIDEBAR WORKSPACE CONTROLS
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

# Data Filtering Rules
filtered_df = df[
    (df['Year'].isin(selected_years)) &
    (df['Region'].isin(selected_regions)) &
    (df['Segment'].isin(selected_segments)) &
    (df['Series'].isin(selected_series))
]
if search_model:
    filtered_df = filtered_df[filtered_df['Model'].str.contains(search_model, case=False, na=False)]

# ------------------------------------
# 4. HEADERS & PERFORMANCE TILES
# ------------------------------------
st.title("💻 Intel Silicon Infrastructure Analytics Portal")
st.write("---")

if not filtered_df.empty:
    col_k1, col_k2, col_k3 = st.columns(3)
    with col_k1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="💰 Avg Financial Revenue", value=f"${filtered_df['Total Revenue (USD)'].mean():,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_k2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="⚡ Avg Thermal Envelope", value=f"{filtered_df['TDP (Watts)'].mean():.1f} W")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_k3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="🎛️ Avg Physical Cores", value=f"{filtered_df['Cores'].mean():.1f} Cores")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.write("---")

    # ------------------------------------
    # 5. THE 8 SPECIFIC GRID DIAGRAMS
    # ------------------------------------
    
    # --- ROW 1: Pie & Line (Classic Set) ---
    r1_left, r1_right = st.columns(2)
    with r1_left:
        st.markdown("### 1. 🍕 Share of Units Sold by Processor Series")
        pie_data = filtered_df.groupby('Series')['Units Sold'].sum().reset_index()
        fig1 = px.pie(pie_data, names='Series', values='Units Sold', template='plotly_white',
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)
        
    with r1_right:
        st.markdown("### 2. 📈 Revenue Performance Trajectory Over Time")
        time_data = filtered_df.groupby('Date')['Total Revenue (USD)'].sum().reset_index()
        fig2 = px.line(time_data, x='Date', y='Total Revenue (USD)', template='plotly_white',
                       color_discrete_sequence=['#1d4ed8'])
        st.plotly_chart(fig2, use_container_width=True)

    st.write("---")

    # --- ROW 2: Bar & Scatter (Classic Set) ---
    r2_left, r2_right = st.columns(2)
    with r2_left:
        st.markdown("### 3. 📊 Gross Revenue Contributions by Region")
        bar_data = filtered_df.groupby('Region')['Total Revenue (USD)'].sum().reset_index()
        fig3 = px.bar(bar_data, x='Region', y='Total Revenue (USD)', template='plotly_white',
                      color_discrete_sequence=['#0d9488'])
        st.plotly_chart(fig3, use_container_width=True)
        
    with r2_right:
        st.markdown("### 4. 📍 Dotted Graph: Cores vs TDP Configuration Matrix")
        fig4 = px.scatter(filtered_df, x='Cores', y='TDP (Watts)', color='Series', hover_name='Model',
                          template='plotly_white', color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig4, use_container_width=True)

    st.write("---")

    # --- ROW 3: NEW Grouped Bar & NEW Violin Plot ---
    r3_left, r3_right = st.columns(2)
    with r3_left:
        st.markdown("### 5. 📊 Grouped Bar Graph: Units Sold per Region by Variant Series")
        grouped_data = filtered_df.groupby(['Region', 'Series'])['Units Sold'].sum().reset_index()
        fig5 = px.bar(grouped_data, x='Region', y='Units Sold', color='Series', barmode='group',
                      template='plotly_white', color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig5, use_container_width=True)
        
    with r3_right:
        st.markdown("### 6. 🎻 Violin Plot: Pricing Density Spread Across Regional Markets")
        fig6 = px.violin(filtered_df, x='Region', y='Unit Price (USD)', color='Region', box=True,
                         template='plotly_white', color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig6, use_container_width=True)

    st.write("---")

    # --- ROW 4: NEW Multi-Line Timeline & NEW Horizontal Bar ---
    r4_left, r4_right = st.columns(2)
    with r4_left:
        st.markdown("### 7. 📈 Multi-Line Graph: Average TDP Envelope Tracking by Production Year")
        year_tdp_data = filtered_df.groupby(['Year', 'Series'])['TDP (Watts)'].mean().reset_index()
        fig7 = px.line(year_tdp_data, x='Year', y='TDP (Watts)', color='Series', markers=True,
                       template='plotly_white', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig7, use_container_width=True)
        
    with r4_right:
        st.markdown("### 8. 📊 Horizontal Bar Chart: Total Production Volume by Core Layout Configurations")
        core_vol_data = filtered_df.groupby('Cores')['Units Sold'].sum().reset_index().sort_values(by='Units Sold', ascending=True)
        core_vol_data['Cores'] = core_vol_data['Cores'].astype(str) + " Cores"
        fig8 = px.bar(core_vol_data, x='Units Sold', y='Cores', orientation='h',
                      template='plotly_white', color_discrete_sequence=['#4f46e5'])
        st.plotly_chart(fig8, use_container_width=True)

    st.write("---")
    st.markdown("### 📋 Filtered System Data Ledger")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("⚠️ Workspace empty. Adjust active filters to populate your graphics panels.")
