import streamlit as st
from pathlib import Path

import pandas as pd
import plotly.express as px

from utils.dashboard_helpers import (
    build_country_sales_chart,
    build_daily_transactions_chart,
    build_monthly_sales_chart,
    build_recommendation_preview,
    build_revenue_distribution_chart,
    build_segment_distribution_chart,
    build_top_products_chart,
    compute_kpis,
    format_currency,
    format_number,
    generate_customer_segments,
    get_customer_insights,
    load_rfm_segments,
    load_transaction_data,
    summarize_missing_values,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _render_hero():
    st.markdown(
        """
        <div class='hero'>
            <div class='hero-badge'>🚀 Portfolio-ready e-commerce analytics</div>
            <h1 class='hero-title'>Shopper Spectrum Dashboard</h1>
            <p class='hero-description'>A premium home page for customer segmentation, product recommendations, and revenue performance monitoring. Designed for modern presentations, internship portfolios, and GitHub showcase.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_metadata_cards(kpis: dict):
    card_layout = st.columns(4, gap="large")
    contents = [
        ("👥 Total Customers", format_number(kpis["total_customers"]), "Active shoppers in the dataset."),
        ("₹ Total Revenue", format_currency(kpis["total_revenue"]), "Sum of purchase value across all invoices."),
        ("🧾 Total Transactions", format_number(kpis["total_transactions"]), "Total recorded invoices and orders."),
        ("📦 Total Products", format_number(kpis["total_products"]), "Unique product SKUs sold."),
    ]

    for column, (title, value, caption) in zip(card_layout, contents):
        column.markdown(
            f"""
            <div class='metric-card'>
                <h4>{title}</h4>
                <div class='metric-value'>{value}</div>
                <div class='metric-meta'>{caption}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_dataset_overview(df: pd.DataFrame):
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Dataset Overview</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3, gap="large")
    col1.metric("Rows", format_number(df.shape[0]))
    col2.metric("Columns", format_number(df.shape[1]))
    col3.metric("Missing fields", format_number(int(df.isna().sum().sum())))

    with st.expander("Preview data and quality summary", expanded=False):
        st.dataframe(df.head(8), use_container_width=True)
        missing = summarize_missing_values(df)
        st.markdown("**Missing value summary**")
        st.dataframe(missing, use_container_width=True)

    column_descriptions = pd.DataFrame(
        [
            ("InvoiceNo", "Unique invoice identifier."),
            ("StockCode", "Product SKU code."),
            ("Description", "Product description."),
            ("Quantity", "Units sold per transaction line."),
            ("InvoiceDate", "Transaction timestamp."),
            ("UnitPrice", "Sale price per unit."),
            ("CustomerID", "Unique customer identifier."),
            ("Country", "Customer shipping country."),
            ("TotalPrice", "Line revenue: Quantity × UnitPrice."),
        ],
        columns=["Column", "Description"],
    )
    st.markdown("**Column definitions**")
    st.dataframe(column_descriptions, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_sales_section(df: pd.DataFrame):
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Sales Performance</div>", unsafe_allow_html=True)

    with st.spinner("Rendering sales charts..."):
        tab1, tab2 = st.tabs(["Trend & Distribution", "Product & Geography"])

        with tab1:
            chart1, chart2 = st.columns(2, gap="large")
            with chart1:
                st.plotly_chart(build_monthly_sales_chart(df), use_container_width=True)
            with chart2:
                st.plotly_chart(build_revenue_distribution_chart(df), use_container_width=True)
            st.plotly_chart(build_daily_transactions_chart(df), use_container_width=True)

        with tab2:
            chart1, chart2 = st.columns(2, gap="large")
            with chart1:
                st.plotly_chart(build_country_sales_chart(df), use_container_width=True)
            with chart2:
                st.plotly_chart(build_top_products_chart(df), use_container_width=True)

    with st.expander("View revenue map and regional insights", expanded=False):
        if "Country" in df.columns and "TotalPrice" in df.columns:
            try:
                geo = df.groupby("Country", as_index=False)["TotalPrice"].sum()
                fig_map = px.choropleth(
                    geo,
                    locations="Country",
                    locationmode="country names",
                    color="TotalPrice",
                    title="Revenue by Country",
                    color_continuous_scale="Blues",
                )
                st.plotly_chart(fig_map, use_container_width=True)
            except Exception as exc:
                st.warning("Country map is unavailable: %s" % str(exc))
        else:
            st.info("Country or TotalPrice column missing; geographic map cannot render.")

    st.markdown("</div>", unsafe_allow_html=True)


def _render_customer_insights(df: pd.DataFrame, rfm_segments: pd.DataFrame):
    insights = get_customer_insights(df)
    segments = rfm_segments.copy() if not rfm_segments.empty and "segment" in rfm_segments.columns else generate_customer_segments(df)
    segment_counts = segments["segment"].value_counts().sort_values(ascending=False)
    sourced_from_model = not rfm_segments.empty and "segment" in rfm_segments.columns

    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Customer Insights</div>", unsafe_allow_html=True)

    row1, row2 = st.columns(2, gap="large")
    with row1:
        st.markdown(
            f"<div class='info-card'><h4>Highest spending country</h4><p>{insights['highest_spending_country']}</p></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='info-card'><h4>Average order value</h4><p>{insights['average_order_value']}</p></div>",
            unsafe_allow_html=True,
        )
    with row2:
        st.markdown(
            f"<div class='info-card'><h4>Top customer</h4><p>{insights['top_customer']}</p></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='info-card'><h4>Busiest month</h4><p>{insights['busiest_month']}</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Segment Preview</div>", unsafe_allow_html=True)
    split1, split2 = st.columns([1.6, 1], gap="large")
    with split1:
        st.plotly_chart(build_segment_distribution_chart(segment_counts), use_container_width=True)
    with split2:
        for label, count in segment_counts.items():
            percent = (count / segment_counts.sum()) * 100
            st.markdown(
                f"<div class='metric-card'><h4>{label}</h4><div class='metric-value'>{format_number(count)}</div><div class='metric-meta'>{percent:.1f}% of customers</div></div>",
                unsafe_allow_html=True,
            )
        source_label = "Model-based segments" if sourced_from_model else "Behavioral preview segments"
        st.markdown(f"<p class='metric-meta'><strong>Segment source:</strong> {source_label}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_recommendation_preview(df: pd.DataFrame):
    preview = build_recommendation_preview(df, top_n=6)
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Recommendation Engine Preview</div>", unsafe_allow_html=True)

    st.markdown(
        f"<div class='info-card'><h4>Summary</h4><p>{preview['summary']}</p></div>",
        unsafe_allow_html=True,
    )

    if not preview["popular_products"].empty:
        st.markdown("<div class='section-title'>Popular Products</div>", unsafe_allow_html=True)
        st.dataframe(preview["popular_products"], use_container_width=True)
    else:
        st.info("Popular product preview is unavailable due to missing item-level sales data.")

    if not preview["recommendations"].empty:
        st.markdown("<div class='section-title'>Sample Recommendations</div>", unsafe_allow_html=True)
        st.dataframe(preview["recommendations"].head(8), use_container_width=True)
    else:
        st.info("Recommendation preview cannot be generated because the recommendation model has not been built or the dataset is too small.")

    st.markdown("</div>", unsafe_allow_html=True)


def render():
    st.sidebar.title("🏠 Home Dashboard")
    st.sidebar.markdown("Dashboard homepage with dataset overview and insights.")
    
    with st.sidebar:
        refresh = st.button("🔄 Refresh data")
        if refresh:
            st.rerun()

    _render_hero()

    data_path = PROJECT_ROOT / "online_retail.csv"
    rfm_path = PROJECT_ROOT / "data" / "processed" / "rfm_clusters.csv"

    try:
        with st.spinner("Loading and validating transaction data..."):
            transactions = load_transaction_data(data_path)
            rfm_segments = load_rfm_segments(rfm_path)
    except FileNotFoundError as exc:
        st.error(f"Required data file not found: {exc}")
        return
    except ValueError as exc:
        st.error(f"Dataset validation failed: {exc}")
        return
    except Exception as exc:
        st.error(f"Unexpected error while loading dataset: {exc}")
        return

    if transactions.empty:
        st.warning("The dataset was loaded but contains no valid transactions after cleaning.")
        return

    kpis = compute_kpis(transactions)
    _render_metadata_cards(kpis)

    tabs = st.tabs(["Dataset Overview", "Sales Overview", "Customer Insights", "Recommendation Preview"])

    with tabs[0]:
        _render_dataset_overview(transactions)

    with tabs[1]:
        _render_sales_section(transactions)

    with tabs[2]:
        _render_customer_insights(transactions, rfm_segments)

    with tabs[3]:
        _render_recommendation_preview(transactions)

    st.markdown("---")
    st.markdown(
        "<div class='footer-panel'><strong>Shopper Spectrum</strong> • Python · Streamlit · pandas · Plotly · scikit-learn · NumPy" 
        "<br>Developer: Vighnesh • GitHub: <a href='#'>github.com/your-repo</a> • LinkedIn: <a href='#'>linkedin.com/in/your-name</a></div>",
        unsafe_allow_html=True,
    )

