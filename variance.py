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
search_term = st.sidebar.text_input("Search by Item Name or Barcode").strip()
if search_term:
    df = df[
        df['Items'].astype(str).str.contains(search_term, case=False, na=False)
        | df['Item Code'].astype(str).str.contains(search_term, case=False, na=False)
    ]

# =========================
# Key Insights (Dynamic)
# =========================
total_purchase_value = df['Total Purchase'].sum()
total_sales_value = df['Total Sales'].sum()
total_qty_purchased = df['Qty Purchased'].sum()
total_qty_sold = df['QTY Sold'].sum()
total_stock = df['STOCK'].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Purchase Value", f"{total_purchase_value:,.2f}")
col2.metric("💵 Total Sales Value", f"{total_sales_value:,.2f}")
col3.metric("📦 Total Purchased Qty", f"{total_qty_purchased:,}")
col4.metric("🛒 Total Sold Qty", f"{total_qty_sold:,}")
col5.metric("🏷️ Total Stock", f"{total_stock:,}")

# =========================
# Chart Section
# =========================
st.subheader("📊 Quantity Overview")

if search_term:
    # When searched, show total Purchased vs Sold for filtered items
    summary = pd.DataFrame({
        "Category": ["Qty Purchased", "QTY Sold"],
        "Quantity": [total_qty_purchased, total_qty_sold]
    })

    fig = px.bar(
        summary,
        x="Quantity",
        y="Category",
        orientation="h",
        text="Quantity",
        title=f"Total Purchased vs Sold for '{search_term}'",
        color="Category",
    )
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig.update_layout(showlegend=False, height=400)
else:
    # Default view — Top 30 items
    chart_df = (
        df.groupby("Items")[["Qty Purchased", "QTY Sold"]]
        .sum()
        .reset_index()
        .sort_values(by="QTY Sold", ascending=False)
        .head(30)
    )

    fig = px.bar(
        chart_df,
        y="Items",
        x=["Qty Purchased", "QTY Sold"],
        orientation="h",
        barmode="group",
        title="Top 30 Items - Purchase vs Sold Quantity",
        labels={"value": "Quantity", "Items": "Item"},
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=900)

st.plotly_chart(fig, use_container_width=True)

# =========================
# Display Table
# =========================
st.subheader("📋 Detailed Data View")
st.dataframe(df.reset_index(drop=True), use_container_width=True)
