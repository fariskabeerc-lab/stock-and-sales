import streamlit as st
import pandas as pd
import plotly.express as px

# ============================
# Page Config
# ============================
st.set_page_config(page_title="Highest Unsold Items Dashboard", layout="wide")
st.title("📦 EMERGING WORLD")

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

# Derived columns
df["Profit"] = df["Total Sales"] - df["Total Purchase"]
df["Sold-Stock"] = df["QTY Sold"] - df["STOCK"]

# ============================
# Sidebar Filters
# ============================
st.sidebar.header("🔍 Filters")

# Outlet filter
outlets = ["All"] + sorted(df["Outlet"].dropna().unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlets)

filtered_df = df.copy()
if selected_outlet != "All":
    filtered_df = filtered_df[filtered_df["Outlet"] == selected_outlet]

# Search box
search_query = st.sidebar.text_input("Search by Item Code or Item Name").strip().lower()
if search_query:
    filtered_df = filtered_df[
        filtered_df["Items"].str.lower().str.contains(search_query)
        | filtered_df["Item Code"].astype(str).str.contains(search_query)
    ]

# ============================
# Key Insights Section
# ============================
if not filtered_df.empty:
    total_purchased_qty = filtered_df["Qty Purchased"].sum()
    total_sold_qty = filtered_df["QTY Sold"].sum()
    total_stock = filtered_df["STOCK"].sum()
    total_purchase_value = filtered_df["Total Purchase"].sum()
    total_sales_value = filtered_df["Total Sales"].sum()
    total_profit = filtered_df["Profit"].sum()
    sold_stock_diff = filtered_df["Sold-Stock"].sum()

    st.markdown("### 📊 Key Insights")

    col1, col2, col3 = st.columns(3)
    col1.metric("🛒 Total Purchased Qty", f"{int(total_purchased_qty):,}")
    col2.metric("📦 Total Sold Qty", f"{int(total_sold_qty):,}")
    col3.metric("📉 Total Stock (Unsold)", f"{int(total_stock):,}")

    col4, col5, col6 = st.columns(3)
    col4.metric("💰 Total Purchase Value", f"{total_purchase_value:,.2f}")
    col5.metric("💵 Total Sales Value", f"{total_sales_value:,.2f}")
    col6.metric("📈 Total Profit", f"{total_profit:,.2f}")

    st.metric("📊 Sold - Stock Difference", f"{int(sold_stock_diff):,}")

else:
    st.warning("No data available for selected filters or search.")

# ============================
# Highest Unsold Items Graph
# ============================
if not filtered_df.empty:
    st.markdown("### 🏷️ Top 50 Highest Unsold Items")

    top_unsold = (
        filtered_df.groupby(["Item Code", "Items"], as_index=False)["STOCK"]
        .sum()
        .sort_values(by="STOCK", ascending=False)
        .head(50)
    )

    fig_unsold = px.bar(
        top_unsold,
        x="STOCK",
        y="Items",
        orientation="h",
        title="Top 50 Highest Unsold Items",
        text="STOCK",
        color="STOCK",
        color_continuous_scale="Blues"
    )

    fig_unsold.update_traces(
        texttemplate='%{text:.0f}',
        textposition="outside",
        textfont_size=16,  # Bigger labels
        marker_line_width=1.5,
        marker_line_color="white"
    )
    fig_unsold.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Unsold Quantity",
        yaxis_title="Item",
        height=1000,
        title_x=0.5,
        bargap=0.35,  # Gap between bars
        font=dict(size=16),
        plot_bgcolor="white"
    )

    st.plotly_chart(fig_unsold, use_container_width=True)

# ============================
# Purchase vs Sales Graph
# ============================
if not filtered_df.empty:
    st.markdown("### 📊 Item-wise Purchase vs Sales Comparison")

    # Aggregate by Item
    item_summary = (
        filtered_df.groupby(["Item Code", "Items"], as_index=False)[["Total Purchase", "Total Sales"]]
        .sum()
        .sort_values(by="Total Sales", ascending=False)
        .head(50)
    )

    # Melt for comparison bar chart
    melted_df = item_summary.melt(
        id_vars=["Item Code", "Items"], value_vars=["Total Purchase", "Total Sales"],
        var_name="Type", value_name="Amount"
    )

    fig_compare = px.bar(
        melted_df,
        x="Amount",
        y="Items",
        color="Type",
        orientation="h",
        title="Top 50 Items - Purchase vs Sales",
        barmode="group",
        text_auto=".2s",
        color_discrete_map={"Total Purchase": "#FF7F0E", "Total Sales": "#1F77B4"}
    )

    fig_compare.update_traces(
        textfont_size=16,
        marker_line_width=1.2,
        marker_line_color="white"
    )
    fig_compare.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Amount",
        yaxis_title="Item",
        height=900,
        title_x=0.5,
        bargap=0.35,  # Increased gap
        font=dict(size=16),
        plot_bgcolor="white"
    )

    st.plotly_chart(fig_compare, use_container_width=True)

# ============================
# Data Table (All Columns)
# ============================
st.markdown("### 📄 Detailed Data Table")
st.dataframe(filtered_df, use_container_width=True)

# ============================
# Footer
# ============================
st.caption("📈 Dashboard dynamically updates with Outlet filter and Search. All charts and tables are linked.")
