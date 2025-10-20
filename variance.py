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
file_path = "faisalka.xlsx"  # Change your file path
df = pd.read_excel(file_path)

# ============================
# Data Cleaning
# ============================
df.columns = df.columns.str.strip()

# Ensure numeric columns
for col in ["Qty Purchased", "Total Purchase", "STOCK", "QTY Sold", "Total Sales"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Add derived columns
df["Unsold Qty"] = df["STOCK"]
df["Profit"] = df["Total Sales"] - df["Total Purchase"]

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
    df = df[
        df["Items"].str.lower().str.contains(search_query)
        | df["Item Code"].astype(str).str.contains(search_query)
    ]

# ============================
# Key Insights Section
# ============================
total_purchased_qty = df["Qty Purchased"].sum()
total_sold_qty = df["QTY Sold"].sum()
total_stock = df["STOCK"].sum()
total_purchase_value = df["Total Purchase"].sum()
total_sales_value = df["Total Sales"].sum()
total_profit = df["Profit"].sum()
unsold_difference = total_stock - total_sold_qty

st.markdown("### 📊 Key Insights")

col1, col2, col3 = st.columns(3)
col1.metric("🛒 Total Purchased Qty", f"{int(total_purchased_qty):,}")
col2.metric("📦 Total Sold Qty", f"{int(total_sold_qty):,}")
col3.metric("📉 Total Stock (Unsold)", f"{int(total_stock):,}")

col4, col5, col6 = st.columns(3)
col4.metric("💰 Total Purchase Value", f"{total_purchase_value:,.2f}")
col5.metric("💵 Total Sales Value", f"{total_sales_value:,.2f}")
col6.metric("📈 Total Profit", f"{total_profit:,.2f}")

st.metric("📊 Unsold Difference (Stock - Sold)", f"{int(unsold_difference):,}")

# ============================
# Highest Unsold Items Graph
# ============================
st.markdown("### 🏷️ Top 50 Highest Unsold Items")

top_unsold = (
    df.groupby(["Item Code", "Items"], as_index=False)["STOCK"].sum()
    .sort_values(by="STOCK", ascending=False)
    .head(50)
)

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
# Footer
# ============================
st.caption("📈 Dashboard dynamically updates with search and outlet filters.")
