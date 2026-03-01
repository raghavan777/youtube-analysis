import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
import requests
from streamlit_lottie import st_lottie
from main import get_channel_data

st.set_page_config(page_title="YouTube Analytics Pro", layout="wide", page_icon="🔴")

# --- CUSTOM CSS FOR MODERN UI ---
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Outfit', sans-serif;
}

/* Advanced CSS Animations */
@keyframes fadeInUp {
    0% {
        opacity: 0;
        transform: translateY(20px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 15px rgba(0, 242, 254, 0.4); }
    50% { box-shadow: 0 0 25px rgba(0, 242, 254, 0.7); }
    100% { box-shadow: 0 0 15px rgba(0, 242, 254, 0.4); }
}

@keyframes slideInRight {
    0% {
        opacity: 0;
        transform: translateX(30px);
    }
    100% {
        opacity: 1;
        transform: translateX(0);
    }
}

/* Glassmorphism for KPI Cards */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border 0.3s ease;
    animation: fadeInUp 0.6s ease-out forwards;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(0, 242, 254, 0.15);
    border: 1px solid rgba(0, 242, 254, 0.4);
}

[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    background: -webkit-linear-gradient(45deg, #00F2FE, #4FACFE);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Gradient Titles & Markdown formatting */
h1, h2, h3, h4, .stMarkdown p strong {
    background: -webkit-linear-gradient(45deg, #0072ff, #00c6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
}

/* Button Upgrades */
.stButton > button {
    border-radius: 50px !important;
    background: linear-gradient(90deg, #0072ff 0%, #00c6ff 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    border: none !important;
    animation: pulseGlow 2.5s infinite;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 6px 20px rgba(255, 65, 108, 0.6) !important;
}

/* Styled sidebar */
[data-testid="stSidebar"] {
    background-color: rgba(10, 10, 15, 0.95);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    animation: slideInRight 0.5s ease-out forwards;
}

/* Plotly charts wrap animation */
.stPlotlyChart {
    animation: fadeInUp 0.8s ease-out forwards;
}
</style>
""", unsafe_allow_html=True)


# --- HELPER FUNCTIONS ---
def load_lottieurl(url: str):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Lottie loading animation
lottie_loading = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_f1dhegm9.json")


def calculate_performance_score(df):
    if df.empty:
        return 0
    avg_engagement = df['engagement'].mean()
    avg_views = df['views'].mean()
    
    df_copy = df.copy()
    if 'Published Date' not in df_copy.columns:
        df_copy['Published Date'] = pd.to_datetime(df_copy['publishedAt']).dt.tz_localize(None)
    min_date = df_copy['Published Date'].min()
    max_date = df_copy['Published Date'].max()
    months = (max_date.year - min_date.year) * 12 + max_date.month - min_date.month
    months = max(1, months)
    upload_consistency = len(df_copy) / months 
    
    normalized_engagement = min(avg_engagement * 1000, 100) 
    normalized_views = min(avg_views / 1000, 100) 
    normalized_consistency = min(upload_consistency * 10, 100) 
    
    score = (normalized_engagement * 0.4) + (normalized_views * 0.3) + (normalized_consistency * 0.3)
    return min(int(score), 100)

@st.cache_data(ttl=3600, show_spinner=False)
def render_channel_analysis(channel_id):
    channel_details, df = get_channel_data(channel_id)

    if channel_details is None:
        return None, None

    if not df.empty:
        df['Published Date'] = pd.to_datetime(df['publishedAt']).dt.tz_localize(None)
        df['Day'] = df['Published Date'].dt.day_name()
        df['Year'] = df['Published Date'].dt.year

    return channel_details, df


# --- PLOTLY THEME SETTINGS ---
CHART_THEME = "plotly_dark"
CHART_COLOR_SEQ = px.colors.qualitative.Pastel
def apply_transparent_bg(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Outfit"
    )
    return fig


# --- SIDEBAR & HEADER ---
with st.sidebar:
    st.header("Settings")
    mode = st.radio("Mode", ["Single Channel Analysis", "Compare Channels"])

st.title("YouTube Analytics Pro 🚀")

# --- MAIN UI LOGIC ---
if mode == "Single Channel Analysis":
    input_channel_id = st.text_input("Enter YouTube Channel ID", placeholder="e.g. UC_x5XG1OV2P6uZZ5FSM9Ttw", value=st.session_state.get('single_channel_id', ''))
    
    if st.button("✨ Analyze Channel"):
        if not input_channel_id:
            st.warning("Please enter a Channel ID", icon="⚠️")
            st.session_state.single_channel_id = None
        else:
            st.session_state.single_channel_id = input_channel_id

    if st.session_state.get('single_channel_id'):
        channel_id = st.session_state.single_channel_id

        # Loading State
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            if lottie_loading:
                st_lottie(lottie_loading, height=200, key="loading")
            st.markdown("<h3 style='text-align: center;'>Fetching AI Insights...</h3>", unsafe_allow_html=True)
            
        channel_details, df = render_channel_analysis(channel_id)
        loading_placeholder.empty()

        if not channel_details:
            st.error(f"Invalid Channel ID: {channel_id}", icon="🚨")
            st.stop()

        # Success Effects
        st.toast(f"Successfully loaded data for: **{channel_details['title']}**", icon="🎉")

        # KPIs
        st.markdown(f"## 📌 Overview: {channel_details['title']}")
        
        col1, col2, col3, col4 = st.columns(4)
        subscribers = int(channel_details["subscribers"])
        views = int(channel_details["views"])
        videos = int(channel_details["videos"])
        avg_engagement = df['engagement'].mean() if not df.empty else 0

        col1.metric("👥 Subscribers", f"{subscribers:,}")
        col2.metric("👁️ Total Views", f"{views:,}")
        col3.metric("🎬 Total Videos", f"{videos:,}")
        col4.metric("📈 Avg Engagement", f"{avg_engagement:.2%}")

        st.markdown("<br>", unsafe_allow_html=True)

        if not df.empty:
            # Performance Score
            score = calculate_performance_score(df)
            st.markdown(f"### 🏆 Elite Performance Score: {score}/100")
            st.progress(score / 100)

            st.markdown("<br><hr>", unsafe_allow_html=True)

            # FILTERS
            st.sidebar.subheader("🎯 Refine Data")
            min_views = st.sidebar.slider("Minimum Views", min_value=0, max_value=int(df['views'].max()), value=0)
            years = df['Year'].unique()
            selected_years = st.sidebar.multiselect("Filter by Year", years, default=years)

            filtered_df = df[(df["views"] >= min_views) & (df["Year"].isin(selected_years))].copy()

            if filtered_df.empty:
                st.warning("No videos match the filters.", icon="🙈")
            else:
                st.subheader("📊 Advanced Visualizations")
                
                v_col1, v_col2 = st.columns(2)
                
                with v_col1:
                    st.markdown("**Views Growth Pattern (Log Scale)**")
                    filtered_df_sorted = filtered_df.sort_values(by="Published Date")
                    
                    # Prevent log scale errors by adding a tiny epsilon if views are 0
                    filtered_df_sorted['views_log_safe'] = filtered_df_sorted['views'].apply(lambda x: x if x > 0 else 1)
                    
                    fig_trend = px.line(filtered_df_sorted, x="Published Date", y="views_log_safe", log_y=True, template=CHART_THEME, color_discrete_sequence=CHART_COLOR_SEQ)
                    apply_transparent_bg(fig_trend)
                    # Add gradient fill under line
                    fig_trend.update_traces(fill='tozeroy', line=dict(width=3))
                    fig_trend.update_yaxes(title_text="Views (Log Scale)")
                    st.plotly_chart(fig_trend, use_container_width=True)

                    st.markdown("**Engagement Density**")
                    # Replace histogram with a 2D density heatmap
                    fig_heat = px.density_heatmap(
                        filtered_df, x="views", y="engagement", 
                        nbinsx=20, nbinsy=20, 
                        template=CHART_THEME, color_continuous_scale="Purpor"
                    )
                    apply_transparent_bg(fig_heat)
                    st.plotly_chart(fig_heat, use_container_width=True)

                with v_col2:
                    st.markdown("**Top 10 Performing Videos**")
                    top10 = filtered_df.sort_values("views", ascending=False).head(10)
                    # Add precise labels with text_auto
                    fig_bar = px.bar(top10, x="views", y="title", orientation='h', text_auto='.2s', template=CHART_THEME, color_discrete_sequence=['#8E2DE2'])
                    apply_transparent_bg(fig_bar)
                    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_bar, use_container_width=True)

                    st.markdown("**Interaction Breakdown**")
                    # Make scatter axes meaningful: views vs engagement
                    # Cap sizes to prevent massive outliers from breaking the chart visuals
                    q95_likes = filtered_df['likes'].quantile(0.95) if not filtered_df.empty else 1000
                    filtered_df['likes_clamped'] = filtered_df['likes'].clip(upper=q95_likes)
                    
                    fig_scatter = px.scatter(
                        filtered_df, x="views", y="engagement", size="likes_clamped", 
                        hover_data=["title", "likes", "comments"], color="comments", 
                        template=CHART_THEME, color_continuous_scale="Agsunset"
                    )
                    apply_transparent_bg(fig_scatter)
                    fig_scatter.update_layout(xaxis_title="Views", yaxis_title="Engagement Rate")
                    st.plotly_chart(fig_scatter, use_container_width=True)

                st.markdown("<hr>", unsafe_allow_html=True)
                
                # Smart Analytics
                st.header("🧠 Smart Analytics")
                
                s_col1, s_col2, s_col3 = st.columns(3)
                
                with s_col1:
                    st.markdown("### 🏆 Best Upload Period")
                    best_day = filtered_df.groupby("Day")["views"].mean().idxmax()
                    st.success(f"Algorithm favors: **{best_day}**", icon="🔥")
                    
                with s_col2:
                    st.markdown("### 📌 Content Performance")
                    def categorize(title):
                        t = title.lower()
                        if 'tutorial' in t or 'how to' in t: return 'Tutorial'
                        if 'live' in t or 'stream' in t: return 'Live'
                        if '#shorts' in t or 'shorts' in t: return 'Shorts'
                        return 'Other'
                    
                    filtered_df['Content Type'] = filtered_df['title'].apply(categorize)
                    content_perf = filtered_df.groupby('Content Type')['views'].mean().reset_index()
                    fig_content = px.bar(content_perf, x='Content Type', y='views', color="Content Type", template=CHART_THEME, color_discrete_sequence=CHART_COLOR_SEQ)
                    apply_transparent_bg(fig_content)
                    st.plotly_chart(fig_content, use_container_width=True)

                with s_col3:
                    st.markdown("### 📈 Growth Trajectory")
                    min_date = filtered_df['Published Date'].min()
                    max_date = filtered_df['Published Date'].max()
                    months_active = (max_date.year - min_date.year) * 12 + max_date.month - min_date.month
                    months_active = max(1, months_active)
                    avg_monthly_upload = len(filtered_df) / months_active
                    avg_views_per_video = filtered_df['views'].mean()
                    est_next_month_views = avg_monthly_upload * avg_views_per_video
                    st.info(f"Avg Monthly Uploads: **{avg_monthly_upload:.1f}**", icon="📅")
                    st.info(f"Est. Next Month Views: **{est_next_month_views:,.0f}**", icon="🚀")
                
                st.markdown("<hr>", unsafe_allow_html=True)

                # Download Feature
                st.subheader("💡 Export Intelligence")
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Insight Matrix as CSV",
                    data=csv,
                    file_name=f"{channel_details['title']}_analytics.csv",
                    mime="text/csv",
                )


elif mode == "Compare Channels":
    st.header("⚔️ Clash of Creators")
    colA, colB = st.columns(2)
    with colA:
        input_ch1_id = st.text_input("Challenger 1 ID", key="ch1", value=st.session_state.get('compare_ch1_id', ''))
    with colB:
        input_ch2_id = st.text_input("Challenger 2 ID", key="ch2", value=st.session_state.get('compare_ch2_id', ''))

    if st.button("⚡ Commence Battle"):
        if not input_ch1_id or not input_ch2_id:
            st.warning("Please enter both Challenger IDs.", icon="⚔️")
            st.session_state.compare_ch1_id = None
            st.session_state.compare_ch2_id = None
        else:
            st.session_state.compare_ch1_id = input_ch1_id
            st.session_state.compare_ch2_id = input_ch2_id

    if st.session_state.get('compare_ch1_id') and st.session_state.get('compare_ch2_id'):
        ch1_id = st.session_state.compare_ch1_id
        ch2_id = st.session_state.compare_ch2_id

        loading_placeholder = st.empty()
        with loading_placeholder.container():
            if lottie_loading:
                st_lottie(lottie_loading, height=200, key="loading_battle")
            st.markdown("<h3 style='text-align: center;'>Analyzing Opponents...</h3>", unsafe_allow_html=True)

        ch1_details, df1 = render_channel_analysis(ch1_id)
        ch2_details, df2 = render_channel_analysis(ch2_id)
        
        loading_placeholder.empty()

        if not ch1_details or not ch2_details:
            st.error("One or both Channel IDs are invalid.", icon="❌")
            st.stop()
            
        st.toast("Battle analytics ready!", icon="🔥")

        # Side-by-side KPIs
        colA, colB = st.columns(2)
        
        def render_kpis(col, details, df):
            with col:
                st.markdown(f"### {details['title']}")
                subscribers = int(details["subscribers"])
                views = int(details["views"])
                videos = int(details["videos"])
                avg_engagement = df['engagement'].mean() if not df.empty else 0
                score = calculate_performance_score(df)

                st.metric("Subscribers", f"{subscribers:,}")
                st.metric("Total Views", f"{views:,}")
                st.metric("Avg Engagement", f"{avg_engagement:.2%}")
                st.metric("Power Level Score", f"{score}/100")

        render_kpis(colA, ch1_details, df1)
        render_kpis(colB, ch2_details, df2)
        
        st.markdown("<br><hr>", unsafe_allow_html=True)
        st.subheader("📊 Tactical Analysis")
        if not df1.empty and not df2.empty:
            df1['Channel'] = ch1_details['title']
            df2['Channel'] = ch2_details['title']
            combined_df = pd.concat([df1, df2])
            
            # Compare Avg Views Box Plot
            fig_compare_views = px.box(
                combined_df, x="Channel", y="views", 
                color="Channel", 
                template=CHART_THEME,
                color_discrete_sequence=['#FF416C', '#8E2DE2']
            )
            apply_transparent_bg(fig_compare_views)
            st.plotly_chart(fig_compare_views, use_container_width=True)