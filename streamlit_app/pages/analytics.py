import streamlit as st
import pandas as pd
from pathlib import Path

from utils.helpers import log_error, show_error_message, render_metric_card
from utils.model_loader import find_dataset_path
from utils.dashboard_helpers import (
    compute_kpis,
    build_monthly_sales_chart,
    build_revenue_distribution_chart,
    build_top_products_chart,
    safe_bar_chart,
    safe_line_chart,
    safe_histogram,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = find_dataset_path()


def _display_kpi_cards(kpis: dict) -> None:
    """Display KPIs as professional metric cards."""
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        render_metric_card(
            "👥 Total Customers",
            f"{kpis.get('total_customers', 0):,.0f}",
            "Active shoppers in dataset"
        )
    
    with col2:
        render_metric_card(
            "💰 Total Revenue",
            f"₹{kpis.get('total_revenue', 0):,.0f}",
            "Sum of all transactions"
        )
    
    with col3:
        render_metric_card(
            "🧾 Total Transactions",
            f"{kpis.get('total_transactions', 0):,.0f}",
            "Total invoices recorded"
        )
    
    with col4:
        render_metric_card(
            "📦 Total Products",
            f"{kpis.get('total_products', 0):,.0f}",
            "Unique SKUs in catalog"
        )


def render():
    st.markdown("# 📊 Analytics")
    st.markdown("Explore sales, customer, and product performance metrics.")

    if DATA_PATH is None:
        show_error_message(
            "⚠️ Retail dataset not found.",
            "Please place online_retail.csv in the project root or data/ folder and refresh."
        )
        return

    try:
        df = pd.read_csv(DATA_PATH, low_memory=False)
        if df.empty:
            st.error("Dataset loaded but contains no rows.")
            return
    except Exception as exc:
        log_error(exc, "Loading analytics dataset")
        show_error_message(
            "❌ Unable to load dataset.",
            "Verify the CSV file is valid and try refreshing the page."
        )
        return

    # Compute and display KPIs
    try:
        kpis = compute_kpis(df)
        st.markdown("## 📈 Key Performance Indicators")
        _display_kpi_cards(kpis)
    except Exception as exc:
        log_error(exc, "Computing KPIs")
        st.warning("Unable to calculate KPI metrics. Dataset may be malformed.")

    st.markdown("---")
    st.markdown("## 💰 Revenue Analysis")

    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        if safe_line_chart(df, "monthly_revenue", "Build monthly revenue chart"):
            try:
                st.plotly_chart(build_monthly_sales_chart(df), use_container_width=True)
            except Exception as exc:
                log_error(exc, "Rendering monthly sales chart")
                st.info("Monthly revenue chart unavailable.")
    
    with col2:
        if safe_histogram(df, "revenue_distribution", "Build revenue distribution"):
            try:
                st.plotly_chart(build_revenue_distribution_chart(df), use_container_width=True)
            except Exception as exc:
                log_error(exc, "Rendering revenue distribution")
                st.info("Revenue distribution chart unavailable.")

    st.markdown("---")
    st.markdown("## 🏆 Top Performing Products")
    
    if safe_bar_chart(df, "top_products", "Build product chart"):
        try:
            st.plotly_chart(build_top_products_chart(df), use_container_width=True)
        except Exception as exc:
            log_error(exc, "Rendering top products chart")
            st.info("Top products chart unavailable.")

    st.markdown("---")
    with st.expander("📚 Analytics Guide", expanded=False):
        st.markdown(
            """
            **What this page shows:**
            - **KPIs:** Customer count, total revenue, transaction volume, product diversity
            - **Revenue Trends:** Monthly revenue pattern and distribution of order values
            - **Top Products:** Best-selling items by quantity
            
            **How to use this data:**
            1. Monitor KPI trends over time
            2. Identify seasonal patterns in revenue
            3. Focus marketing on top-performing products
            4. Use insights for inventory and campaign planning
            """
        )
