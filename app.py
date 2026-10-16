import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Industrial Demand & Inventory Insights", layout="wide")

st.title("Industrial Demand & Inventory Insights Dashboard")
st.markdown("**A simple analytics tool for small industrial / retail operations**")

# --------------------------
# Generate Sample Data
# --------------------------
@st.cache_data
def generate_sample_data():
    np.random.seed(42)
    
    products = [
        "Steel Rod 12mm", "Copper Wire 2.5mm", "Industrial Bearing 6205",
        "Hydraulic Pump", "Gear Box Type-A", "LED Panel Light",
        "PVC Pipe 1 inch", "Electric Motor 1HP", "Cutting Blade",
        "Safety Helmet", "Welding Electrode", "Control Valve"
    ]
    
    # Inventory Data
    inventory = pd.DataFrame({
        "Product": products,
        "Current_Stock": np.random.randint(5, 120, size=len(products)),
        "Reorder_Level": np.random.randint(15, 40, size=len(products)),
        "Unit_Cost": np.round(np.random.uniform(50, 2500, size=len(products)), 2)
    })
    
    # Sales Data (last 90 days)
    dates = [datetime.today() - timedelta(days=x) for x in range(90)]
    sales_records = []
    
    for date in dates:
        for product in products:
            if np.random.random() > 0.3:  # not every product sells every day
                qty = np.random.randint(1, 15)
                sales_records.append({
                    "Date": date.date(),
                    "Product": product,
                    "Quantity_Sold": qty
                })
    
    sales = pd.DataFrame(sales_records)
    return inventory, sales

inventory, sales = generate_sample_data()

# --------------------------
# Sidebar Filters
# --------------------------
st.sidebar.header("Filters")
selected_products = st.sidebar.multiselect(
    "Select Products", 
    options=inventory["Product"].tolist(),
    default=inventory["Product"].tolist()
)

# Filter data
inventory_filtered = inventory[inventory["Product"].isin(selected_products)]
sales_filtered = sales[sales["Product"].isin(selected_products)]

# --------------------------
# Key Metrics
# --------------------------
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_products = len(inventory_filtered)
low_stock_count = len(inventory_filtered[inventory_filtered["Current_Stock"] <= inventory_filtered["Reorder_Level"]])
total_stock_value = (inventory_filtered["Current_Stock"] * inventory_filtered["Unit_Cost"]).sum()
total_sales_qty = sales_filtered["Quantity_Sold"].sum()

col1.metric("Total Products", total_products)
col2.metric("Low Stock Items", low_stock_count, delta_color="inverse")
col3.metric("Total Inventory Value", f"₹{total_stock_value:,.0f}")
col4.metric("Total Units Sold (90 days)", f"{total_sales_qty:,}")

st.divider()

# --------------------------
# Low Stock Alert
# --------------------------
st.subheader("Low Stock Alerts (Reorder Needed)")

low_stock = inventory_filtered[inventory_filtered["Current_Stock"] <= inventory_filtered["Reorder_Level"]].copy()
low_stock["Shortage"] = low_stock["Reorder_Level"] - low_stock["Current_Stock"]

if len(low_stock) > 0:
    st.dataframe(
        low_stock[["Product", "Current_Stock", "Reorder_Level", "Shortage", "Unit_Cost"]],
        use_container_width=True
    )
else:
    st.success("No items are currently below reorder level.")

st.divider()

# --------------------------
# Demand Analysis
# --------------------------
st.subheader("Demand Analysis")

# Total sales by product
product_sales = sales_filtered.groupby("Product")["Quantity_Sold"].sum().sort_values(ascending=False)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Top Selling Products**")
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    product_sales.head(8).plot(kind="barh", ax=ax1, color="steelblue")
    ax1.set_xlabel("Total Quantity Sold")
    ax1.invert_yaxis()
    st.pyplot(fig1)

with col2:
    st.markdown("**Current Stock vs Reorder Level**")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    x = np.arange(len(inventory_filtered))
    width = 0.35
    ax2.bar(x - width/2, inventory_filtered["Current_Stock"], width, label="Current Stock", color="skyblue")
    ax2.bar(x + width/2, inventory_filtered["Reorder_Level"], width, label="Reorder Level", color="salmon")
    ax2.set_xticks(x)
    ax2.set_xticklabels(inventory_filtered["Product"], rotation=45, ha="right", fontsize=8)
    ax2.legend()
    st.pyplot(fig2)

st.divider()

# --------------------------
# Daily Demand Trend
# --------------------------
st.subheader("Daily Demand Trend (All Selected Products)")

daily_sales = sales_filtered.groupby("Date")["Quantity_Sold"].sum().reset_index()
daily_sales["Date"] = pd.to_datetime(daily_sales["Date"])

fig3, ax3 = plt.subplots(figsize=(12, 4))
ax3.plot(daily_sales["Date"], daily_sales["Quantity_Sold"], color="green", linewidth=2)
ax3.set_xlabel("Date")
ax3.set_ylabel("Quantity Sold")
ax3.set_title("Overall Daily Sales Trend")
plt.xticks(rotation=45)
st.pyplot(fig3)

st.divider()

# --------------------------
# Full Inventory Table
# --------------------------
st.subheader("Complete Inventory Overview")
st.dataframe(inventory_filtered, use_container_width=True)

st.caption("This is a sample project for portfolio demonstration | Data is randomly generated")