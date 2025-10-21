import streamlit as st
import pandas as pd

st.set_page_config(page_title="Negative Margin Items vs Credit Notes", layout="wide")
st.title("📋 Negative Margin Items in Sales but Not in Credit Notes")

# ================================
# Load Data from fixed paths
# ================================
sales_file = r"Salem.Xlsx"
credit_file = r"shams credit note sep.Xlsx"

# Load Excel files
sales_df = pd.read_excel(sales_file)
credit_df = pd.read_excel(credit_file)

# Clean column names (remove leading/trailing spaces)
sales_df.columns = sales_df.columns.str.strip()
credit_df.columns = credit_df.columns.str.strip()

# Convert Item Code to string
sales_df['Item Code'] = sales_df['Item Code'].astype(str)
credit_df['Item Code'] = credit_df['Item Code'].astype(str)

# Filter only negative margin items
negative_margin_sales = sales_df[sales_df['Excise Margin (%)'] < 0]

# Find items in negative margin sales but not in credit notes
unmatched_items = negative_margin_sales[~negative_margin_sales['Item Code'].isin(credit_df['Item Code'])]

# Display results
st.subheader("📌 Negative Margin Items NOT in Credit Notes")
st.write(f"Total unmatched negative margin items: {unmatched_items.shape[0]}")

st.dataframe(unmatched_items[['Item Code', 'Items', 'Category', 'Total Sales', 'Total Profit', 'Excise Margin (%)']])

# Download option
def convert_df(df):
    return df.to_excel(index=False, engine='openpyxl')

st.download_button(
    label="📥 Download Unmatched Items as Excel",
    data=convert_df(unmatched_items),
    file_name="negative_margin_unmatched_items.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
