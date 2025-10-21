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
file_path = "faisalka.xlsx"  # Change path if needed
df = pd.read_excel(file_path)

# ============================
# Validate Columns
# ============================
required_cols = ["Item Code", "Items", "Qty Purchased", "Total Purchase", "STOCK", "QTY Sold", "Total Sales", "Outlet"]
missing_cols = [c for c in required_cols if c not in df.columns]
if missing_cols:
    st.error(f"Missing columns in Excel: {', '.join(missing_cols)}")
    st.stop()

# ============================
# Derived Columns
# ============================
df["Sold - Stock"] = df["QTY Sold"] - df["STOCK"]
df["Unsold Qty"] = df["Qty Purchased"] - df["QTY Sold"]

# ============================
# Sidebar Filters
# ============================
st.sidebar.header("🔍 Filters")

outlet_list = ["All"] + sorted(df["Outlet"].dropna().unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlet_list)

search_query = st.sidebar.text_input("Search (Item, Code, Outlet, or Any Field)").strip().lower()

# ============================
# Filter Logic
# ============================
filtered_df = df.copy()

if selected_outlet != "All":
    filtered_df = filtered_df[filtered_df["Outlet"] == selected_outlet]

if search_query:
    mask = pd.Series(False, index=filtered_df.index)
    for col in filtered_df.columns:
        mask = mask | filtered_df[col].astype(str).str.lower().str.contains(search_query, na=False)
    filtered_df = filtered_df[mask]

# ============================
# Key Insights
# ============================
total_purchase = filtered_df["Total Purchase"].sum()
total_sales = filtered_df["Total Sales"].sum()
total_items = len(filtered_df)
total_qty_purchased = filtered_df["Qty Purchased"].sum()
total_qty_sold = filtered_df["QTY Sold"].sum()
total_stock = filtered_df["STOCK"].sum()
total_diff = filtered_df["Sold - Stock"].sum()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("🛒 Total Purchase", f"{total_purchase:,.0f}")
col2.metric("💰 Total Sales", f"{total_sales:,.0f}")
col3.metric("📦 Total Stock", f"{total_stock:,.0f}")
col4.metric("📊 Qty Purchased", f"{total_qty_purchased:,.0f}")
col5.metric("📈 Qty Sold", f"{total_qty_sold:,.0f}")
col6.metric("⚖️ Sold - Stock", f"{total_diff:,.0f}")

# ============================
# Graph 1: Highest Unsold Items
# ============================
st.subheader("📉 Highest Unsold Items (Qty Purchased - QTY Sold)")

top_limit = 15 if search_query else 50  # shrink graph when searching
top_unsold = filtered_df.copy()
top_unsold["Unsold Qty"] = top_unsold["Qty Purchased"] - top_unsold["QTY Sold"]
top_unsold = top_unsold.sort_values("Unsold Qty", ascending=False).head(top_limit)

fig_unsold = px.bar(
    top_unsold,
    x="Unsold Qty",
    y="Items",
    orientation="h",
    text="Unsold Qty",
    title=f"Top {top_limit} Highest Unsold Items",
    color="Unsold Qty",
    color_continuous_scale="Reds",
)
fig_unsold.update_layout(
    yaxis=dict(autorange="reversed"),
    height=500 if search_query else 900,
)
st.plotly_chart(fig_unsold, use_container_width=True)

# ============================
# Graph 2: Purchase vs Sold
# ============================
st.subheader("📊 Purchase vs Sold Comparison")

top_limit_2 = 10 if search_query else 30  # shrink if searching
top30 = filtered_df.nlargest(top_limit_2, "Qty Purchased")

fig_compare = px.bar(
    top30.melt(id_vars=["Items"], value_vars=["Qty Purchased", "QTY Sold"]),
    y="Items",
    x="value",
    color="variable",
    orientation="h",
    barmode="group",
    title=f"Top {top_limit_2} Items: Purchase vs Sold",
)
fig_compare.update_layout(
    yaxis=dict(autorange="reversed"),
    height=400 if search_query else 800,
)
st.plotly_chart(fig_compare, use_container_width=True)

# ============================
# Table View
# ============================
st.subheader("📋 Detailed Data View")
st.dataframe(filtered_df, use_container_width=True)
