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
# FILE PATHS
# ===============================
SALES_FILE = "Salem.Xlsx"  # Replace with your sales file
CREDIT_FILE = "shams credit note sep.Xlsx"  # Replace with your credit note file

# ===============================
# LOAD SALES DATA
# ===============================
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

# ===============================
# LOAD CREDIT NOTE DATA
# ===============================
if os.path.exists(CREDIT_FILE):
    credit_df = pd.read_excel(CREDIT_FILE)
else:
    st.error(f"Credit Note file not found: {CREDIT_FILE}")
    st.stop()

# Detect the correct column for Item Code in credit note
st.write("Columns in Credit Note file:", credit_df.columns.tolist())
possible_names = ["Item Code", "ItemCode", "ITEM CODE", "Item"]  # add more variations if needed
for name in possible_names:
    if name in credit_df.columns:
        credit_col = name
        break
else:
    st.error("⚠️ Could not find 'Item Code' column in credit note file.")
    st.stop()

# Normalize credit note Item Codes
credit_items = credit_df[credit_col].astype(str).str.strip().tolist()

# ===============================
# ADD CREDIT NOTE COLUMN
# ===============================
sales_df["Credit Note"] = sales_df["Item Code"].apply(lambda x: "Yes" if x in credit_items else "No")

# ===============================
# KEY INSIGHTS
# ===============================
total_sales = sales_df["Total Sales"].sum() if "Total Sales" in sales_df.columns else 0
total_profit = sales_df["Total Profit"].sum() if "Total Profit" in sales_df.columns else 0
avg_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

credit_yes_count = sales_df[sales_df["Credit Note"] == "Yes"].shape[0]
credit_no_count = sales_df[sales_df["Credit Note"] == "No"].shape[0]

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

columns_to_show = ["Item Code", "Items", "Category", "Total Sales", "Total Profit", "Credit Note"]
columns_to_show = [col for col in columns_to_show if col in sales_df.columns]

st.dataframe(
    sales_df[columns_to_show]
    .sort_values(by="Total Sales", ascending=False)
    .reset_index(drop=True),
    use_container_width=True
)
