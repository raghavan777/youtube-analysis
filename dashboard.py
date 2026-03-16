import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
import io
import re
import textwrap
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import gridspec
from PIL import Image
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


def sanitize_pdf_text(value):
    text = "" if value is None else str(value)
    return re.sub(r"[^\x00-\x7F]+", "", text)


def format_compact_number(value):
    abs_value = abs(float(value))
    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"


def safe_report_filename(title, suffix):
    base_name = sanitize_pdf_text(title).strip().replace(" ", "_")
    base_name = re.sub(r"[^A-Za-z0-9._-]+", "_", base_name)
    base_name = re.sub(r"_+", "_", base_name).strip("._")
    if not base_name:
        base_name = "youtube_report"
    return f"{base_name}_{suffix}"


def build_pdf_report(channel_details, filtered_df):
    pdf_buffer = io.BytesIO()
    report_df = filtered_df.copy().sort_values("Published Date")
    page_images = []
    generated_at = dt.datetime.now()
    report_start = report_df["Published Date"].min().strftime("%Y-%m-%d")
    report_end = report_df["Published Date"].max().strftime("%Y-%m-%d")
    page_bg = "#120a24"
    accent = "#8b3dff"
    accent_soft = "#b58cff"
    text_primary = "#f7f3ff"
    text_muted = "#b7a6df"
    highlight = "#ff8fab"

    def style_axes(ax):
        ax.set_facecolor(page_bg)
        for spine in ax.spines.values():
            spine.set_color("#3b245d")
        ax.tick_params(colors=text_muted, labelsize=8)
        ax.yaxis.label.set_color(text_muted)
        ax.xaxis.label.set_color(text_muted)
        ax.title.set_color(text_primary)

    def add_page_footer(fig, page_no):
        footer = (
            f"YouTube Insight Hub - Report for {sanitize_pdf_text(channel_details['title'])} "
            f"- Period {report_start} to {report_end} - Generated {generated_at:%d %b %Y %H:%M} "
            f"- Page {page_no}"
        )
        fig.text(0.5, 0.02, footer, ha="center", va="bottom", fontsize=8, color=accent_soft)
        fig.add_artist(
            plt.Line2D([0.05, 0.95], [0.045, 0.045], transform=fig.transFigure, color=accent_soft, linewidth=1.2)
        )

    def append_pdf_page(fig):
        image_buffer = io.BytesIO()
        fig.savefig(image_buffer, format="png", dpi=200, facecolor=fig.get_facecolor())
        image_buffer.seek(0)
        page_images.append(Image.open(image_buffer).convert("RGB").copy())
        image_buffer.close()
        plt.close(fig)

    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    outer = gridspec.GridSpec(
        5,
        1,
        height_ratios=[1.0, 1.0, 2.2, 2.4, 1.7],
        hspace=0.35,
        top=0.96,
        bottom=0.08,
        left=0.05,
        right=0.97,
    )

    header_ax = fig.add_subplot(outer[0])
    header_ax.set_facecolor(page_bg)
    header_ax.set_xticks([])
    header_ax.set_yticks([])
    for spine in header_ax.spines.values():
        spine.set_visible(False)
    header_ax.text(0.02, 0.62, "YouTube Insight Hub", color=text_primary, fontsize=19, fontweight="bold", transform=header_ax.transAxes)
    header_ax.text(0.98, 0.68, sanitize_pdf_text(channel_details["title"]), color=text_primary, fontsize=10, fontweight="bold", ha="right", transform=header_ax.transAxes)
    header_ax.text(0.98, 0.42, f"Channel ID: {sanitize_pdf_text(st.session_state.get('single_channel_id', ''))}", color=text_muted, fontsize=8, ha="right", transform=header_ax.transAxes)
    header_ax.text(0.98, 0.18, f"{format_compact_number(int(channel_details['subscribers']))} subscribers", color=text_muted, fontsize=9, ha="right", transform=header_ax.transAxes)

    meta_ax = fig.add_subplot(outer[1])
    meta_ax.axis("off")
    meta_ax.text(0.01, 0.72, f"Report period: {report_start} to {report_end}", fontsize=8.5, color="#5e4aa1", fontweight="bold")
    meta_ax.text(0.99, 0.72, f"Generated {generated_at:%d %b %Y, %H:%M}", fontsize=8.5, color="#5e4aa1", ha="right")
    meta_ax.text(0.01, 0.18, "CHANNEL METRICS", fontsize=8.2, color=accent_soft, fontweight="bold")

    metrics_ax = fig.add_subplot(outer[1], frame_on=False)
    metrics_ax.set_xlim(0, 1)
    metrics_ax.set_ylim(0, 1)
    metrics_ax.axis("off")
    metric_labels = [
        ("TOTAL VIEWS", format_compact_number(int(report_df["views"].sum()))),
        ("TOTAL VIDEOS", f"{len(report_df)}"),
        ("TOTAL LIKES", format_compact_number(int(report_df["likes"].sum()))),
        ("TOTAL COMMENTS", format_compact_number(int(report_df["comments"].sum()))),
        ("ENGAGEMENT", f"{report_df['engagement'].mean() * 100:.1f}%"),
        ("AVG VIEWS/VID", format_compact_number(report_df["views"].mean())),
    ]
    card_y = 0.05
    card_h = 0.55
    card_w = 0.155
    start_x = 0.01
    gap = 0.01
    for index, (label, value) in enumerate(metric_labels):
        x = start_x + index * (card_w + gap)
        metrics_ax.add_patch(plt.Rectangle((x, card_y), card_w, card_h, facecolor=page_bg, edgecolor=accent_soft, linewidth=0.8))
        metrics_ax.text(x + 0.02, card_y + 0.38, label, color="#7f73aa", fontsize=6.5, fontweight="bold")
        metrics_ax.text(x + 0.02, card_y + 0.09, value, color=highlight if label == "ENGAGEMENT" else text_primary, fontsize=15, fontweight="bold")

    charts_title_ax = fig.add_subplot(outer[2], frame_on=False)
    charts_title_ax.axis("off")
    charts_title_ax.text(0.01, 1.05, "ANALYTICS CHARTS", fontsize=8.2, color=accent_soft, fontweight="bold")

    charts_grid = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer[2], wspace=0.08, width_ratios=[1.35, 1])
    trend_ax = fig.add_subplot(charts_grid[0])
    style_axes(trend_ax)
    monthly_df = report_df.resample("ME", on="Published Date").size().reset_index(name="videos")
    trend_ax.plot(monthly_df["Published Date"], monthly_df["videos"], color=accent, linewidth=2.2)
    trend_ax.fill_between(monthly_df["Published Date"], monthly_df["videos"], color=accent, alpha=0.18)
    trend_ax.set_title("Upload Trend - Videos per Month", loc="left", fontsize=9)
    trend_ax.grid(color="#2a1745", alpha=0.7, linewidth=0.5)
    trend_ax.set_xlabel("")
    trend_ax.set_ylabel("")

    donut_ax = fig.add_subplot(charts_grid[1])
    donut_ax.set_facecolor(page_bg)
    donut_ax.set_aspect("equal")
    engagement_totals = [report_df["views"].sum(), report_df["likes"].sum(), report_df["comments"].sum()]
    donut_labels = ["Views", "Likes", "Comments"]
    donut_colors = [accent_soft, accent, "#d78bff"]
    wedges, _, autotexts = donut_ax.pie(
        engagement_totals,
        startangle=120,
        colors=donut_colors,
        wedgeprops=dict(width=0.38, edgecolor=page_bg),
        autopct=lambda pct: f"{pct:.1f}%" if pct >= 4 else "",
        textprops=dict(color=text_primary, fontsize=8),
    )
    for text in autotexts:
        text.set_color(text_primary)
        text.set_fontsize(7)
    donut_ax.set_title("Engagement Breakdown", loc="left", color=text_primary, fontsize=9)
    donut_ax.legend(wedges, donut_labels, loc="center left", bbox_to_anchor=(0.82, 0.5), frameon=False, labelcolor=text_muted, fontsize=7)

    bar_wrap = gridspec.GridSpecFromSubplotSpec(1, 1, subplot_spec=outer[3])
    bar_ax = fig.add_subplot(bar_wrap[0])
    style_axes(bar_ax)
    top_videos = report_df.nlargest(8, "views").sort_values("views")
    bar_titles = [sanitize_pdf_text(title[:26] + ("..." if len(title) > 26 else "")) for title in top_videos["title"]]
    bar_ax.barh(bar_titles, top_videos["views"], color=[accent if i < len(bar_titles) - 2 else accent_soft for i in range(len(bar_titles))])
    bar_ax.set_title("TOP VIDEOS CHART", loc="left", fontsize=8.5, color=accent_soft, pad=10, fontweight="bold")
    bar_ax.grid(axis="x", color="#2a1745", alpha=0.7, linewidth=0.5)
    bar_ax.tick_params(axis="y", labelsize=7)
    for idx, value in enumerate(top_videos["views"]):
        bar_ax.text(value, idx, f" {format_compact_number(value)}", va="center", color=text_primary, fontsize=7)

    table_ax = fig.add_subplot(outer[4])
    table_ax.set_facecolor(page_bg)
    table_ax.axis("off")
    table_ax.text(0.0, 1.08, "TOP 10 VIDEOS - DETAILED TABLE", fontsize=8.2, color=accent_soft, fontweight="bold", transform=table_ax.transAxes)
    table_df = report_df.nlargest(4, "views")[["title", "views", "likes", "comments"]].copy()
    table_df.insert(0, "#", range(1, len(table_df) + 1))
    table_df["title"] = table_df["title"].apply(lambda value: sanitize_pdf_text(value[:48] + ("..." if len(value) > 48 else "")))
    table_df["views"] = table_df["views"].map(lambda value: f"{int(value):,}")
    table_df["likes"] = table_df["likes"].map(lambda value: f"{int(value):,}")
    table_df["comments"] = table_df["comments"].map(lambda value: f"{int(value):,}")
    table = table_ax.table(
        cellText=table_df.values,
        colLabels=["", "Title", "Views", "Likes", "Comments"],
        cellLoc="left",
        colLoc="left",
        loc="upper left",
        bbox=[0, 0.02, 1, 0.9],
        colWidths=[0.04, 0.50, 0.12, 0.12, 0.12],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#3b245d")
        cell.set_linewidth(0.6)
        if row == 0:
            cell.set_facecolor(accent)
            cell.get_text().set_color(text_primary)
            cell.get_text().set_fontweight("bold")
        else:
            cell.set_facecolor(page_bg)
            cell.get_text().set_color(text_primary)

    add_page_footer(fig, 1)
    append_pdf_page(fig)

    page_two = report_df.nlargest(20, "views")[["title", "views", "likes", "comments", "Published Date"]].copy()
    page_two["Duration"] = "--"
    page_two["title"] = page_two["title"].apply(lambda value: "\n".join(textwrap.wrap(sanitize_pdf_text(value), 42))[:110])
    page_two["views"] = page_two["views"].map(lambda value: f"{int(value):,}")
    page_two["likes"] = page_two["likes"].map(lambda value: f"{int(value):,}")
    page_two["comments"] = page_two["comments"].map(lambda value: f"{int(value):,}")
    page_two["Published Date"] = page_two["Published Date"].dt.strftime("%Y-%m-%d")
    page_two.insert(0, "#", range(1, len(page_two) + 1))

    fig2 = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    ax2 = fig2.add_axes([0.04, 0.06, 0.92, 0.9])
    ax2.set_facecolor(page_bg)
    ax2.axis("off")
    table2 = ax2.table(
        cellText=page_two[["#", "title", "views", "likes", "comments", "Duration"]].values,
        colLabels=["#", "Title", "Views", "Likes", "Comments", "Duration"],
        cellLoc="left",
        colLoc="left",
        loc="upper left",
        bbox=[0, 0.06, 1, 0.9],
        colWidths=[0.04, 0.46, 0.14, 0.12, 0.12, 0.12],
    )
    table2.auto_set_font_size(False)
    table2.set_fontsize(7)
    for (row, col), cell in table2.get_celld().items():
        cell.set_edgecolor("#3b245d")
        cell.set_linewidth(0.5)
        if row == 0:
            cell.set_facecolor(accent)
            cell.get_text().set_color(text_primary)
            cell.get_text().set_fontweight("bold")
        else:
            cell.set_facecolor(page_bg)
            cell.get_text().set_color(text_primary)
            if col == 1:
                cell.PAD = 0.02
    add_page_footer(fig2, 2)
    append_pdf_page(fig2)

    page_images[0].save(pdf_buffer, format="PDF", resolution=100.0, save_all=True, append_images=page_images[1:])
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


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
            search_query = st.sidebar.text_input("🔍 Search Video Title", placeholder="e.g. Streamlit", value="")
            min_views = st.sidebar.slider("Minimum Views", min_value=0, max_value=int(df['views'].max()), value=0)
            years = df['Year'].unique()
            selected_years = st.sidebar.multiselect("Filter by Year", years, default=years)

            filtered_df = df[(df["views"] >= min_views) & (df["Year"].isin(selected_years))].copy()
            if search_query:
                filtered_df = filtered_df[filtered_df["title"].str.contains(search_query, case=False, na=False)]

            if filtered_df.empty:
                st.warning("No videos match the filters.", icon="🙈")
            else:
                st.subheader("📊 Advanced Visualizations")
                
                v_col1, v_col2 = st.columns(2)
                
                with v_col1:
                    st.markdown("**Views Growth Pattern**")
                    filtered_df_sorted = filtered_df.sort_values(by="Published Date")
                    
                    fig_trend = px.line(filtered_df_sorted, x="Published Date", y="views", template=CHART_THEME, color_discrete_sequence=['#00F2FE'], markers=True)
                    apply_transparent_bg(fig_trend)
                    # Smoothed spline curve with filled area underneath
                    fig_trend.update_traces(line_shape='spline', fill='tozeroy', fillcolor='rgba(0, 242, 254, 0.1)', line=dict(width=3))
                    fig_trend.update_yaxes(title_text="Total Views")
                    st.plotly_chart(fig_trend, use_container_width=True)

                    st.markdown("**Engagement Density**")
                    # Use Inferno so 0-values map to dark background, blending perfectly
                    fig_heat = px.density_heatmap(
                        filtered_df, x="views", y="engagement", 
                        nbinsx=15, nbinsy=15, 
                        template=CHART_THEME, color_continuous_scale="Inferno"
                    )
                    apply_transparent_bg(fig_heat)
                    fig_heat.update_layout(xaxis_title="Views", yaxis_title="Engagement Rate")
                    st.plotly_chart(fig_heat, use_container_width=True)

                with v_col2:
                    st.markdown("**Top 10 Performing Videos**")
                    top10 = filtered_df.sort_values("views", ascending=False).head(10).copy()
                    # Shorten titles to prevent chart squashing
                    top10['Short Title'] = top10['title'].apply(lambda x: x[:35] + '...' if len(x) > 35 else x)
                    
                    fig_bar = px.bar(top10, x="views", y="Short Title", orientation='h', text_auto='.2s', template=CHART_THEME, color_discrete_sequence=['#4FACFE'])
                    apply_transparent_bg(fig_bar)
                    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, yaxis_title="")
                    st.plotly_chart(fig_bar, use_container_width=True)

                    st.markdown("**Interaction Breakdown**")
                    # Make scatter axes meaningful: views vs engagement
                    q95_likes = filtered_df['likes'].quantile(0.95) if not filtered_df.empty else 1000
                    filtered_df['likes_clamped'] = filtered_df['likes'].clip(upper=q95_likes)
                    
                    # Use a punchy color scale like Sunsetdark
                    fig_scatter = px.scatter(
                        filtered_df, x="views", y="engagement", size="likes_clamped", 
                        hover_data=["title", "likes", "comments"], color="engagement", 
                        template=CHART_THEME, color_continuous_scale="Sunsetdark"
                    )
                    apply_transparent_bg(fig_scatter)
                    fig_scatter.update_layout(xaxis_title="Views", yaxis_title="Engagement Rate")
                    # Increase marker border for visibility
                    fig_scatter.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
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
                        if 'reaction' in t: return 'Reaction'
                        if 'trailer' in t or 'teaser' in t: return 'Trailer/Teaser'
                        if 'song' in t or 'music' in t: return 'Music'
                        if 'comedy' in t or 'funny' in t: return 'Comedy'
                        if 'live' in t or 'stream' in t: return 'Live'
                        if '#shorts' in t or 'shorts' in t: return 'Shorts'
                        if 'podcast' in t or 'interview' in t: return 'Podcast'
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

                # Video Data Table
                st.subheader("📑 Video Database")
                st.markdown("Explore and filter specific videos from the dataset.")
                
                # Select formatting for presenting the dataframe beautifully
                display_df = filtered_df[['title', 'Published Date', 'views', 'likes', 'comments', 'engagement']].copy()
                display_df.rename(columns={
                    'title': 'Video Title',
                    'views': 'Views',
                    'likes': 'Likes',
                    'comments': 'Comments',
                    'engagement': 'Engagement Rate'
                }, inplace=True)
                
                # Format the Engagement Rate to percentage for the progress column
                display_df['Engagement Rate'] = display_df['Engagement Rate'] * 100
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=400,
                    hide_index=True,
                    column_config={
                        "Views": st.column_config.NumberColumn(format="%d"),
                        "Likes": st.column_config.NumberColumn(format="%d"),
                        "Comments": st.column_config.NumberColumn(format="%d"),
                        "Engagement Rate": st.column_config.ProgressColumn(
                            "Engagement (%)",
                            help="Engagement rate percentage",
                            format="%.2f%%",
                            min_value=0,
                            max_value=max(display_df['Engagement Rate'].max(), 5)
                        ),
                        "Published Date": st.column_config.DatetimeColumn(format="MMM DD, YYYY")
                    }
                )
                
                st.markdown("<hr>", unsafe_allow_html=True)

                # Download Feature
                st.subheader("💡 Export Intelligence")
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                pdf_bytes = build_pdf_report(channel_details, filtered_df)
                csv_file_name = safe_report_filename(channel_details["title"], "analytics.csv")
                pdf_file_name = safe_report_filename(channel_details["title"], "insight_report.pdf")
                export_col1, export_col2 = st.columns(2)
                with export_col1:
                    st.download_button(
                        label="📥 Download Insight Matrix as CSV",
                        data=csv,
                        file_name=csv_file_name,
                        mime="text/csv",
                        use_container_width=True,
                    )
                with export_col2:
                    st.download_button(
                        label="📄 Download Insight Report as PDF",
                        data=pdf_bytes,
                        file_name=pdf_file_name,
                        mime="application/pdf",
                        use_container_width=True,
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
