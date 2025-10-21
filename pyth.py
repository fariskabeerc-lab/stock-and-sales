import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sales vs Credit Notes", layout="wide")
st.title("📋 Items in Sales but Not in Credit Notes")

# ================================
# Load Data from fixed paths
# ================================
sales_file = r"Salem.Xlsx"
credit_file = r"shams credit note sep.Xlsx"

# Load Excel files
sales_df = pd.read_excel(sales_file)
credit_df = pd.read_excel(credit_file)

# Ensure Item Codes are strings
sales_df['Item Code'] = sales_df['Item Code'].astype(str)
credit_df['Item Code'] = credit_df['Item Code'].astype(str)

# Find items in sales but not in credit notes
unmatched_items = sales_df[~sales_df['Item Code'].isin(credit_df['Item Code'])]

# Display results
st.subheader("📌 Items in Sales but NOT in Credit Notes")
st.write(f"Total unmatched items: {unmatched_items.shape[0]}")

st.dataframe(unmatched_items[['Item Code', 'Items', 'Category', 'Total Sales', 'Total Profit']])

# Download option
def convert_df(df):
    return df.to_excel(index=False, engine='openpyxl')

st.download_button(
    label="📥 Download Unmatched Items as Excel",
    data=convert_df(unmatched_items),
    file_name="unmatched_items.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
