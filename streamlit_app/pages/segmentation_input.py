import streamlit as st
from pathlib import Path
import numpy as np
import pandas as pd

from utils.model_persistence import load_artifacts

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models" / "kmeans_v1"


def _derive_segment_mapping(scaler, model):
    """Derive human-readable segment labels from KMeans cluster centers.

    We inverse-transform the scaled cluster centers to the original RFM space,
    compute a simple composite score (Monetary + Frequency - Recency) per cluster,
    and map the highest-scoring cluster to 'High-Value', next to 'Regular', then
    'Occasional', and lowest to 'At-Risk'. If there are more than 4 clusters,
    clusters are grouped into 4 buckets by composite quantiles.
    """
    centers_scaled = model.cluster_centers_  # shape (k, 3)
    centers = scaler.inverse_transform(centers_scaled)
    # centers columns correspond to Recency, Frequency, Monetary
    rec = centers[:, 0]
    freq = centers[:, 1]
    mon = centers[:, 2]

    # composite score: higher is better
    comp = (mon - np.mean(mon)) / (np.std(mon) + 1e-9) + (freq - np.mean(freq)) / (np.std(freq) + 1e-9) - (rec - np.mean(rec)) / (np.std(rec) + 1e-9)

    idx = np.argsort(-comp)  # descending
    labels = ["High-Value", "Regular", "Occasional", "At-Risk"]
    mapping = {}
    k = len(idx)
    if k <= 4:
        for i, cluster in enumerate(idx):
            mapping[int(cluster)] = labels[i]
    else:
        # split into 4 groups
        groups = np.array_split(idx, 4)
        for i, grp in enumerate(groups):
            for c in grp:
                mapping[int(c)] = labels[i]

    # Also provide a textual description per mapped label
    descriptions = {
        "High-Value": "Frequent, recent purchasers with high spend. Prioritize for retention and VIP programs.",
        "Regular": "Reliable customers with moderate to high frequency and spend. Target with loyalty incentives.",
        "Occasional": "Infrequent buyers with moderate spend. Use reactivation campaigns and promotions.",
        "At-Risk": "Customers with old last-purchase dates and low activity. Use win-back strategies.",
    }

    return mapping, descriptions


def _compute_confidence(scaler, model, sample_scaled):
    """Compute a heuristic confidence for the assigned cluster.

    We use distance to the assigned cluster center normalized by the max inter-center distance.
    Confidence = 1 - (distance / max_center_distance), clipped to [0,1].
    """
    centers = model.cluster_centers_
    dists = np.linalg.norm(centers - sample_scaled, axis=1)
    assigned = int(model.predict(sample_scaled.reshape(1, -1))[0])
    dist_assigned = dists[assigned]
    max_dist = dists.max() if dists.max() > 0 else 1.0
    conf = 1.0 - (dist_assigned / max_dist)
    conf = float(np.clip(conf, 0.0, 1.0))
    return assigned, conf


def render():
    st.title("Customer Segmentation — Predict a Customer Segment")

    st.markdown("Use the inputs below to predict which customer segment a given RFM profile belongs to.")

    with st.form("rfm_form"):
        col1, col2, col3 = st.columns(3)
        recency = col1.number_input("Recency (days since last purchase)", min_value=0, value=30, step=1)
        frequency = col2.number_input("Frequency (number of purchases)", min_value=0, value=3, step=1)
        monetary = col3.number_input("Monetary (total spend)", min_value=0.0, value=100.0, step=1.0, format="%.2f")

        submitted = st.form_submit_button("Predict Segment")

    if not submitted:
        st.info("Enter RFM values and click 'Predict Segment' to see the result.")
        return

    # Validation checks
    if recency < 0 or frequency < 0 or monetary < 0:
        st.error("Recency, Frequency, and Monetary must be non-negative values.")
        return

    # Load artifacts
    try:
        scaler, model, metadata = load_artifacts(MODELS_DIR)
    except Exception as e:
        st.error(f"Could not load model artifacts: {e}")
        return

    # Prepare sample and scale
    sample = np.array([[recency, frequency, monetary]], dtype=float)
    try:
        sample_scaled = scaler.transform(sample)
    except Exception as e:
        st.error(f"Error scaling input: {e}")
        return

    # Predict cluster
    try:
        pred = int(model.predict(sample_scaled)[0])
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return

    # Derive mapping and descriptions
    try:
        mapping, descriptions = _derive_segment_mapping(scaler, model)
        segment_name = mapping.get(pred, f"Cluster {pred}")
        description = descriptions.get(segment_name, "No description available.")
    except Exception:
        segment_name = f"Cluster {pred}"
        description = "Segment description not available."

    # Compute confidence
    try:
        assigned, confidence = _compute_confidence(scaler, model, sample_scaled.flatten())
    except Exception:
        confidence = None

    # Display results using styled cards
    st.success(f"Predicted segment: {segment_name}")

    card_col1, card_col2 = st.columns([2, 3])
    with card_col1:
        st.markdown("**Segment**")
        st.markdown(f"<div class='card'><h3>{segment_name}</h3><p>{description}</p></div>", unsafe_allow_html=True)

        if confidence is not None:
            st.markdown("**Confidence**")
            st.progress(int(confidence * 100))

    with card_col2:
        st.markdown("**Customer Snapshot**")
        st.write(f"Recency: {recency} days")
        st.write(f"Frequency: {frequency}")
        st.write(f"Monetary: ${monetary:,.2f}")

        # Marketing recommendation
        recommendations = {
            "High-Value": "Offer VIP perks, exclusive deals, and personalized outreach.",
            "Regular": "Promote loyalty programs and targeted cross-sells.",
            "Occasional": "Use timed promotions and reminders to increase purchase frequency.",
            "At-Risk": "Run win-back campaigns, discounts, and re-engagement emails.",
        }
        rec_text = recommendations.get(segment_name, "Consider retention and personalized messaging.")
        st.markdown("**Marketing Recommendation**")
        st.markdown(f"<div class='card'>{rec_text}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Note: Segmentation mapping is derived from the trained KMeans model centers when explicit labels are not available.")
