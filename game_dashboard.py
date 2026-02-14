import pandas as pd
import streamlit as st
import plotly.express as px

# ---------- PAGE ----------
st.set_page_config(
    page_title="🎮 Game Sales Intelligence",
    layout="wide"
)

# ---------- STYLE ----------
st.markdown("""
<style>
body {
    background: linear-gradient(120deg,#0f172a,#1e293b,#020617);
    color:white;
}

.title {
    font-size:46px;
    font-weight:900;
    background: linear-gradient(90deg,#00f5ff,#ff00ff,#fdbb2d);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.card {
    background: rgba(255,255,255,0.08);
    padding:20px;
    border-radius:16px;
    text-align:center;
    box-shadow:0 4px 25px rgba(0,0,0,0.5);
}

.metric {
    font-size:30px;
    font-weight:bold;
    color:#00ffd5;
}
</style>
""", unsafe_allow_html=True)

# ---------- DATA ----------
PATH = "best_selling_video_games.csv"

@st.cache_data
def load():
    df = pd.read_csv(PATH)

    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ","_")
        .str.lower()
    )

    return df

df = load()

# ---------- CLEAN ----------
df["global_sales_millions"] = pd.to_numeric(
    df["global_sales_millions"], errors="coerce"
)

df["release_year"] = pd.to_numeric(
    df["release_year"], errors="coerce"
)

df = df.dropna()

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("🎛 Filters")

platform_f = st.sidebar.multiselect(
    "Platform",
    df["platform"].unique(),
    df["platform"].unique()
)

publisher_f = st.sidebar.multiselect(
    "Publisher",
    df["publisher"].unique(),
    df["publisher"].unique()
)

year_range = st.sidebar.slider(
    "Release Year",
    int(df["release_year"].min()),
    int(df["release_year"].max()),
    (int(df["release_year"].min()),
     int(df["release_year"].max()))
)

df = df[
    (df["platform"].isin(platform_f)) &
    (df["publisher"].isin(publisher_f)) &
    (df["release_year"].between(*year_range))
]

# ---------- TITLE ----------
st.markdown('<p class="title">🎮 Video Game Sales Intelligence</p>', unsafe_allow_html=True)
st.caption("Explore global best-selling games, platforms & publishers")

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
card(c2,"Total Sales (M)",round(df["global_sales_millions"].sum(),1))
card(c3,"Average Sales",round(df["global_sales_millions"].mean(),1))

top_game = df.loc[df["global_sales_millions"].idxmax()]
card(c4,"Top Game",top_game["game"])

st.divider()

# ---------- CHARTS ----------
col1,col2 = st.columns(2)

# Top 10 Games
top10 = df.nlargest(10,"global_sales_millions")

fig1 = px.bar(
    top10,
    x="game",
    y="global_sales_millions",
    color="global_sales_millions",
    color_continuous_scale="Turbo",
    title="🏆 Top 10 Best-Selling Games"
)
fig1.update_layout(template="plotly_dark")
col1.plotly_chart(fig1,use_container_width=True)

# Sales trend
yearly = df.groupby("release_year")["global_sales_millions"].sum().reset_index()

fig2 = px.area(
    yearly,
    x="release_year",
    y="global_sales_millions",
    color_discrete_sequence=["#00f5ff"],
    title="📈 Global Sales Trend"
)
fig2.update_layout(template="plotly_dark")
col2.plotly_chart(fig2,use_container_width=True)

# Platform dominance
plat = df.groupby("platform")["global_sales_millions"].sum().reset_index()

fig3 = px.pie(
    plat,
    names="platform",
    values="global_sales_millions",
    hole=0.55,
    title="🎮 Platform Market Share"
)
fig3.update_layout(template="plotly_dark")
st.plotly_chart(fig3,use_container_width=True)

# Publisher leaderboard
pub = (
    df.groupby("publisher")["global_sales_millions"]
    .sum()
    .nlargest(10)
    .reset_index()
)

fig4 = px.bar(
    pub,
    x="publisher",
    y="global_sales_millions",
    color="global_sales_millions",
    color_continuous_scale="Plasma",
    title="🏢 Top Publishers by Sales"
)
fig4.update_layout(template="plotly_dark")
st.plotly_chart(fig4,use_container_width=True)

# ---------- RANK TABLE ----------
st.subheader("🎯 Sales Ranking Table")
st.dataframe(
    df.sort_values("global_sales_millions",ascending=False),
    use_container_width=True
)

# ---------- DOWNLOAD ----------
st.download_button(
    "⬇ Download Filtered Data",
    df.to_csv(index=False),
    "filtered_games.csv"
)

