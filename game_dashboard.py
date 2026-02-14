import pandas as pd
import streamlit as st
import plotly.express as px

# ---------- PAGE ----------
st.set_page_config(
    page_title="🎮 Game Sales Analytics",
    layout="wide"
)

# ---------- STYLE ----------
st.markdown("""
<style>
body {
    background: linear-gradient(120deg,#0f172a,#1e293b);
    color:white;
}

.big-title {
    font-size:42px;
    font-weight:800;
    background: linear-gradient(90deg,#00c6ff,#fdbb2d);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.card {
    background: rgba(255,255,255,0.08);
    padding:18px;
    border-radius:14px;
    text-align:center;
    box-shadow:0 4px 15px rgba(0,0,0,0.4);
}

.metric {
    font-size:28px;
    font-weight:bold;
    color:#00ffd5;
}
</style>
""", unsafe_allow_html=True)

# ---------- PATH ----------
PATH = "best_selling_video_games.csv"

# ---------- LOAD ----------
@st.cache_data
def load():
    df = pd.read_csv(PATH)

    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("(", "")
        .str.replace(")", "")
        .str.lower()
    )
    return df

df = load()

# ---------- COLUMN DETECTION ----------
def find_col(word):
    for c in df.columns:
        if word in c:
            return c
    return None

sales_col = find_col("sales")
year_col = find_col("year")
platform_col = find_col("platform")
publisher_col = find_col("publisher")
game_col = find_col("game") or find_col("title") or df.columns[0]

# ---------- CLEAN ----------
df[sales_col] = pd.to_numeric(df[sales_col], errors="coerce")
if year_col:
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")

df = df.dropna()

# ---------- TITLE ----------
st.markdown('<p class="big-title">🎮 Video Game Sales Intelligence</p>', unsafe_allow_html=True)
st.caption("A visual exploration of best-selling games")

# ---------- SIDEBAR ----------
st.sidebar.header("🎛 Filters")

if platform_col:
    pf = st.sidebar.multiselect(
        "Platform",
        df[platform_col].unique(),
        df[platform_col].unique()
    )
    df = df[df[platform_col].isin(pf)]

if publisher_col:
    pubf = st.sidebar.multiselect(
        "Publisher",
        df[publisher_col].unique(),
        df[publisher_col].unique()
    )
    df = df[df[publisher_col].isin(pubf)]

# ---------- KPI CARDS ----------
c1,c2,c3,c4 = st.columns(4)

def card(col,title,val):
    col.markdown(f"""
    <div class="card">
        <h4>{title}</h4>
        <p class="metric">{val}</p>
    </div>
    """, unsafe_allow_html=True)

card(c1,"Total Games",len(df))
card(c2,"Total Sales (M)",round(df[sales_col].sum(),1))
card(c3,"Average Sales (M)",round(df[sales_col].mean(),1))

top_game = df.loc[df[sales_col].idxmax()]
card(c4,"Top Game",top_game[game_col])

st.divider()

# ---------- CHARTS ----------
col1,col2 = st.columns(2)

# Top games
top10 = df.nlargest(10, sales_col)

fig1 = px.bar(
    top10,
    x=game_col,
    y=sales_col,
    color=sales_col,
    color_continuous_scale="Turbo",
    title="🏆 Top 10 Games by Sales"
)
fig1.update_layout(template="plotly_dark")
col1.plotly_chart(fig1, use_container_width=True)

# Sales trend
if year_col:
    yearly = df.groupby(year_col)[sales_col].sum().reset_index()

    fig2 = px.line(
        yearly,
        x=year_col,
        y=sales_col,
        markers=True,
        title="📈 Sales Trend Over Time"
    )
    fig2.update_layout(template="plotly_dark")
    col2.plotly_chart(fig2, use_container_width=True)

# Platform share
if platform_col:
    plat = df.groupby(platform_col)[sales_col].sum().reset_index()

    fig3 = px.pie(
        plat,
        names=platform_col,
        values=sales_col,
        hole=0.55,
        title="🎮 Platform Market Share"
    )
    fig3.update_layout(template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

# Publisher ranking
if publisher_col:
    pub = (
        df.groupby(publisher_col)[sales_col]
        .sum()
        .nlargest(10)
        .reset_index()
    )

    fig4 = px.bar(
        pub,
        x=publisher_col,
        y=sales_col,
        color=sales_col,
        color_continuous_scale="Plasma",
        title="🏢 Top Publishers"
    )
    fig4.update_layout(template="plotly_dark")
    st.plotly_chart(fig4, use_container_width=True)

# ---------- TABLE ----------
st.subheader("📄 Data Preview")
st.dataframe(df, use_container_width=True)

st.download_button(
    "⬇ Download Filtered Data",
    df.to_csv(index=False),
    "filtered_games.csv"
)
