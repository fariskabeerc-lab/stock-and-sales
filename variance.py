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
file_path = "faisalka.xlsx"  # Update your path
df = pd.read_excel(file_path)

# ============================
# Preprocess
# ============================
df['Unsold'] = df['Qty Purchased'] - df['QTY Sold']
df['Sold - Stock'] = df['QTY Sold'] - df['STOCK']

# ============================
# Sidebar Filters
# ============================
st.sidebar.header("🔍 Filters")
outlet_list = ["All"] + sorted(df['Outlet'].dropna().unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlet_list)
search_term = st.sidebar.text_input("Search Item (name or code):", "").strip().lower()

# ============================
# Filter Data
# ============================
if selected_outlet == "All":
    filtered_df = df.copy()
else:
    filtered_df = df[df['Outlet'] == selected_outlet]

if search_term:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: search_term in str(row['Items']).lower()
            or search_term in str(row['Item Code']).lower(),
            axis=1
        )
    ]

# ============================
# Key Insights (2 rows)
# ============================
st.markdown("### 📊 Key Insights")

# First row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Purchase Qty", f"{filtered_df['Qty Purchased'].sum():,.0f}")
col2.metric("Total Purchase Value", f"{filtered_df['Total Purchase'].sum():,.2f}")
col3.metric("Total Sold Qty", f"{filtered_df['QTY Sold'].sum():,.0f}")
col4.metric("Total Sales Value", f"{filtered_df['Total Sales'].sum():,.2f}")

# Second row
col5, col6, col7, col8 = st.columns(4)
col5.metric("Total Stock Qty", f"{filtered_df['STOCK'].sum():,.0f}")
col6.metric("Unsold Qty", f"{filtered_df['Unsold'].sum():,.0f}")
col7.metric("Sold - Stock", f"{filtered_df['Sold - Stock'].sum():,.0f}")
col8.metric("Total Items", f"{len(filtered_df):,.0f}")

# ============================
# Graph 1: Purchase vs Sold
# ============================
st.subheader("📊 Purchase vs Sold Comparison")

agg_compare = filtered_df.groupby("Items")[["Qty Purchased", "QTY Sold"]].sum().reset_index()
top_items = agg_compare.nlargest(30, "Qty Purchased")  # top 30 items

fig_compare = px.bar(
    top_items.melt(id_vars=["Items"], value_vars=["Qty Purchased", "QTY Sold"]),
    y="Items",
    x="value",
    color="variable",
    orientation="h",
    barmode="group",
    text="value",
)
fig_compare.update_traces(
    textposition="outside",
    textfont_size=14,
    texttemplate="%{text:,}"
)
fig_compare.update_layout(
    yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
    xaxis=dict(title="Quantity", tickfont=dict(size=12)),
    bargap=0.5,  # standard gap
    height=750,  # standard height
    margin=dict(l=180, r=50, t=50, b=50),
    legend=dict(font=dict(size=12)),
)
st.plotly_chart(fig_compare, use_container_width=True)

# ============================
# Graph 2: Unsold Items
# ============================
st.subheader("📉 Highest Unsold Items")

unsold_agg = filtered_df.groupby("Items")[["Qty Purchased", "QTY Sold", "Unsold"]].sum().reset_index()
top_unsold = unsold_agg.sort_values("Unsold", ascending=False).head(30)

fig_unsold = px.bar(
    top_unsold,
    x="Unsold",
    y="Items",
    orientation="h",
    text="Unsold",
    hover_data=["Qty Purchased", "QTY Sold", "Unsold"],
    color="Unsold",
    color_continuous_scale="Reds",
)
fig_unsold.update_traces(
    textposition="outside",
    textfont_size=14,
    texttemplate="%{text:,}"
)
fig_unsold.update_layout(
    yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
    xaxis=dict(title="Unsold Qty", tickfont=dict(size=12)),
    bargap=0.5,
    height=750,  # standard height
    margin=dict(l=180, r=50, t=50, b=50),
    coloraxis_colorbar=dict(title="Unsold Qty", tickfont=dict(size=12)),
)
st.plotly_chart(fig_unsold, use_container_width=True)

# ============================
# Table Section
# ============================
st.subheader("📋 Detailed Data View")
st.dataframe(filtered_df, use_container_width=True)
