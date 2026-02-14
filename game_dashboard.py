import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="🎮 Game Dashboard", layout="wide")

PATH = "best_selling_video_games.csv"

@st.cache_data
def load():
    df = pd.read_csv(PATH)

    # clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "")
        .str.replace(")", "")
    )
    return df

df = load()

# ---------- AUTO DETECT COLUMNS ----------
def find(name):
    for c in df.columns:
        if name in c:
            return c
    return None

sales_col = find("sales")
year_col = find("year")
game_col = find("game") or find("title")
platform_col = find("platform")
publisher_col = find("publisher")

# ---------- CLEAN ----------
df[sales_col] = pd.to_numeric(df[sales_col], errors="coerce")
df[year_col] = pd.to_numeric(df[year_col], errors="coerce")

df = df.dropna()

# ---------- TITLE ----------
st.title("🎮 Video Game Sales Dashboard")

# ---------- KPIs ----------
c1,c2,c3 = st.columns(3)

c1.metric("Total Games", len(df))
c2.metric("Total Sales", round(df[sales_col].sum(),1))
c3.metric("Average Sales", round(df[sales_col].mean(),1))

# ---------- CHARTS ----------
top10 = df.nlargest(10, sales_col)

fig = px.bar(top10, x=game_col, y=sales_col, color=sales_col)
st.plotly_chart(fig, use_container_width=True)

yearly = df.groupby(year_col)[sales_col].sum().reset_index()

fig2 = px.line(yearly, x=year_col, y=sales_col, markers=True)
st.plotly_chart(fig2, use_container_width=True)

if platform_col:
    fig3 = px.pie(df, names=platform_col, values=sales_col)
    st.plotly_chart(fig3, use_container_width=True)

if publisher_col:
    pub = df.groupby(publisher_col)[sales_col].sum().reset_index()
    fig4 = px.bar(pub, x=publisher_col, y=sales_col)
    st.plotly_chart(fig4, use_container_width=True)

st.dataframe(df)
