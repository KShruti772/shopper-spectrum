"""
04_model_persistence_test.py

Demonstrates saving and loading a StandardScaler and KMeans model using `utils.model_persistence`.

The script will:
- Load RFM data (from data/processed/rfm_customers.csv or compute fallback)
- Train a simple StandardScaler + KMeans (k=4) if artifacts are not present
- Save artifacts to `models/kmeans_v1/`
- Load artifacts back and perform a prediction on a sample RFM row

Run:
    python notebooks/04_model_persistence_test.py
"""

from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from utils.model_persistence import save_artifacts, load_artifacts, predict_with_artifacts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RFM_FILE = PROJECT_ROOT / "data" / "processed" / "rfm_customers.csv"
MODELS_DIR = PROJECT_ROOT / "models"


def load_or_compute_rfm(rfm_path: Path) -> pd.DataFrame:
    """Load RFM scored CSV if present; otherwise attempt to compute using cleaning utilities."""
    if rfm_path.exists():
        rfm = pd.read_csv(rfm_path)
        return rfm

    # Fallback: compute RFM by reading raw dataset and using utils.cleaning
    try:
        from utils.cleaning import clean_retail_data
        raw, cleaned = clean_retail_data(str(PROJECT_ROOT / "online_retail.csv"))
        snapshot = cleaned["InvoiceDate"].max() + pd.Timedelta(days=1)
        grouped = cleaned.groupby("CustomerID")
        recency = grouped["InvoiceDate"].max().apply(lambda x: (snapshot - x).days).rename("Recency")
        frequency = grouped["InvoiceNo"].nunique().rename("Frequency")
        monetary = grouped["TotalPrice"].sum().rename("Monetary")
        rfm = pd.concat([recency, frequency, monetary], axis=1).reset_index()
        rfm.to_csv(rfm_path, index=False)
        print(f"Computed RFM and saved to {rfm_path}")
        return rfm
    except Exception as exc:
        raise RuntimeError("Could not load or compute RFM data: " + str(exc))


def train_and_save_sample(rfm: pd.DataFrame, k: int = 4):
    """Train scaler + KMeans and save artifacts to models directory."""
    features = ["Recency", "Frequency", "Monetary"]
    X = rfm[features].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)

    artifact_dir = save_artifacts(scaler, kmeans, MODELS_DIR, model_name="kmeans", version="v1")
    print(f"Saved scaler and model to {artifact_dir}")
    return artifact_dir


def test_prediction(artifact_dir: Path, rfm: pd.DataFrame):
    """Load artifacts and predict cluster for a sample customer and a manual example."""
    # Example 1: predict for the first customer in RFM
    sample = rfm.iloc[0]
    sample_row = [int(sample["Recency"]), int(sample["Frequency"]), float(sample["Monetary"])]
    label, model = predict_with_artifacts(artifact_dir, sample_row)
    print("Predicted cluster for first customer:", label)

    # Example 2: manual sample (e.g., very recent, high frequency, high monetary)
    manual = {"Recency": 10, "Frequency": 20, "Monetary": 2000.0}
    label2, _ = predict_with_artifacts(artifact_dir, manual)
    print("Predicted cluster for manual high-value sample:", label2)


def main():
    rfm = load_or_compute_rfm(RFM_FILE)

    # If no artifacts exist, train and save
    artifact_dir = MODELS_DIR / "kmeans_v1"
    if not artifact_dir.exists():
        print("No artifacts found; training KMeans and saving artifacts...")
        artifact_dir = train_and_save_sample(rfm, k=4)
    else:
        print(f"Artifacts found in {artifact_dir}; skipping training.")

    # Load and test predictions
    scaler, model, metadata = load_artifacts(artifact_dir)
    print("Loaded artifacts metadata:", metadata)

    test_prediction(artifact_dir, rfm)


if __name__ == "__main__":
    main()
