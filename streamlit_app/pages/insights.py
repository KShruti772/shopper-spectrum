import streamlit as st
from pathlib import Path

from utils.helpers import show_error_message
from utils.model_loader import find_dataset_path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = find_dataset_path()


def render():
    st.markdown("# Business Insights")
    st.markdown("Turn data into action with customer, product, and campaign recommendations.")

    if DATA_PATH is None:
        show_error_message("Retail dataset unavailable.", "Place the dataset in the project root or data/ folder.")
        return

    st.markdown("## What you can do next")
    st.markdown(
        "- Review customer segments to identify high-value and at-risk segments.\n"
        "- Use product recommendations to power merchandising and cross-sell strategies.\n"
        "- Combine purchase behavior with RFM insights to personalize promotions and reduce churn."
    )

    st.markdown("## Suggested action plan")
    st.write(
        "1. Run the segmentation module and capture the top-tier customer profiles.\n"
        "2. Use recommendation insights to bundle best-selling products.\n"
        "3. Monitor analytics trends on the home dashboard and refine your promotions."
    )

    st.markdown("## Resource checklist")
    st.write(
        "- Dataset loaded from `online_retail.csv` or `data/online_retail.csv`.\n"
        "- `models/scaler.pkl` and `models/kmeans_model.pkl` for segmentation.\n"
        "- `models/similarity_matrix.pkl` for recommendation quality."
    )

    st.markdown("## Deployment note")
    st.write(
        "Streamlit pages are modular and can be reused in a deployed SaaS dashboard. "
        "Ensure the dataset and model files are accessible to the deployment environment."
    )
