import streamlit as st
import pandas as pd
import os

# ===============================
# CONFIGURATION
# ===============================
st.set_page_config(page_title="Sales & Credit Note Dashboard", layout="wide")

# ===============================
# PASSWORD PROTECTION
# ===============================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Dashboard")
    password = st.text_input("Enter Password to Continue", type="password")
    if st.button("Login"):
        if password == "123123":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect password")
    st.stop()

# ===============================
# LOAD SALES DATA
# ===============================
SALES_FILE = "Salem.Xlsx"  # Replace with your sales file

if os.path.exists(SALES_FILE):
    sales_df = pd.read_excel(SALES_FILE)
else:
    st.error(f"Sales file not found: {SALES_FILE}")
    st.stop()

# Ensure necessary columns
if "Item Code" not in sales_df.columns:
    st.error("Sales file must have 'Item Code' column")
    st.stop()

# Normalize sales Item Code
sales_df["Item Code"] = sales_df["Item Code"].astype(str).str.strip()

# Ensure numeric columns
for col in ["Total Sales", "Total Profit"]:
    if col in sales_df.columns:
        sales_df[col] = pd.to_numeric(sales_df[col], errors="coerce").fillna(0)

# Compute Margin %
if "Total Sales" in sales_df.columns and "Total Profit" in sales_df.columns:
    sales_df["Margin %"] = (sales_df["Total Profit"] / sales_df["Total Sales"] * 100).fillna(0).round(2)
else:
    sales_df["Margin %"] = 0

# ===============================
# CREDIT NOTE ITEM CODES
# ===============================
credit_items = [
    "6291069730531","6291069730562","6281001305026","9714226230912","1098551452576",
    "100077121778","100079323603","6290361320273","6290361320273","6291103658722",
    "8908004178027","8908004178027","8908004178027","6050633566569","8901440208259",
    "8902850036647","8902102126232","8902102126232","9963087000000","6050633566576",
    "6291069730586","6291069730579","6291101408619","6291108339169","8901440203421",
    "6281034000356","8901440001034","6291069730548","6290360452104","6290360453187",
    "6290360453194","8902102164241","8901440208266","6281001820284","6281001820291",
    "6290360468426","6290360468433","6290360468440","6290360468464","6290360468471",
    "6290360468488","8902102164289","8908004178591","200023898","6291101408633",
    "6291101408626","8901440217930","100075601837","100077820233","6291079218258",
    "6291079218258","6291069730555","6291101407438","6050633566552","9714226107016",
    "6291101715359","4200115199200","0990107529293","6805699956027","788364062413",
    "6290360271811"
]

credit_items = [str(x).strip() for x in credit_items]

# Add Credit Note column
sales_df["Credit Note"] = sales_df["Item Code"].apply(lambda x: "Yes" if x in credit_items else "No")

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.header("🔍 Filters")

# Category filter
categories = ["All"] + sorted(sales_df["Category"].dropna().unique().tolist()) if "Category" in sales_df.columns else ["All"]
selected_category = st.sidebar.selectbox("Select Category", categories)

# Outlet filter
outlets = ["All"] + sorted(sales_df["Outlet"].dropna().unique().tolist()) if "Outlet" in sales_df.columns else ["All"]
selected_outlet = st.sidebar.selectbox("Select Outlet", outlets)

# Margin filter
margin_filters = ["All", "< 0", "0 - 5", "5 - 10", "10 - 20", "20 - 30", "30 +"]
selected_margin = st.sidebar.selectbox("Select Margin Range (%)", margin_filters)

# ===============================
# APPLY FILTERS
# ===============================
filtered_df = sales_df.copy()

# Category
if selected_category != "All" and "Category" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# Outlet
if selected_outlet != "All" and "Outlet" in filtered_df.columns:
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
st.title("📊 Sales & Profit Insights")

search_term = st.text_input("🔎 Search Item Name", placeholder="Type an item name...")
if search_term and "Items" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Items"].str.contains(search_term, case=False, na=False)]

# ===============================
# KEY INSIGHTS
# ===============================
total_sales = filtered_df["Total Sales"].sum() if "Total Sales" in filtered_df.columns else 0
total_profit = filtered_df["Total Profit"].sum() if "Total Profit" in filtered_df.columns else 0
avg_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

credit_yes_count = filtered_df[filtered_df["Credit Note"] == "Yes"].shape[0]
credit_no_count = filtered_df[filtered_df["Credit Note"] == "No"].shape[0]

st.subheader("📈 Key Insights")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Total Sales", f"{total_sales:,.2f}")
c2.metric("📊 Total Profit", f"{total_profit:,.2f}")
c3.metric("⚙️ Avg. Margin %", f"{avg_margin:.2f}%")
c4.metric("✅ Credit Note Items", f"{credit_yes_count}")
c5.metric("❌ Non-Credit Note Items", f"{credit_no_count}")

# ===============================
# ITEM-WISE TABLE
# ===============================
st.subheader("📋 Item-wise Sales & Credit Note Status")

columns_to_show = ["Item Code", "Items", "Category", "Outlet", "Total Sales", "Total Profit", "Margin %", "Credit Note"]
columns_to_show = [col for col in columns_to_show if col in filtered_df.columns]

st.dataframe(
    filtered_df[columns_to_show]
    .sort_values(by="Margin %", ascending=True)
    .reset_index(drop=True),
    use_container_width=True,
    height=450
)

# ===============================
# OUTLET-WISE TOTALS
# ===============================
st.subheader("🏪 Outlet-wise Total Sales, Profit & Avg Margin")
if "Outlet" in filtered_df.columns and not filtered_df.empty:
    outlet_summary = (
        filtered_df.groupby("Outlet")
        .agg({"Total Sales": "sum", "Total Profit": "sum"})
        .reset_index()
    )
    outlet_summary["Avg Margin %"] = (outlet_summary["Total Profit"] / outlet_summary["Total Sales"] * 100).round(2)
    st.dataframe(outlet_summary.sort_values("Total Sales", ascending=False), use_container_width=True, height=350)
else:
    st.info("No outlet data to display.")
