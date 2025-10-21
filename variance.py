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
# Sidebar Filters (list style)
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
# Key Insights
# ============================
st.markdown("### 📊 Key Insights")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Purchased", f"{filtered_df['Qty Purchased'].sum():,.0f}")
col2.metric("Total Sold", f"{filtered_df['QTY Sold'].sum():,.0f}")
col3.metric("Total Stock", f"{filtered_df['STOCK'].sum():,.0f}")
col4.metric("Sold - Stock", f"{filtered_df['Sold - Stock'].sum():,.0f}")
col5.metric("Total Unsold", f"{filtered_df['Unsold'].sum():,.0f}")
col6.metric("Total Items", f"{len(filtered_df):,.0f}")

# ============================
# Graph 1: Purchase vs Sold
# ============================
st.subheader("📊 Purchase vs Sold Comparison")
top_limit = 10 if search_term else 30

if search_term and selected_outlet == "All":
    top_items = filtered_df.groupby("Items")[["Qty Purchased", "QTY Sold"]].sum().reset_index()
else:
    top_items = filtered_df.nlargest(top_limit, "Qty Purchased")

fig_compare = px.bar(
    top_items.melt(id_vars=["Items"], value_vars=["Qty Purchased", "QTY Sold"]),
    y="Items",
    x="value",
    color="variable",
    orientation="h",
    barmode="group",
    text="value",
)
fig_compare.update_layout(
    yaxis=dict(autorange="reversed", tickmode='linear', tickson='boundaries'),
    bargap=0.4,
    height=400 if search_term else 800
)
st.plotly_chart(fig_compare, use_container_width=True)

# ============================
# Graph 2: Unsold Items
# ============================
st.subheader("📉 Highest Unsold Items")

if search_term:
    if selected_outlet == "All":
        unsold_agg = filtered_df.groupby("Items")[["Qty Purchased", "QTY Sold", "Unsold"]].sum().reset_index()
        top_unsold = unsold_agg.sort_values("Unsold", ascending=False).head(15)
        hover_data = ["Qty Purchased", "QTY Sold", "Unsold"]
    else:
        top_unsold = filtered_df.copy()
        hover_data = ["Outlet", "Qty Purchased", "QTY Sold", "Unsold"]
else:
    top_unsold = filtered_df.sort_values("Unsold", ascending=False).head(15)
    hover_data = ["Outlet", "Qty Purchased", "QTY Sold", "Unsold"]

fig_unsold = px.bar(
    top_unsold,
    x="Unsold",
    y="Items",
    orientation="h",
    text="Unsold",
    hover_data=hover_data,
    color="Unsold",
    color_continuous_scale="Reds",
)
fig_unsold.update_layout(
    yaxis=dict(autorange="reversed", tickmode='linear', tickson='boundaries'),
    bargap=0.4,
    height=500
)
st.plotly_chart(fig_unsold, use_container_width=True)

# ============================
# Table Section
# ============================
st.subheader("📋 Detailed Data View")
st.dataframe(filtered_df, use_container_width=True)

