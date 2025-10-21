# ============================
# Graph 1: Purchase vs Sold (with gap)
# ============================
st.subheader("📊 Purchase vs Sold Comparison")

top_limit = 10 if search_term else 30

# Aggregate values per item when search is active
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
    title=f"Top {top_limit} Items: Purchase vs Sold",
)
# Add spacing between items
fig_compare.update_layout(
    yaxis=dict(autorange="reversed", tickmode='linear', tickson='boundaries'),
    bargap=0.4,  # Gap between bars for each item
    height=400 if search_term else 800
)
st.plotly_chart(fig_compare, use_container_width=True)

# ============================
# Graph 2: Unsold Items (with gap)
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
    bargap=0.4,  # Adds gap between bars
    height=500
)
st.plotly_chart(fig_unsold, use_container_width=True)
