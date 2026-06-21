import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def render():
    st.title("Customer Segmentation")

    processed = PROJECT_ROOT / "data" / "processed" / "rfm_clusters.csv"
    if not processed.exists():
        st.error("RFM clusters not found. Run the RFM analysis and KMeans scripts first.")
        return

    rfm = pd.read_csv(processed)

    st.markdown("### Cluster Overview")
    counts = rfm["segment"].value_counts().reset_index()
    counts.columns = ["segment", "count"]
    fig = px.bar(counts, x="segment", y="count", color="segment", title="Customers per Segment")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Cluster Summary (averages)")
    summary = rfm.groupby("segment")[ ["Recency", "Frequency", "Monetary"] ].mean().round(2).reset_index()
    st.dataframe(summary)

    st.markdown("### Explore Customers")
    seg = st.selectbox("Choose segment", options=rfm["segment"].unique())
    sample = rfm[rfm["segment"] == seg].sort_values("Monetary", ascending=False).head(50)
    st.dataframe(sample)

    csv = sample.to_csv(index=False).encode("utf-8")
    st.download_button("Download sample CSV", csv, file_name=f"{seg}_customers.csv")

    st.markdown("---")
    st.markdown("#### Notes")
    st.write("Segments are created via KMeans on RFM features and mapped to business labels. Use this view to inspect high-value customers and plan actions.")
