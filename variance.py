import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# 🎨 Page Configuration
# =========================
st.set_page_config(page_title="📊 Purchase vs Sales Dashboard", layout="wide")
st.markdown("<h1 style='text-align:center;'>📦 Purchase vs Sales Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# =========================
# 📂 Load Excel Data (No Uploader)
# =========================
file_path = "faisalka.xlsx"   # 🔹 Change this to your Excel file name
df = pd.read_excel(file_path)

# =========================
# 🧹 Data Preparation
# =========================
df.columns = df.columns.str.strip()
df['Sold-Stock'] = df['QTY Sold'] - df['STOCK']
df['Unsold'] = df['STOCK']  # For clarity

# Safety check
required_cols = ['Item Code', 'Items', 'Qty Purchased', 'Total Purchase', 
                 'STOCK', 'QTY Sold', 'Total Sales', 'Outlet']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"❌ Missing columns in file: {missing_cols}")
    st.stop()

# =========================
# 🧭 Sidebar Filters
# =========================
st.sidebar.header("🔍 Filter Options")

outlet_list = ["All"] + sorted(df['Outlet'].dropna().unique().tolist())
selected_outlet = st.sidebar.selectbox("🏬 Select Outlet", outlet_list)

if selected_outlet != "All":
    df = df[df['Outlet'] == selected_outlet]

search_term = st.sidebar.text_input("🔎 Search by Item Name or Barcode").strip()

if search_term:
    df = df[
        df['Items'].astype(str).str.contains(search_term, case=False, na=False)
        | df['Item Code'].astype(str).str.contains(search_term, case=False, na=False)
    ]

# =========================
# 💡 Key Insights
# =========================
total_purchase_value = df['Total Purchase'].sum()
total_sales_value = df['Total Sales'].sum()
total_qty_purchased = df['Qty Purchased'].sum()
total_qty_sold = df['QTY Sold'].sum()
total_stock = df['STOCK'].sum()
sold_purchase_diff = total_qty_sold - total_qty_purchased

st.markdown("### 📈 Key Insights")
st.markdown("")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("💰 Total Purchase Value", f"{total_purchase_value:,.2f}")
col2.metric("💵 Total Sales Value", f"{total_sales_value:,.2f}")
col3.metric("📦 Qty Purchased", f"{total_qty_purchased:,}")
col4.metric("🛒 Qty Sold", f"{total_qty_sold:,}")
col5.metric("🏷️ Stock", f"{total_stock:,}")
col6.metric("⚖️ Sold - Purchase", f"{sold_purchase_diff:,}", delta=f"{sold_purchase_diff:,}")
st.markdown("---")

# =========================
# 📊 Visualization 1: Purchase vs Sold (Top 30)
# =========================
if search_term:
    summary = pd.DataFrame({
        "Category": ["Qty Purchased", "QTY Sold"],
        "Quantity": [total_qty_purchased, total_qty_sold]
    })

    fig1 = px.bar(
        summary,
        x="Quantity",
        y="Category",
        orientation="h",
        text="Quantity",
        color="Category",
        color_discrete_map={"Qty Purchased": "#636EFA", "QTY Sold": "#00CC96"},
        title=f"📊 Purchased vs Sold Summary — '{search_term}'",
    )
    fig1.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig1.update_layout(showlegend=False, height=400)
else:
    chart_df = (
        df.groupby("Items")[["Qty Purchased", "QTY Sold"]]
        .sum()
        .reset_index()
        .sort_values(by="QTY Sold", ascending=False)
        .head(30)
    )

    fig1 = px.bar(
        chart_df,
        y="Items",
        x=["Qty Purchased", "QTY Sold"],
        orientation="h",
        barmode="group",
        color_discrete_map={"Qty Purchased": "#636EFA", "QTY Sold": "#00CC96"},
        title="🏆 Top 30 Items — Purchase vs Sold Quantity",
        labels={"value": "Quantity", "Items": "Item"},
    )
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, height=900)

st.plotly_chart(fig1, use_container_width=True)
st.markdown("---")

# =========================
# 📊 Visualization 2: Top 50 Highest Unsold Items
# =========================
unsold_df = (
    df.groupby("Items")[["Unsold", "Qty Purchased", "QTY Sold"]]
    .sum()
    .reset_index()
    .sort_values(by="Unsold", ascending=False)
    .head(50)
)

fig2 = px.bar(
    unsold_df,
    y="Items",
    x="Unsold",
    orientation="h",
    text="Unsold",
    color="Unsold",
    color_continuous_scale="Reds",
    title="📦 Top 50 Highest Unsold Items (By Stock Quantity)",
    labels={"Unsold": "Unsold Quantity", "Items": "Item"},
)
fig2.update_traces(texttemplate='%{text:,}', textposition='outside')
fig2.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    height=1000,
    coloraxis_showscale=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)

st.plotly_chart(fig2, use_container_width=True)
st.markdown("---")

# =========================
# 📋 Detailed Data View
# =========================
st.markdown("### 📄 Detailed Data View")
st.dataframe(df.reset_index(drop=True), use_container_width=True)
