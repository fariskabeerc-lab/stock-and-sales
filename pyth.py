import streamlit as st
import pandas as pd

st.set_page_config(page_title="Negative Margin Items vs Credit Notes", layout="wide")
st.title("📋 Negative Margin Items in Sales but Not in Credit Notes")

# ================================
# File paths
# ================================
sales_file = r"Salem.Xlsx"
credit_file = r"shams credit note sep.Xlsx"

# ================================
# Load Sales Data
# ================================
sales_df = pd.read_excel(sales_file)
sales_df.columns = sales_df.columns.str.strip()  # clean column names

# ================================
# Load Credit Notes Data
# ================================
# Attempt to read headers from first row; if not, adjust header row
credit_df = pd.read_excel(credit_file, header=0)  # change to header=1 if real headers start at 2nd row
credit_df.columns = credit_df.columns.str.strip()  # clean column names

# Check if "Item Code" exists, otherwise try to guess the column
if 'Item Code' not in credit_df.columns:
    st.warning("Column 'Item Code' not found in credit notes. Attempting to use first column as Item Code.")
    credit_df.rename(columns={credit_df.columns[0]: 'Item Code'}, inplace=True)

# ================================
# Convert Item Code to string
# ================================
sales_df['Item Code'] = sales_df['Item Code'].astype(str)
credit_df['Item Code'] = credit_df['Item Code'].astype(str)

# ================================
# Filter Negative Margin Sales
# ================================
negative_margin_sales = sales_df[sales_df['Excise Margin (%)'] < 0]

# ================================
# Find unmatched items
# ================================
unmatched_items = negative_margin_sales[~negative_margin_sales['Item Code'].isin(credit_df['Item Code'])]

# ================================
# Display results
# ================================
st.subheader("📌 Negative Margin Items NOT in Credit Notes")
st.write(f"Total unmatched negative margin items: {unmatched_items.shape[0]}")

st.dataframe(unmatched_items[['Item Code', 'Items', 'Category', 'Total Sales', 'Total Profit', 'Excise Margin (%)']])

# ================================
# Download option
# ================================
def convert_df(df):
    return df.to_excel(index=False, engine='openpyxl')

st.download_button(
    label="📥 Download Unmatched Items as Excel",
    data=convert_df(unmatched_items),
    file_name="negative_margin_unmatched_items.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
