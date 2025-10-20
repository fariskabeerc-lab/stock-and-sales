import streamlit as st
import pandas as pd
import plotly.express as px

# ============================
# Page Config
# ============================
st.set_page_config(page_title="Highest Unsold Items Dashboard", layout="wide")
st.title("📦 Highest Unsold Items Dashboard")

# ============================
# Load Data
# ============================
# Replace this with your Excel file name
file_path = "faisalka.xlsx"
df = pd.read_excel(file_path)

# ============================
# Data Cleaning
# ============================
df.columns = df.columns.str.strip()
df["Unsold Qty"] = df["STOCK"].fillna(0)

# ============================
# Sidebar Filters
# ============================
st.sidebar.header("🔍 Filters")

# Outlet filter
outlets = ["All"] + sorted(df["Outlet"].dropna().unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlets)

if selected_outlet != "All":
    df = df[df["Outlet"] == selected_outlet]

# Search box
search_query = st.sidebar.text_input("Search by Item Code or Item Name").strip().lower()
if search_query:
    df = df[df["Items"].str.lower().str.contains(search_query) | 
            df["Item Code"].astype(str).str.contains(search_query)]

# ============================
# Insights Section
# ============================
total_stock = df["STOCK"].sum()
total_sold = df["QTY Sold"].sum()
unsold = total_stock - total_sold

st.markdown("### 📊 Key Insights")
col1, col2, col3 = st.columns(3)
col1.metric("Total Stock", f"{int(total_stock):,}")
col2.metric("Total Sold", f"{int(total_sold):,}")
col3.metric("Unsold (Stock - Sold)", f"{int(unsold):,}")

# ============================
# Highest Unsold Items
# ============================
st.markdown("### 🏷️ Top 50 Highest Unsold Items")

top_unsold = df.groupby(["Item Code", "Items"], as_index=False)["STOCK"].sum()
top_unsold = top_unsold.sort_values(by="STOCK", ascending=False).head(50)

fig = px.bar(
    top_unsold,
    x="STOCK",
    y="Items",
    orientation="h",
    title="Top 50 Highest Unsold Items",
    text="STOCK",
)
fig.update_traces(texttemplate='%{text:.0f}', textposition="outside")
fig.update_layout(
    yaxis=dict(autorange="reversed"),
    xaxis_title="Unsold Quantity",
    yaxis_title="Item",
    height=1000,
    title_x=0.5,
    showlegend=False,
)

st.plotly_chart(fig, use_container_width=True)

# ============================
# Footer Info
# ============================
st.caption("📈 Dashboard updates dynamically with outlet and search filters.")
