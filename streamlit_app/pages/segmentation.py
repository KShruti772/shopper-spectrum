import streamlit as st
import plotly.express as px
from pathlib import Path

from utils.helpers import log_error, show_error_message
from utils.model_loader import load_pickle_resource
from utils.segmentation_engine import (
    load_segmentation_artifacts,
    preprocess_rfm_input,
    predict_rfm_segment,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCALER_PATH = PROJECT_ROOT / "models" / "scaler.pkl"
KMEANS_PATH = PROJECT_ROOT / "models" / "kmeans_model.pkl"


def _render_header():
    st.markdown("# 👥 Customer Segmentation")
    st.markdown("Map RFM values to business-ready customer segments and receive strategy guidance.")


def _render_sidebar():
    st.sidebar.header("📊 Segmentation Dashboard")
    st.sidebar.info("Provide Recency, Frequency, and Monetary values to classify a customer segment.")


def _render_rfm_form():
    with st.form("rfm_form"):
        st.markdown("### 📈 Predict customer segment from RFM")
        recency = st.number_input(
            "Recency (days since last purchase)",
            min_value=0,
            value=30,
            step=1,
            help="Number of days since the customer's last purchase.",
        )
        frequency = st.number_input(
            "Frequency (number of purchases)",
            min_value=0,
            value=4,
            step=1,
            help="How many orders the customer completed.",
        )
        monetary = st.number_input(
            "Monetary (total spend)",
            min_value=0.0,
            value=220.0,
            step=1.0,
            format="%.2f",
            help="Total revenue contributed by this customer.",
        )
        submitted = st.form_submit_button("🔮 Predict Segment")
    return submitted, recency, frequency, monetary


def _render_metrics(cluster_id: int, label: str, confidence: float):
    col1, col2, col3 = st.columns(3)
    col1.metric("Cluster ID", cluster_id)
    col2.metric("Segment", label)
    col3.metric("Confidence", f"{confidence * 100:.1f}%")


def _render_insights(insights: dict):
    st.markdown("### 💡 Segment Insights")
    st.markdown(f"**Description:** {insights['description']}")
    st.markdown(f"**Strategy:** {insights['strategy']}")
    st.markdown(f"**Customer behavior:** {insights['behavior']}")
    st.markdown(f"**Revenue impact:** {insights['revenue_impact']}")


def _render_cluster_chart(sample, predicted_label: str):
    try:
        fig = px.scatter(
            sample,
            x="Recency",
            y="Monetary",
            size="Frequency",
            color="Segment",
            title="Segment profiling overview",
            labels={"Recency": "Recency (days)", "Monetary": "Monetary value"},
        )
        fig.add_vline(x=60, line_dash="dash", line_color="#5fd0ff", annotation_text="Recency threshold")
        fig.add_hline(y=500, line_dash="dash", line_color="#f6c361", annotation_text="Monetary threshold")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        log_error(exc, "Rendering cluster chart")
        st.info("Chart preview unavailable.")


def _rule_based_segment(recency: float, frequency: float, monetary: float) -> tuple:
    """Rule-based segmentation using RFM thresholds when ML models unavailable."""
    if frequency >= 10 and monetary >= 800:
        if recency <= 30:
            label, cluster_id = "High-Value", 0
        else:
            label, cluster_id = "Regular", 1
    elif frequency >= 5 and monetary >= 300:
        label, cluster_id = "Regular", 1
    elif frequency >= 2:
        label, cluster_id = "Occasional", 2
    else:
        label, cluster_id = "At-Risk", 3
    
    insights_map = {
        0: {
            "description": "Frequent, recent purchasers with high spend. Premium customers.",
            "strategy": "Offer exclusive deals, early access, and VIP treatment.",
            "behavior": "Regular purchases, high AOV, consistent engagement.",
            "revenue_impact": "Highest lifetime value, stable revenue, low churn risk.",
        },
        1: {
            "description": "Reliable customers with moderate to high activity. Core segment.",
            "strategy": "Promote loyalty programs and cross-selling.",
            "behavior": "Periodic purchases, moderate order value.",
            "revenue_impact": "Good revenue contribution, moderate churn risk.",
        },
        2: {
            "description": "Infrequent buyers with growth potential.",
            "strategy": "Use seasonal campaigns and limited-time offers.",
            "behavior": "Occasional purchases, declining engagement.",
            "revenue_impact": "Opportunity segment, higher churn risk.",
        },
        3: {
            "description": "Low-activity, high churn-risk segment.",
            "strategy": "Deploy win-back campaigns with special discounts.",
            "behavior": "Few recent purchases, disengaged.",
            "revenue_impact": "Churn risk, recovery opportunity.",
        },
    }
    
    insights = insights_map.get(cluster_id, {})
    confidence = min(0.65 + (frequency / 20), 0.95)
    return cluster_id, label, insights, confidence


def render():
    _render_header()
    _render_sidebar()

    # Check if models exist
    models_available = SCALER_PATH.exists() and KMEANS_PATH.exists()
    if not models_available:
        st.warning(
            "⚠️ **Segmentation models not available**\n\n"
            "Using rule-based classification. For ML-powered predictions, ensure "
            "`scaler.pkl` and `kmeans_model.pkl` exist in the `models/` folder."
        )

    submitted, recency, frequency, monetary = _render_rfm_form()
    if not submitted:
        st.info("📋 Enter RFM values and click 'Predict Segment' to classify a customer.")
        st.markdown("---")
        st.markdown(
            "**RFM Explained:**\n"
            "- **Recency:** Days since last purchase\n"
            "- **Frequency:** Total purchase count\n"
            "- **Monetary:** Total lifetime value"
        )
        return

    if recency < 0 or frequency < 0 or monetary < 0:
        show_error_message("❌ Invalid input", "Recency, Frequency, and Monetary must be non-negative.")
        return

    # Try ML model if available
    cluster_id, label, insights, confidence = None, None, None, None
    if models_available:
        try:
            scaler, model = load_segmentation_artifacts(SCALER_PATH, KMEANS_PATH)
            sample = preprocess_rfm_input(recency, frequency, monetary)
            cluster_id, label, insights, confidence = predict_rfm_segment(scaler, model, sample)
        except Exception as exc:
            log_error(exc, "ML segmentation failed, falling back to rules")
            cluster_id, label, insights, confidence = _rule_based_segment(recency, frequency, monetary)
    else:
        # Use rule-based fallback
        cluster_id, label, insights, confidence = _rule_based_segment(recency, frequency, monetary)

    st.success(f"✅ Predicted segment: **{label}**")
    _render_metrics(cluster_id, label, confidence)
    _render_insights(insights)

    with st.expander("📊 View segment profile chart", expanded=False):
        sample_profiles = [
            {"Recency": 12, "Frequency": 20, "Monetary": 1450, "Segment": "High-Value"},
            {"Recency": 28, "Frequency": 10, "Monetary": 720, "Segment": "Regular"},
            {"Recency": 90, "Frequency": 5, "Monetary": 250, "Segment": "Occasional"},
            {"Recency": 190, "Frequency": 2, "Monetary": 90, "Segment": "At-Risk"},
            {"Recency": recency, "Frequency": frequency, "Monetary": monetary, "Segment": label},
        ]
        _render_cluster_chart(sample_profiles, label)

    with st.expander("ℹ️ Model information", expanded=False):
        if models_available:
            st.success("✅ ML models loaded")
            st.caption(f"Scaler: {SCALER_PATH.name} | Model: {KMEANS_PATH.name}")
        else:
            st.info("📌 Using rule-based classification")
        
        st.markdown(
            "**Segment Definitions:**\n"
            "- **High-Value:** Recent, frequent, high spend → VIP programs\n"
            "- **Regular:** Moderate activity → Loyalty\n"
            "- **Occasional:** Low frequency → Reactivation\n"
            "- **At-Risk:** Declining → Win-back campaigns"
        )
