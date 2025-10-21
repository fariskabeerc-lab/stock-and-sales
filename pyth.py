import streamlit as st
import pandas as pd
import os

# ===============================
# CONFIGURATION
# ===============================
st.set_page_config(page_title="Sales & Profit Dashboard", layout="wide")

OUTLET_FILES = {
    "shams": "Salem.Xlsx"  # <-- replace with your sales file path
}

# ===============================
# PASSWORD PROTECTION
# ===============================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Sales & Profit Dashboard")
    password = st.text_input("Enter Password to Continue", type="password")
    if st.button("Login"):
        if password == "123123":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect password. Try again.")
    st.stop()

# ===============================
# LOAD ALL DATA
# ===============================
@st.cache_data
def load_all_outlet_data():
    all_data = []
    for outlet, file in OUTLET_FILES.items():
        if os.path.exists(file):
            df = pd.read_excel(file)
            df["Outlet"] = outlet
            all_data.append(df)
        else:
            st.warning(f"⚠️ File not found: {file}")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

df = load_all_outlet_data()

# Remove items without category
df = df[df["Category"].notna()]

# Ensure numeric
for col in ["Total Sales", "Total Profit"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Compute margin %
df["Margin %"] = (df["Total Profit"] / df["Total Sales"] * 100).fillna(0).round(2)

# ===============================
# CREDIT NOTE INTEGRATION
# ===============================
CREDIT_FILE = "shams credit note sep.Xlsx"  # <-- replace with your credit note file path
credit_items = []

if os.path.exists(CREDIT_FILE):
    credit_df = pd.read_excel(CREDIT_FILE)
    if "Item Code" in credit_df.columns:
        credit_items = credit_df["Item Code"].astype(str).tolist()
    elif "Barcode" in credit_df.columns:
        credit_items = credit_df["Barcode"].astype(str).tolist()
    else:
        st.warning("⚠️ Credit note file must have 'Item Code' or 'Barcode' column.")
else:
    st.warning(f"⚠️ Credit note file not found: {CREDIT_FILE}")

# Add Credit Note column
if not df.empty:
    df["Credit Note"] = df["Item Code"].astype(str).apply(lambda x: "Yes" if x in credit_items else "No")

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.header("🔍 Filters")

# Category Filter
categories = ["All"] + sorted(df["Category"].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)

# Exclude Categories Filter (multi-select)
exclude_categories = st.sidebar.multiselect("Exclude Categories", options=df["Category"].unique())

# Outlet Filter
outlets = ["All"] + sorted(df["Outlet"].unique().tolist())
selected_outlet = st.sidebar.selectbox("Select Outlet", outlets)

# Margin Filter (non-overlapping)
margin_filters = ["All", "< 0", "0 - 5", "5 - 10", "10 - 20", "20 - 30", "30 +"]
selected_margin = st.sidebar.selectbox("Select Margin Range (%)", margin_filters)

# ===============================
# APPLY FILTERS
# ===============================
filtered_df = df.copy()

# Include Category
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# Exclude Categories
if exclude_categories:
    filtered_df = filtered_df[~filtered_df["Category"].isin(exclude_categories)]

# Outlet
if selected_outlet != "All":
    filtered_df = filtered_df[filtered_df["Outlet"] == selected_outlet]

# Margin
if selected_margin != "All":
    if selected_margin == "< 0":
        filtered_df = filtered_df[filtered_df["Margin %"] < 0]
    elif selected_margin == "0 - 5":
        filtered_df = filtered_df[(filtered_df["Margin %"] >= 0) & (filtered_df["Margin %"] < 5)]
    elif selected_margin == "5 - 10":
        filtered_df = filtered_df[(filtered_df["Margin %"] >= 5) & (filtered_df["Margin %"] < 10)]
    elif selected_margin == "10 - 20":
        filtered_df = filtered_df[(filtered_df["Margin %"] >= 10) & (filtered_df["Margin %"] < 20)]
    elif selected_margin == "20 - 30":
        filtered_df = filtered_df[(filtered_df["Margin %"] >= 20) & (filtered_df["Margin %"] < 30)]
    elif selected_margin == "30 +":
        filtered_df = filtered_df[filtered_df["Margin %"] >= 30]

# ===============================
# SEARCH BAR
# ===============================
st.title("📊 Sales & Profit Insights (Sep)")

search_term = st.text_input("🔎 Search Item Name", placeholder="Type an item name...")
if search_term:
    filtered_df = filtered_df[filtered_df["Items"].str.contains(search_term, case=False, na=False)]

# ===============================
# KEY INSIGHTS
# ===============================
if not filtered_df.empty:
    total_sales = filtered_df["Total Sales"].sum()
    total_profit = filtered_df["Total Profit"].sum()
    avg_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

    credit_yes = filtered_df[filtered_df["Credit Note"] == "Yes"]
    credit_no = filtered_df[filtered_df["Credit Note"] == "No"]

    total_sales_credit_yes = credit_yes["Total Sales"].sum()
    total_sales_credit_no = credit_no["Total Sales"].sum()

    st.subheader("📈 Key Insights")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💰 Total Sales", f"{total_sales:,.2f}")
    c2.metric("📊 Total Profit", f"{total_profit:,.2f}")
    c3.metric("⚙️ Avg. Margin %", f"{avg_margin:.2f}%")
    c4.metric("✅ Credit Note Items (Sales)", f"{total_sales_credit_yes:,.2f}")
    c5.metric("❌ Non-Credit Note Items (Sales)", f"{total_sales_credit_no:,.2f}")
else:
    st.warning("No data found for the selected filters or search term.")

# ===============================
# ITEM-WISE DETAILS
# ===============================
st.subheader("📋 Item-wise Sales, Profit, Margin & Credit Note Status")

if not filtered_df.empty:
    st.dataframe(
        filtered_df[["Outlet", "Category", "Items", "Total Sales", "Total Profit", "Margin %", "Credit Note"]]
        .sort_values(by="Margin %", ascending=True)
        .reset_index(drop=True),
        use_container_width=True,
        height=450
    )

# ===============================
# OUTLET-WISE TOTALS
# ===============================
st.subheader("🏪 Outlet-wise Total Sales, Profit & Avg Margin")

if not filtered_df.empty:
    outlet_summary = (
        filtered_df.groupby("Outlet")
        .agg({"Total Sales": "sum", "Total Profit": "sum"})
        .reset_index()
    )
    outlet_summary["Avg Margin %"] = (outlet_summary["Total Profit"] / outlet_summary["Total Sales"] * 100).round(2)
    st.dataframe(outlet_summary.sort_values("Total Sales", ascending=False), use_container_width=True, height=350)
else:
    st.info("No outlet data to display.")
