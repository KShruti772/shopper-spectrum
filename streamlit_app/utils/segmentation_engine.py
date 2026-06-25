from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from .helpers import setup_logger, resolve_safe_path, safe_load_model

LOGGER = setup_logger(__name__)
ROOT_DIR = Path(__file__).resolve().parents[2]


def load_segmentation_artifacts(scaler_path: Path, model_path: Path) -> Tuple[StandardScaler, KMeans]:
    scaler_file = resolve_safe_path(scaler_path, base_dir=ROOT_DIR)
    model_file = resolve_safe_path(model_path, base_dir=ROOT_DIR)

    scaler = safe_load_model(scaler_file, base_dir=ROOT_DIR)
    model = safe_load_model(model_file, base_dir=ROOT_DIR)

    return scaler, model


def preprocess_rfm_input(recency: float, frequency: float, monetary: float) -> np.ndarray:
    sample = np.asarray([[recency, frequency, monetary]], dtype=float)
    return sample


def map_cluster_label(cluster_id: int) -> str:
    mapping = {
        0: "High-Value",
        1: "Regular",
        2: "Occasional",
        3: "At-Risk",
    }
    return mapping.get(cluster_id, f"Cluster {cluster_id}")


def derive_segment_insights(cluster_id: int) -> Dict[str, str]:
    insights = {
        "High-Value": {
            "description": "Customers with strong recency, frequency, and monetary value. Ideal for loyalty and VIP programs.",
            "strategy": "Offer premium bundles, high-touch outreach, and retention rewards.",
            "behavior": "Purchases often, spends more, and returns frequently.",
            "revenue_impact": "High lifetime value and stable revenue contribution.",
        },
        "Regular": {
            "description": "Consistent buyers who contribute reliable revenue and product demand.",
            "strategy": "Promote repeat purchase offers and cross-sell complementary items.",
            "behavior": "Moderate purchase frequency with dependable spending patterns.",
            "revenue_impact": "Good revenue stream with growth potential.",
        },
        "Occasional": {
            "description": "Customers who buy sporadically and may respond to reactivation campaigns.",
            "strategy": "Use email reminders, seasonal discounts, and personalized promotions.",
            "behavior": "Infrequent purchases and moderate order value.",
            "revenue_impact": "Opportunity to improve purchase frequency and average order value.",
        },
        "At-Risk": {
            "description": "Customers whose purchase activity has dropped significantly.",
            "strategy": "Deploy win-back offers, recovery marketing, and churn prevention campaigns.",
            "behavior": "Low frequency and recency, often with declining spend.",
            "revenue_impact": "High churn risk; recovering these customers improves retention efficiency.",
        },
    }
    return insights.get(map_cluster_label(cluster_id), {
        "description": "Cluster insights are unavailable.",
        "strategy": "Use general customer re-engagement tactics.",
        "behavior": "Not enough cluster metadata.",
        "revenue_impact": "Review model outputs for the segment.",
    })


def predict_rfm_segment(scaler: StandardScaler, model: KMeans, sample: np.ndarray) -> Tuple[int, str, Dict[str, str], float]:
    scaled = scaler.transform(sample)
    cluster_id = int(model.predict(scaled)[0])
    label = map_cluster_label(cluster_id)
    insights = derive_segment_insights(cluster_id)

    centers = model.cluster_centers_
    distance = np.linalg.norm(centers[cluster_id] - scaled[0])
    max_distance = float(np.max(np.linalg.norm(centers - scaled[0], axis=1)))
    confidence = float(np.clip(1.0 - distance / (max_distance + 1e-9), 0.0, 1.0))

    return cluster_id, label, insights, confidence
