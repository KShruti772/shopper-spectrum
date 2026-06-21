import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def render():
    st.markdown("# Shopper Spectrum")
    st.markdown("### E-commerce analytics and recommendations — interactive dashboard")

    # Load data
    try:
        from utils.cleaning import clean_retail_data
        _, df = clean_retail_data(str(PROJECT_ROOT / "online_retail.csv"))
    except Exception:
        df = pd.read_csv(PROJECT_ROOT / "online_retail.csv")

    # Prepare key metrics with spinner
    with st.spinner("Computing metrics..."):
        total_transactions = df.shape[0]
        total_customers = int(df["CustomerID"].nunique(dropna=True))
        total_revenue = float(df["TotalPrice"].sum()) if "TotalPrice" in df.columns else float((df["Quantity"] * df["UnitPrice"]).sum())
        avg_order = total_revenue / total_transactions if total_transactions else 0
        avg_order = float(avg_order)

    # KPI cards
    k1, k2, k3, k4 = st.columns([1,1,1,1])
    k1.markdown("<div class='card kpi'><div class='value'>%s</div><div class='label'>Transactions</div></div>" % f"{total_transactions:,}", unsafe_allow_html=True)
    k2.markdown("<div class='card kpi'><div class='value'>%s</div><div class='label'>Customers</div></div>" % f"{total_customers:,}", unsafe_allow_html=True)
    k3.markdown("<div class='card kpi'><div class='value'>${:,.2f}</div><div class='label'>Total Revenue</div></div>".format(total_revenue), unsafe_allow_html=True)
    k4.markdown("<div class='card kpi'><div class='value'>${:,.2f}</div><div class='label'>Avg Order</div></div>".format(avg_order), unsafe_allow_html=True)

    st.markdown("---")

    # Tabs for interactive charts and segment analytics
    tab1, tab2 = st.tabs(["Overview", "Segments & Products"])

    with tab1:
        st.subheader("Sales & Product Popularity")
        # Monthly sales trend (plotly)
        df_dates = df.dropna(subset=["InvoiceDate"]).copy()
        df_dates["InvoiceDate"] = pd.to_datetime(df_dates["InvoiceDate"], errors="coerce")
        df_dates["YearMonth"] = df_dates["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
        monthly = df_dates.groupby("YearMonth")["TotalPrice"].sum().reset_index()
        fig_month = px.line(monthly, x="YearMonth", y="TotalPrice", title="Monthly Revenue", markers=True)
        st.plotly_chart(fig_month, use_container_width=True)

        # Product popularity
        st.subheader("Top Products by Quantity")
        prod_pop = df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(10).reset_index()
        fig_prod = px.bar(prod_pop, x="Quantity", y="Description", orientation="h", title="Top 10 Products", labels={"Quantity":"Total Quantity","Description":"Product"})
        st.plotly_chart(fig_prod, use_container_width=True)

        with st.expander("Download top products CSV"):
            csv = prod_pop.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, file_name="top_products.csv")

    with tab2:
        st.subheader("Customer Segment Analytics")
        processed = PROJECT_ROOT / "data" / "processed" / "rfm_clusters.csv"
        if not processed.exists():
            st.info("RFM clusters not available. Run RFM/KMeans scripts to populate segment analytics.")
        else:
            rfm = pd.read_csv(processed)
            # Pie chart for cluster distribution
            seg_counts = rfm["segment"].value_counts().reset_index()
            seg_counts.columns = ["segment","count"]
            fig_pie = px.pie(seg_counts, names="segment", values="count", title="Customer Segment Distribution", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

            # Segment summary table
            seg_summary = rfm.groupby("segment")[ ["Recency","Frequency","Monetary"] ].agg(["mean","median","count"]).round(2)
            st.dataframe(seg_summary)

            with st.expander("Download full RFM customers CSV"):
                csv = rfm.to_csv(index=False).encode("utf-8")
                st.download_button("Download RFM CSV", csv, file_name="rfm_customers.csv")

    st.markdown("---")
    st.markdown("<div class='footer'>Built with care — Shopper Spectrum</div>", unsafe_allow_html=True)
