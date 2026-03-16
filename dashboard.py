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
from PIL import Image
from streamlit_lottie import st_lottie
from main import get_channel_data

st.set_page_config(page_title="YouTube Analytics Pro", layout="wide", page_icon="🔴")

# --- CUSTOM CSS FOR MODERN UI ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Outfit', sans-serif;
}
h1, h2, h3, h4 { font-family: 'Outfit', sans-serif; }

@keyframes fadeInUp {
    0%   { opacity: 0; transform: translateY(24px); }
    100% { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 18px rgba(124, 58, 237, 0.35); }
    50%      { box-shadow: 0 0 30px rgba(124, 58, 237, 0.65); }
}
@keyframes slideInRight {
    0%   { opacity: 0; transform: translateX(30px); }
    100% { opacity: 1; transform: translateX(0); }
}

/* ---------- KPI Metric Cards ---------- */
[data-testid="stMetric"] {
    background: rgba(124, 58, 237, 0.06);
    border-radius: 18px;
    padding: 22px 24px;
    box-shadow: 0 4px 30px rgba(0,0,0,0.18);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(124, 58, 237, 0.12);
    border-left: 4px solid;
    border-image: linear-gradient(180deg, #7c3aed, #f43f5e) 1;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border 0.3s ease;
    animation: fadeInUp 0.55s ease-out forwards;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 14px 44px rgba(124, 58, 237, 0.22);
    border: 1px solid rgba(124, 58, 237, 0.45);
    border-left: 4px solid;
    border-image: linear-gradient(180deg, #7c3aed, #f43f5e) 1;
}
[data-testid="stMetricValue"] {
    font-size: 2.3rem !important;
    font-weight: 800 !important;
    font-family: 'Outfit', sans-serif !important;
    background: linear-gradient(135deg, #a78bfa, #7c3aed, #f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stMetricLabel"] {
    font-weight: 600 !important;
    letter-spacing: 0.03em;
    opacity: 0.85;
}

/* ---------- Gradient Headings ---------- */
h1, h2, h3, h4, .stMarkdown p strong {
    background: linear-gradient(135deg, #7c3aed, #a78bfa, #f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
}

/* ---------- Buttons ---------- */
.stButton > button {
    border-radius: 50px !important;
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #f43f5e 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.04em;
    border: none !important;
    padding: 0.55rem 1.8rem !important;
    animation: pulseGlow 3s infinite;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: scale(1.06) !important;
    box-shadow: 0 8px 28px rgba(244, 63, 94, 0.5) !important;
}

/* ---------- Download Buttons ---------- */
.stDownloadButton > button {
    border-radius: 50px !important;
    background: linear-gradient(135deg, #7c3aed 0%, #f43f5e 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    border: none !important;
    padding: 0.55rem 1.6rem !important;
    transition: all 0.35s ease !important;
}
.stDownloadButton > button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.5) !important;
    background: linear-gradient(135deg, #f43f5e 0%, #7c3aed 100%) !important;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10, 6, 20, 0.97), rgba(18, 10, 35, 0.97));
    border-right: 1px solid rgba(124, 58, 237, 0.15);
    animation: slideInRight 0.5s ease-out forwards;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdown"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdown"] h3 {
    background: linear-gradient(135deg, #a78bfa, #f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ---------- Charts ---------- */
.stPlotlyChart {
    animation: fadeInUp 0.7s ease-out forwards;
    border-radius: 16px;
}

/* ---------- Dataframe ---------- */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    border: 1px solid rgba(124, 58, 237, 0.12);
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.08);
    animation: fadeInUp 0.6s ease-out forwards;
}

/* ---------- Progress bar ---------- */
.stProgress > div > div {
    background: linear-gradient(90deg, #7c3aed, #a855f7, #f43f5e) !important;
    border-radius: 10px;
}

/* ---------- Gradient Divider ---------- */
.gradient-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #7c3aed, #f43f5e, transparent);
    border: none;
    margin: 2rem 0;
    border-radius: 2px;
}

/* ---------- Toast / Alerts ---------- */
[data-testid="stToast"] {
    border-left: 4px solid #7c3aed !important;
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
CHART_COLOR_SEQ = ["#7c3aed", "#f43f5e", "#f59e0b", "#10b981", "#38bdf8", "#e879f9", "#a78bfa", "#fb7185"]
def apply_transparent_bg(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter",
        font_color="#c4b5fd",
        title_font_color="#e9d5ff",
    )
    return fig


def gradient_divider():
    """Render a gradient divider instead of plain <hr>."""
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)


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
    page_bg = "#0f0a1e"
    card_bg = "#1a1232"
    card_bg_alt = "#241845"
    accent = "#7c3aed"
    accent_soft = "#a78bfa"
    accent_cyan = "#e879f9"
    accent_rose = "#f43f5e"
    text_primary = "#f5f0ff"
    text_muted = "#c4b5fd"
    subtle = "#7e6ba3"

    summary_metrics = [
        ("Total Views", format_compact_number(int(report_df["views"].sum()))),
        ("Videos", f"{len(report_df)}"),
        ("Total Likes", format_compact_number(int(report_df["likes"].sum()))),
        ("Comments", format_compact_number(int(report_df["comments"].sum()))),
        ("Avg Engagement", f"{report_df['engagement'].mean() * 100:.2f}%"),
        ("Avg Views", format_compact_number(report_df["views"].mean())),
    ]
    top_video = report_df.nlargest(1, "views").iloc[0]
    best_day = report_df.groupby("Day")["views"].mean().idxmax() if "Day" in report_df.columns else "N/A"
    monthly_df = report_df.resample("ME", on="Published Date").size().reset_index(name="videos")
    top_videos = report_df.nlargest(8, "views").sort_values("views")

    def new_page():
        fig = plt.figure(figsize=(8.27, 11.69), facecolor=page_bg)
        return fig

    def add_page_number(fig, page_no):
        footer = (
            f"YouTube Insight Hub | {sanitize_pdf_text(channel_details['title'])} | "
            f"{report_start} to {report_end} | Generated {generated_at:%d %b %Y %H:%M} | Page {page_no}"
        )
        fig.text(0.5, 0.022, footer, ha="center", va="bottom", fontsize=8, color=subtle)

    def card_axes(fig, rect, facecolor=card_bg):
        ax = fig.add_axes(rect)
        ax.set_facecolor(facecolor)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        return ax

    def style_axes(ax):
        ax.set_facecolor(card_bg)
        for spine in ax.spines.values():
            spine.set_color("#3d2a6e")
        ax.tick_params(colors=text_muted, labelsize=8)
        ax.yaxis.label.set_color(text_muted)
        ax.xaxis.label.set_color(text_muted)
        ax.title.set_color(text_primary)
        ax.grid(color="#3d2a6e", alpha=0.45, linewidth=0.5)

    def add_section_title(ax, title, subtitle=None):
        ax.text(0.03, 0.92, sanitize_pdf_text(title), color=text_primary, fontsize=11, fontweight="bold", transform=ax.transAxes)
        if subtitle:
            ax.text(0.03, 0.84, sanitize_pdf_text(subtitle), color=text_muted, fontsize=8, transform=ax.transAxes)

    def append_pdf_page(fig):
        image_buffer = io.BytesIO()
        fig.savefig(image_buffer, format="png", dpi=200, facecolor=fig.get_facecolor())
        image_buffer.seek(0)
        page_images.append(Image.open(image_buffer).convert("RGB").copy())
        image_buffer.close()
        plt.close(fig)

    fig = new_page()

    hero_ax = card_axes(fig, [0.05, 0.84, 0.90, 0.11], facecolor=card_bg)
    hero_ax.text(0.03, 0.64, "Insight Report", color=accent_cyan, fontsize=10, fontweight="bold", transform=hero_ax.transAxes)
    hero_ax.text(0.03, 0.18, "YouTube Analytics Pro", color=text_primary, fontsize=22, fontweight="bold", transform=hero_ax.transAxes)
    hero_ax.text(0.97, 0.62, sanitize_pdf_text(channel_details["title"]), color=text_primary, fontsize=12, fontweight="bold", ha="right", transform=hero_ax.transAxes)
    hero_ax.text(0.97, 0.36, f"Channel ID: {sanitize_pdf_text(st.session_state.get('single_channel_id', ''))}", color=text_muted, fontsize=8, ha="right", transform=hero_ax.transAxes)
    hero_ax.text(0.97, 0.14, f"Period {report_start} to {report_end}", color=text_muted, fontsize=8, ha="right", transform=hero_ax.transAxes)

    meta_ax = fig.add_axes([0.05, 0.78, 0.90, 0.04])
    meta_ax.axis("off")
    meta_ax.text(0.00, 0.5, f"Generated {generated_at:%d %b %Y, %H:%M}", color=subtle, fontsize=8.5, va="center")
    meta_ax.text(1.00, 0.5, f"Subscribers {format_compact_number(int(channel_details['subscribers']))}", color=subtle, fontsize=8.5, va="center", ha="right")

    for index, (label, value) in enumerate(summary_metrics):
        x = 0.05 + index * 0.15
        metric_ax = card_axes(fig, [x, 0.68, 0.135, 0.085], facecolor=card_bg_alt if index % 2 else card_bg)
        metric_ax.text(0.08, 0.68, sanitize_pdf_text(label.upper()), color=text_muted, fontsize=7, fontweight="bold", transform=metric_ax.transAxes)
        metric_ax.text(0.08, 0.20, value, color=text_primary, fontsize=16, fontweight="bold", transform=metric_ax.transAxes)

    trend_panel = card_axes(fig, [0.05, 0.42, 0.56, 0.22])
    add_section_title(trend_panel, "Publishing Trend", "Videos published per month")
    trend_ax = fig.add_axes([0.08, 0.455, 0.50, 0.15])
    style_axes(trend_ax)
    trend_ax.plot(monthly_df["Published Date"], monthly_df["videos"], color=accent_cyan, linewidth=2.6, marker="o", markersize=3.2)
    trend_ax.fill_between(monthly_df["Published Date"], monthly_df["videos"], color=accent_cyan, alpha=0.15)
    trend_ax.set_xlabel("")
    trend_ax.set_ylabel("")
    trend_ax.set_title("")

    mix_panel = card_axes(fig, [0.64, 0.42, 0.31, 0.22], facecolor=card_bg_alt)
    add_section_title(mix_panel, "Engagement Mix", "Views, likes and comments share")
    donut_ax = fig.add_axes([0.68, 0.465, 0.16, 0.13])
    donut_ax.set_facecolor(card_bg_alt)
    for spine in donut_ax.spines.values():
        spine.set_visible(False)
    donut_ax.set_aspect("equal")
    donut_values = [report_df["views"].sum(), report_df["likes"].sum(), report_df["comments"].sum()]
    donut_labels = ["Views", "Likes", "Comments"]
    donut_colors = [accent_soft, accent_cyan, accent_rose]
    wedges, _ = donut_ax.pie(
        donut_values,
        colors=donut_colors,
        startangle=120,
        wedgeprops=dict(width=0.38, edgecolor=card_bg_alt),
    )
    mix_panel.legend(wedges, donut_labels, loc="lower left", bbox_to_anchor=(0.03, 0.06), frameon=False, labelcolor=text_muted, fontsize=8)

    insight_ax = card_axes(fig, [0.05, 0.25, 0.32, 0.13], facecolor=card_bg_alt)
    add_section_title(insight_ax, "Quick Insights")
    insight_ax.text(0.04, 0.60, f"Top video: {sanitize_pdf_text(top_video['title'][:36])}", color=text_primary, fontsize=8.2, transform=insight_ax.transAxes)
    insight_ax.text(0.04, 0.40, f"Views on top video: {int(top_video['views']):,}", color=text_muted, fontsize=8.2, transform=insight_ax.transAxes)
    insight_ax.text(0.04, 0.22, f"Best upload day: {sanitize_pdf_text(best_day)}", color=text_muted, fontsize=8.2, transform=insight_ax.transAxes)

    ranking_panel = card_axes(fig, [0.40, 0.25, 0.55, 0.13])
    add_section_title(ranking_panel, "Top Videos by Views")
    rank_ax = fig.add_axes([0.44, 0.275, 0.47, 0.08])
    style_axes(rank_ax)
    rank_titles = [sanitize_pdf_text(title[:30] + ("..." if len(title) > 30 else "")) for title in top_videos["title"]]
    rank_ax.barh(rank_titles, top_videos["views"], color=[accent, accent, accent_soft, accent_soft, accent_cyan, accent_cyan, "#67e8f9", "#c4b5fd"])
    rank_ax.tick_params(axis="y", labelsize=7)
    rank_ax.tick_params(axis="x", labelsize=7)
    rank_ax.set_xlabel("")
    rank_ax.set_ylabel("")
    rank_ax.set_title("")

    snapshot_panel = card_axes(fig, [0.05, 0.06, 0.90, 0.15])
    add_section_title(snapshot_panel, "Executive Snapshot", "High-performing videos in the current filtered result")
    snapshot_df = report_df.nlargest(5, "views")[["title", "views", "likes", "comments"]].copy()
    snapshot_df.insert(0, "#", range(1, len(snapshot_df) + 1))
    snapshot_df["title"] = snapshot_df["title"].apply(lambda value: sanitize_pdf_text(value[:52] + ("..." if len(value) > 52 else "")))
    snapshot_df["views"] = snapshot_df["views"].map(lambda value: f"{int(value):,}")
    snapshot_df["likes"] = snapshot_df["likes"].map(lambda value: f"{int(value):,}")
    snapshot_df["comments"] = snapshot_df["comments"].map(lambda value: f"{int(value):,}")
    snapshot_table_ax = fig.add_axes([0.07, 0.075, 0.86, 0.10])
    snapshot_table_ax.axis("off")
    snapshot_table = snapshot_table_ax.table(
        cellText=snapshot_df.values,
        colLabels=["#", "Title", "Views", "Likes", "Comments"],
        cellLoc="left",
        colLoc="left",
        loc="center",
        bbox=[0, 0, 1, 1],
        colWidths=[0.05, 0.52, 0.14, 0.14, 0.15],
    )
    snapshot_table.auto_set_font_size(False)
    snapshot_table.set_fontsize(7.2)
    for (row, col), cell in snapshot_table.get_celld().items():
        cell.set_linewidth(0.6)
        cell.set_edgecolor("#3d2a6e")
        if row == 0:
            cell.set_facecolor(accent)
            cell.get_text().set_color(text_primary)
            cell.get_text().set_fontweight("bold")
        else:
            cell.set_facecolor(card_bg if row % 2 else card_bg_alt)
            cell.get_text().set_color(text_primary)

    add_page_number(fig, 1)
    append_pdf_page(fig)

    fig2 = new_page()

    page2_header = card_axes(fig2, [0.05, 0.86, 0.90, 0.08], facecolor=card_bg)
    page2_header.text(0.03, 0.55, "Detailed Video Performance", color=text_primary, fontsize=18, fontweight="bold", transform=page2_header.transAxes)
    page2_header.text(0.03, 0.20, "Full ranking table for the current filtered dataset", color=text_muted, fontsize=8.5, transform=page2_header.transAxes)
    page2_header.text(0.97, 0.38, sanitize_pdf_text(channel_details["title"]), color=accent_cyan, fontsize=10, fontweight="bold", ha="right", transform=page2_header.transAxes)

    page2_stats = card_axes(fig2, [0.05, 0.76, 0.90, 0.07], facecolor=card_bg_alt)
    page2_stats.text(0.03, 0.50, f"Best upload day: {sanitize_pdf_text(best_day)}", color=text_primary, fontsize=9, va="center", transform=page2_stats.transAxes)
    page2_stats.text(0.36, 0.50, f"Top video views: {int(top_video['views']):,}", color=text_primary, fontsize=9, va="center", transform=page2_stats.transAxes)
    page2_stats.text(0.69, 0.50, f"Average engagement: {report_df['engagement'].mean() * 100:.2f}%", color=text_primary, fontsize=9, va="center", transform=page2_stats.transAxes)

    page_two = report_df.nlargest(20, "views")[["title", "Published Date", "views", "likes", "comments", "engagement"]].copy()
    page_two.insert(0, "#", range(1, len(page_two) + 1))
    page_two["title"] = page_two["title"].apply(lambda value: "\n".join(textwrap.wrap(sanitize_pdf_text(value), 36))[:120])
    page_two["Published Date"] = page_two["Published Date"].dt.strftime("%Y-%m-%d")
    page_two["views"] = page_two["views"].map(lambda value: f"{int(value):,}")
    page_two["likes"] = page_two["likes"].map(lambda value: f"{int(value):,}")
    page_two["comments"] = page_two["comments"].map(lambda value: f"{int(value):,}")
    page_two["engagement"] = page_two["engagement"].map(lambda value: f"{value * 100:.2f}%")

    table_wrap = card_axes(fig2, [0.05, 0.08, 0.90, 0.64], facecolor=card_bg)
    add_section_title(table_wrap, "Ranking Table", "Top 20 videos ordered by views")
    table2_ax = fig2.add_axes([0.07, 0.11, 0.86, 0.56])
    table2_ax.axis("off")
    table2 = table2_ax.table(
        cellText=page_two.values,
        colLabels=["#", "Title", "Published", "Views", "Likes", "Comments", "Engagement"],
        cellLoc="left",
        colLoc="left",
        loc="center",
        bbox=[0, 0, 1, 1],
        colWidths=[0.04, 0.38, 0.12, 0.12, 0.11, 0.11, 0.12],
    )
    table2.auto_set_font_size(False)
    table2.set_fontsize(7.0)
    for (row, col), cell in table2.get_celld().items():
        cell.set_linewidth(0.45)
        cell.set_edgecolor("#3d2a6e")
        if row == 0:
            cell.set_facecolor(accent)
            cell.get_text().set_color(text_primary)
            cell.get_text().set_fontweight("bold")
        else:
            cell.set_facecolor(card_bg if row % 2 else card_bg_alt)
            cell.get_text().set_color(text_primary)
            if col == 6:
                cell.get_text().set_color("#f43f5e")

    add_page_number(fig2, 2)
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

            gradient_divider()

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
                    
                    fig_trend = px.line(filtered_df_sorted, x="Published Date", y="views", template=CHART_THEME, color_discrete_sequence=['#a78bfa'], markers=True)
                    apply_transparent_bg(fig_trend)
                    fig_trend.update_traces(line_shape='spline', fill='tozeroy', fillcolor='rgba(124, 58, 237, 0.12)', line=dict(width=3.5))
                    fig_trend.update_yaxes(title_text="Total Views")
                    st.plotly_chart(fig_trend, use_container_width=True)

                    st.markdown("**Engagement Density**")
                    # Use Inferno so 0-values map to dark background, blending perfectly
                    fig_heat = px.density_heatmap(
                        filtered_df, x="views", y="engagement", 
                        nbinsx=15, nbinsy=15, 
                        template=CHART_THEME, color_continuous_scale="Purples"
                    )
                    apply_transparent_bg(fig_heat)
                    fig_heat.update_layout(xaxis_title="Views", yaxis_title="Engagement Rate")
                    st.plotly_chart(fig_heat, use_container_width=True)

                with v_col2:
                    st.markdown("**Top 10 Performing Videos**")
                    top10 = filtered_df.sort_values("views", ascending=False).head(10).copy()
                    # Shorten titles to prevent chart squashing
                    top10['Short Title'] = top10['title'].apply(lambda x: x[:35] + '...' if len(x) > 35 else x)
                    
                    fig_bar = px.bar(top10, x="views", y="Short Title", orientation='h', text_auto='.2s', template=CHART_THEME, color_discrete_sequence=['#7c3aed'])
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
                        template=CHART_THEME, color_continuous_scale="Plasma"
                    )
                    apply_transparent_bg(fig_scatter)
                    fig_scatter.update_layout(xaxis_title="Views", yaxis_title="Engagement Rate")
                    fig_scatter.update_traces(marker=dict(line=dict(width=1.2, color='rgba(124,58,237,0.5)')))
                    st.plotly_chart(fig_scatter, use_container_width=True)

                gradient_divider()
                
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
                
                gradient_divider()

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
                
                gradient_divider()

                # Download Feature
                st.subheader("💡 Export Intelligence")
                export_df = filtered_df[['title', 'Published Date', 'views', 'likes', 'comments', 'engagement']].copy()
                export_df.rename(columns={
                    'title': 'Video Title',
                    'views': 'Views',
                    'likes': 'Likes',
                    'comments': 'Comments',
                    'engagement': 'Engagement Rate (%)'
                }, inplace=True)
                export_df['Engagement Rate (%)'] = (export_df['Engagement Rate (%)'] * 100).round(4)
                csv = export_df.to_csv(index=False).encode('utf-8')
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
        
        gradient_divider()
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
                color_discrete_sequence=['#7c3aed', '#f43f5e']
            )
            apply_transparent_bg(fig_compare_views)
            st.plotly_chart(fig_compare_views, use_container_width=True)
