import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Page Configuration
# =========================
st.set_page_config(page_title="📊 Purchase vs Sales Dashboard", layout="wide")

st.title("📦 Purchase vs Sales Dashboard")

# =========================
# Load Excel Data (no uploader)
# =========================
file_path = "faisalka.xlsx"   # 🔹 Change this to your actual Excel file name
df = pd.read_excel(file_path)

# =========================
# Data Cleaning
# =========================
df.columns = df.columns.str.strip()
df['Sold-Stock'] = df['QTY Sold'] - df['STOCK']

# =========================
# Sidebar Filters
# =========================
st.sidebar.header("🔍 Filters")

outlet_list = ["All"] + sorted(df['Outlet'].dropna().unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlet_list)

if selected_outlet != "All":
    df = df[df['Outlet'] == selected_outlet]

# =========================
# Search Option
# =========================
search_term = st.sidebar.text_input("Search by Item Name or Barcode")
if search_term:
    df = df[
        df['Items'].astype(str).str.contains(search_term, case=False, na=False)
        | df['Item Code'].astype(str).str.contains(search_term, case=False, na=False)
    ]

# =========================
# Key Insights
# =========================
total_purchase_value = df['Total Purchase'].sum()
total_sales_value = df['Total Sales'].sum()
total_qty_purchased = df['Qty Purchased'].sum()
total_qty_sold = df['QTY Sold'].sum()
total_stock = df['STOCK'].sum()
avg_sold_stock_diff = df['Sold-Stock'].mean()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Purchase Value", f"{total_purchase_value:,.2f}")
col2.metric("💵 Total Sales Value", f"{total_sales_value:,.2f}")
col3.metric("📦 Total Purchased Qty", f"{total_qty_purchased:,}")
col4.metric("🛒 Total Sold Qty", f"{total_qty_sold:,}")
col5.metric("🏷️ Total Stock", f"{total_stock:,}")

# =========================
# Bar Chart: Purchase vs Sold
# =========================
st.subheader("📉 Purchase vs Sold Quantity Comparison")

chart_df = df.groupby("Items")[["Qty Purchased", "QTY Sold"]].sum().reset_index()
fig = px.bar(
    chart_df,
    x="Items",
    y=["Qty Purchased", "QTY Sold"],
    barmode="group",
    title="Purchase vs Sold Quantity",
    labels={"value": "Quantity", "Items": "Item"},
)
st.plotly_chart(fig, use_container_width=True)

# =========================
# Display Table
# =========================
st.subheader("📋 Detailed Data View")
st.dataframe(df.reset_index(drop=True), use_container_width=True)
