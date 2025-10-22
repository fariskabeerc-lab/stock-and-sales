import streamlit as st
import pandas as pd
import plotly.express as px

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(page_title="Purchase & Profit Dashboard", layout="wide")
st.title("📦 PURCHASE & PROFIT INSIGHTS")

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()  # Clean column names
    return df

file_path = "purchase_data.xlsx"  # <-- Change file name here
df = load_data(file_path)

# ===============================
# FILTERS
# ===============================
col1, col2 = st.columns(2)
outlet_filter = col1.multiselect("🏪 Select Outlet", options=sorted(df["outlet"].unique()))
item_filter = col2.multiselect("📦 Select Item", options=sorted(df["Items"].unique()))

filtered_df = df.copy()
if outlet_filter:
    filtered_df = filtered_df[filtered_df["outlet"].isin(outlet_filter)]
if item_filter:
    filtered_df = filtered_df[filtered_df["Items"].isin(item_filter)]

# ===============================
# KEY METRICS
# ===============================
total_purchase = filtered_df["TOTEL PURCHASE"].sum()
total_profit = filtered_df["Total Profit"].sum()

if len(outlet_filter) == 1:
    avg_purchase = filtered_df["TOTEL PURCHASE"].mean()
else:
    avg_purchase = None

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Purchase", f"{total_purchase:,.0f}")
col2.metric("📈 Total Profit", f"{total_profit:,.0f}")
if avg_purchase:
    col3.metric("📊 Avg Purchase (Selected Outlet)", f"{avg_purchase:,.0f}")

# ===============================
# PURCHASE vs PROFIT BAR CHART
# ===============================
st.markdown("### 📊 Purchase & Profit Comparison by Item")

if not filtered_df.empty:
    bar_height = 400 if len(filtered_df["Items"].unique()) > 10 else 300

    fig_bar = px.bar(
        filtered_df,
        x="TOTEL PURCHASE",
        y="Items",
        orientation="h",
        color="Total Profit",
        color_continuous_scale=["#E74C3C", "#27AE60"],
        text="TOTEL PURCHASE",
        title="Items Purchase & Profit",
        hover_data={"Total Profit": ":,.0f", "TOTEL PURCHASE": ":,.0f"},
    )

    fig_bar.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        marker_line_width=0,
    )

    fig_bar.update_layout(
        xaxis_title="Total Purchase",
        yaxis_title="Items",
        height=bar_height,
        bargap=0.3,
        title_font=dict(size=20),
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=False),
        coloraxis_showscale=True,
    )

    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("Please select filters or check your data.")

# ===============================
# OUTLET-WISE SALES WHEN ITEM SELECTED
# ===============================
if item_filter and not outlet_filter:
    st.markdown("### 🏪 Top Outlets for Selected Item(s)")
    item_df = df[df["Items"].isin(item_filter)]

    fig_outlet = px.bar(
        item_df.groupby("outlet", as_index=False).sum(),
        x="TOTEL PURCHASE",
        y="outlet",
        orientation="h",
        color="TOTEL PURCHASE",
        color_continuous_scale="Reds",
        text="TOTEL PURCHASE",
        title="Outlet-wise Purchase (Selected Item)",
    )

    fig_outlet.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        marker_line_width=0,
    )

    fig_outlet.update_layout(
        xaxis_title="Total Purchase",
        yaxis_title="Outlet",
        height=350,
        bargap=0.4,
    )

    st.plotly_chart(fig_outlet, use_container_width=True)

# ===============================
# DISPLAY FILTERED TABLE
# ===============================
st.markdown("### 📋 Filtered Data")
st.dataframe(filtered_df, use_container_width=True)
