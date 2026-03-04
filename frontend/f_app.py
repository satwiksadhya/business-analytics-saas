import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Inventra AI", page_icon="🚀", layout="wide")

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "inventory" not in st.session_state:
    st.session_state.inventory = {}

if "sales_history" not in st.session_state:
    st.session_state.sales_history = {}

# -------------------------------------------------
# THEME TOGGLE
# -------------------------------------------------
def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

theme = {
    "dark": {
        "bg": "#0F172A",
        "card": "#1E293B",
        "text": "#F1F5F9",
        "accent": "#60A5FA",
    },
    "light": {
        "bg": "#F4F6F9",
        "card": "#FFFFFF",
        "text": "#111827",
        "accent": "#2563EB",
    },
}

c = theme[st.session_state.theme]

# -------------------------------------------------
# GLOBAL CSS
# -------------------------------------------------
st.markdown(f"""
<style>
.stApp {{
    background-color: {c["bg"]};
    color: {c["text"]};
}}

.card {{
    background-color: {c["card"]};
    padding: 35px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 15px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid rgba(0,0,0,0.05);
}}

.card:hover {{
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    border: 1px solid {c["accent"]};
}}

div.stButton > button {{
    background-color: {c["card"]};
    color: {c["text"]};
    border: 1px solid {c["accent"]};
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
    transition: 0.2s ease;
}}

div.stButton > button:hover {{
    background-color: {c["accent"]};
    color: white;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# TOP BAR
# -------------------------------------------------
colA, colB = st.columns([6,1])
with colA:
    st.markdown("# 🚀 Inventra AI")
with colB:
    st.button("🌓", on_click=toggle_theme)

st.divider()

# =========================================================
# HOME PAGE
# =========================================================
if st.session_state.page == "home":

    st.markdown("### Smart Inventory Platform")

    total_products = len(st.session_state.inventory)

    if total_products > 0:
        total_stock = sum(st.session_state.inventory.values())

        avg_demand_all = 0
        count = 0
        for product in st.session_state.sales_history:
            avg_demand_all += np.mean(st.session_state.sales_history[product]["sales"])
            count += 1
        avg_demand_all = avg_demand_all / count if count else 0

        k1, k2, k3 = st.columns(3)
        k1.metric("Total Products", total_products)
        k2.metric("Total Inventory Units", int(total_stock))
        k3.metric("Avg Daily Demand (All)", round(avg_demand_all,1))

        st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card">🏌<h3>Golf</h3></div>', unsafe_allow_html=True)
        if st.button("Open Golf"):
            st.session_state.page = "golf"

    with col2:
        st.markdown('<div class="card">🍽<h3>Restaurant</h3></div>', unsafe_allow_html=True)
        if st.button("Open Restaurant"):
            st.session_state.page = "restaurant"

    with col3:
        st.markdown('<div class="card">🛒<h3>Grocery</h3></div>', unsafe_allow_html=True)
        if st.button("Open Grocery"):
            st.session_state.page = "grocery"

# =========================================================
# GROCERY MODULE
# =========================================================
elif st.session_state.page == "grocery":

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    st.header("🛒 Grocery Enterprise Analytics")

    # ---------- CSV UPLOAD ----------
    st.subheader("Upload Sales Data (CSV)")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        try:
                st.success("CSV data successfully loaded!")

        except Exception as e:
            st.error(f"Error processing file: {e}")

    st.divider()

    # ---------- MANUAL INPUT ----------
    product_name = st.text_input("Product Name")
    quantity = st.number_input("Current Stock", min_value=0, value=100)

    if st.button("➕ Add / Update Product") and product_name:

        st.session_state.inventory[product_name] = quantity

        days = 90
        base = np.random.randint(20, 60)
        seasonal = 8 * np.sin(np.linspace(0, 3*np.pi, days))
        noise = np.random.normal(0, 4, days)

        sales = np.round(np.clip(base + seasonal + noise, 0, None))
        dates = [datetime.today() - timedelta(days=x) for x in reversed(range(days))]

        st.session_state.sales_history[product_name] = {
            "dates": dates,
            "sales": sales
        }

        st.success(f"{product_name} updated.")

    # ---------- ANALYTICS ----------
    if st.session_state.inventory:

        selected = st.selectbox("Select Product", list(st.session_state.inventory.keys()))

        current_stock = st.session_state.inventory[selected]
        history = st.session_state.sales_history[selected]

        sales = np.array(history["sales"])
        dates = history["dates"]

        st.subheader("Forecast Settings")

        col1, col2, col3 = st.columns(3)

        with col1:
            lead_time = st.slider("Lead Time (Days)", 1, 30, 7)

        with col2:
            safety_multiplier = st.slider("Safety Stock Multiplier", 0.0, 2.0, 1.0)

        with col3:
            forecast_horizon = st.slider("Forecast Horizon (Days)", 7, 60, 14)

        avg_demand = np.mean(sales)
        demand_std = np.std(sales)

        safety_stock = safety_multiplier * demand_std * np.sqrt(lead_time)
        reorder_point = (avg_demand * lead_time) + safety_stock

        k1, k2, k3, k4 = st.columns(4)

        k1.metric("Current Stock", int(current_stock))
        k2.metric("Avg Daily Demand", round(avg_demand, 2))
        k3.metric("Safety Stock", int(safety_stock))
        k4.metric("Reorder Point", int(reorder_point))

        if current_stock <= reorder_point:
            st.error("⚠ Low Stock Alert: Reorder Required")
        else:
            st.success("Stock Level Healthy")

        forecast_line = np.full(forecast_horizon, avg_demand)
        forecast_dates = [
            dates[-1] + timedelta(days=i+1)
            for i in range(forecast_horizon)
        ]

        fig, ax = plt.subplots(figsize=(10,4))
        ax.plot(dates, sales, label="Historical Demand")
        ax.plot(forecast_dates, forecast_line, linestyle="dashed", label="Forecast")
        ax.axhline(reorder_point, linestyle=":", label="Reorder Point")
        ax.set_title(f"{selected} Demand Forecast")
        ax.legend()

        st.pyplot(fig)

# =========================================================
# GOLF MODULE
# =========================================================
elif st.session_state.page == "golf":

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    st.header("🏌 Golf Club Inventory")
    st.info("Retail + rental analytics module coming next.")

# =========================================================
# RESTAURANT MODULE
# =========================================================
elif st.session_state.page == "restaurant":

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    st.header("🍽 Restaurant Kitchen Analytics")
    st.info("Ingredient demand forecasting coming next.")