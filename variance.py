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

# ============================
# Sidebar Filters
# ============================
st.sidebar.header("🔍 Filters")
outlet_filter = st.sidebar.multiselect(
    "Select Outlet",
    options=df['Outlet'].unique(),
    default=df['Outlet'].unique()
)

# Search bar
search_term = st.text_input("Search Item (name or code):", "").strip().lower()

# ============================
# Filter Data
# ============================
filtered_df = df[df['Outlet'].isin(outlet_filter)]

if search_term:
    filtered_df = filtered_df[
        df.apply(
            lambda row: search_term in str(row['Items']).lower()
            or search_term in str(row['Item Code']).lower(),
            axis=1
        )
    ]

# ============================
# Key Insights
# ============================
st.markdown("### 📊 Key Insights")
col1, col2, col3 = st.columns(3)
col1.metric("Total Purchased", f"{filtered_df['Qty Purchased'].sum():,.0f}")
col2.metric("Total Sold", f"{filtered_df['QTY Sold'].sum():,.0f}")
col3.metric("Total Unsold", f"{filtered_df['Unsold'].sum():,.0f}")

# ============================
# Graph 1: Purchase vs Sold
# ============================
st.subheader("📊 Purchase vs Sold Comparison")

top_limit = 10 if search_term else 30
top_items = filtered_df.nlargest(top_limit, "Qty Purchased")

fig_compare = px.bar(
    top_items.melt(id_vars=["Items"], value_vars=["Qty Purchased", "QTY Sold"]),
    y="Items",
    x="value",
    color="variable",
    orientation="h",
    barmode="group",
    text="value",
    title=f"Top {top_limit} Items: Purchase vs Sold",
)
fig_compare.update_layout(yaxis=dict(autorange="reversed"), height=400 if search_term else 800)
st.plotly_chart(fig_compare, use_container_width=True)

# ============================
# Graph 2: Unsold Items
# ============================
st.subheader("📉 Highest Unsold Items")

if search_term:
    if len(outlet_filter) == len(df['Outlet'].unique()):
        # All outlets selected → aggregate total across all outlets
        unsold_agg = filtered_df.groupby("Items")[["Qty Purchased", "QTY Sold", "Unsold"]].sum().reset_index()
        top_unsold = unsold_agg.sort_values("Unsold", ascending=False).head(15)
        hover_data = ["Qty Purchased", "QTY Sold", "Unsold"]
    else:
        # Specific outlet(s) selected → show unsold per outlet
        top_unsold = filtered_df.copy()
        hover_data = ["Outlet", "Qty Purchased", "QTY Sold", "Unsold"]
else:
    # Default view → top 15 unsold items
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
    title="Highest Unsold Items",
)
fig_unsold.update_layout(yaxis=dict(autorange="reversed"), height=500)
st.plotly_chart(fig_unsold, use_container_width=True)

# ============================
# Table Section
# ============================
st.subheader("📋 Detailed Data View")
st.dataframe(filtered_df, use_container_width=True)
