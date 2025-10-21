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
file_path = "faisalka.xlsx"  # 👈 Update path if needed
df = pd.read_excel(file_path)

# ============================
# Preprocess
# ============================
df['Unsold'] = df['Purchase'] - df['Sold']

# ============================
# Sidebar Filters
# ============================
st.sidebar.header("🔍 Filters")
outlet_filter = st.sidebar.multiselect(
    "Select Outlet",
    options=df['Outlet'].unique(),
    default=df['Outlet'].unique()
)
category_filter = st.sidebar.multiselect(
    "Select Category",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# ============================
# Search bar
# ============================
search_term = st.text_input("Search Item (name or code):", "").strip().lower()

# ============================
# Filter Data
# ============================
filtered_df = df[
    (df['Outlet'].isin(outlet_filter)) &
    (df['Category'].isin(category_filter))
]

if search_term:
    filtered_df = filtered_df[
        df.apply(lambda row: search_term in str(row['Item']).lower() or search_term in str(row['Item Code']).lower(), axis=1)
    ]

# ============================
# Key Insights
# ============================
st.markdown("### 📊 Key Insights")
col1, col2, col3 = st.columns(3)
col1.metric("Total Purchase", f"{filtered_df['Purchase'].sum():,.0f}")
col2.metric("Total Sold", f"{filtered_df['Sold'].sum():,.0f}")
col3.metric("Total Unsold", f"{filtered_df['Unsold'].sum():,.0f}")

# ============================
# Graph Section
# ============================
if search_term:
    # Show outlet-wise Purchase vs Sold for that item
    st.subheader(f"🏪 Outlet-wise Purchase vs Sold for '{search_term.title()}'")
    item_graph = px.bar(
        filtered_df,
        x="Outlet",
        y=["Purchase", "Sold"],
        barmode="group",
        text_auto=True,
        hover_data=["Outlet", "Purchase", "Sold", "Unsold", "Category", "Item"],
        title="Outlet-wise Purchase vs Sold",
        height=400
    )
    st.plotly_chart(item_graph, use_container_width=True)

else:
    # Show overall Highest Unsold Items graph
    st.subheader("🏷️ Top 15 Items with Highest Unsold Quantities")
    top_unsold = filtered_df.sort_values(by="Unsold", ascending=False).head(15)
    unsold_graph = px.bar(
        top_unsold,
        x="Item",
        y="Unsold",
        text_auto=True,
        hover_data=["Outlet", "Purchase", "Sold", "Unsold", "Category"],
        color="Unsold",
        color_continuous_scale="Reds",
        title="Highest Unsold Items",
        height=500
    )
    st.plotly_chart(unsold_graph, use_container_width=True)

# ============================
# Table Section
# ============================
st.subheader("📋 Detailed Data View")
st.dataframe(filtered_df, use_container_width=True)
