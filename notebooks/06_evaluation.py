"""
06_evaluation.py

Evaluation utilities for customer segmentation and recommendations.

Includes:
- Elbow curve and silhouette analysis for KMeans
- Cluster distribution and profiling tables
- Similarity matrix visualization for products
- Recommendation quality evaluation (offline precision@k / recall@k)

Usage:
    python notebooks/06_evaluation.py

Requires: pandas, numpy, matplotlib, seaborn, scikit-learn

This script is written to be clear and modular so you can call functions
from notebooks or import them into a test harness.
"""

from pathlib import Path
import random
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

sns.set(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (10, 6)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RFM_CLUSTER_FILE = PROJECT_ROOT / "data" / "processed" / "rfm_clusters.csv"
RFM_FILE = PROJECT_ROOT / "data" / "processed" / "rfm_customers.csv"
TRANSACTIONS_FILE = PROJECT_ROOT / "online_retail.csv"


def load_rfm_and_clusters(rfm_path: Path = RFM_FILE, cluster_path: Path = RFM_CLUSTER_FILE):
    """Load RFM and clustered RFM dataframe if present.

    Returns (rfm, rfm_clusters). rfm is the basic RFM per customer, rfm_clusters includes segment/cluster labels.
    """
    rfm = pd.DataFrame()
    rfm_clusters = pd.DataFrame()
    if rfm_path.exists():
        rfm = pd.read_csv(rfm_path)
    if cluster_path.exists():
        rfm_clusters = pd.read_csv(cluster_path)
    return rfm, rfm_clusters


def elbow_curve(X: np.ndarray, k_range=range(1, 11)):
    """Compute inertia for KMeans across k_range and plot the elbow curve.

    X should be the feature matrix (already standardized if desired).
    """
    inertias = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X)
        inertias.append(km.inertia_)

    plt.figure()
    plt.plot(list(k_range), inertias, marker="o")
    plt.xlabel("Number of clusters k")
    plt.ylabel("Inertia (sum of squared distances)")
    plt.title("Elbow Curve for KMeans")
    plt.grid(True)
    out = PROJECT_ROOT / "images" / "eval_elbow.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    print(f"Saved elbow plot to {out}")
    plt.show()


def silhouette_analysis(X: np.ndarray, k_range=range(2, 11)):
    """Compute silhouette scores for KMeans across k_range and plot results.

    Silhouette score ranges from -1 to 1; higher is better. It measures how similar
    points are to their own cluster vs other clusters.
    """
    scores = []
    ks = []
    for k in k_range:
        if k <= 1 or k >= len(X):
            continue
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        score = silhouette_score(X, labels)
        ks.append(k)
        scores.append(score)

    plt.figure()
    plt.plot(ks, scores, marker="o", color="#2b8cbe")
    plt.xlabel("Number of clusters k")
    plt.ylabel("Silhouette Score")
    plt.title("Silhouette Score by k")
    plt.grid(True)
    out = PROJECT_ROOT / "images" / "eval_silhouette.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    print(f"Saved silhouette plot to {out}")
    plt.show()


def cluster_distribution(rfm_clusters: pd.DataFrame):
    """Show cluster distribution and basic counts. rfm_clusters should include a 'segment' or 'cluster' column."""
    if rfm_clusters.empty:
        print("No cluster data available to analyze.")
        return

    col = "segment" if "segment" in rfm_clusters.columns else "cluster"
    counts = rfm_clusters[col].value_counts().sort_index()
    print("Cluster distribution:\n", counts.to_string())

    plt.figure()
    counts.plot.pie(autopct="%1.1f%%", ylabel="", title="Cluster Distribution")
    out = PROJECT_ROOT / "images" / "eval_cluster_distribution.png"
    plt.savefig(out, dpi=150)
    plt.show()


def cluster_profiling(rfm_clusters: pd.DataFrame):
    """Produce profiling tables (mean/median/count) for each cluster/segment and save to CSV."""
    if rfm_clusters.empty:
        print("No cluster data available for profiling.")
        return

    group_col = "segment" if "segment" in rfm_clusters.columns else "cluster"
    metrics = ["Recency", "Frequency", "Monetary"]
    prof = rfm_clusters.groupby(group_col)[metrics].agg(["mean", "median", "count"]).round(2)
    out = PROJECT_ROOT / "images" / "eval_cluster_profile.csv"
    prof.to_csv(out)
    print(f"Saved cluster profiling CSV to {out}")
    print(prof)
    return prof


def visualize_similarity_matrix(df_transactions: pd.DataFrame, top_n_products: int = 50):
    """Compute and visualize a product-product similarity heatmap for the top N products by popularity.

    For performance, restrict to top_n_products by total quantity.
    """
    pivot = pd.pivot_table(df_transactions, index="CustomerID", columns="Description", values="Quantity", aggfunc="sum", fill_value=0)
    product_pop = pivot.sum(axis=0).sort_values(ascending=False).head(top_n_products)
    selected_products = product_pop.index.tolist()
    sub = pivot[selected_products]
    sim = cosine_similarity(sub.T.values)

    plt.figure(figsize=(12, 10))
    sns.heatmap(sim, xticklabels=selected_products, yticklabels=selected_products, cmap="vlag", center=0)
    plt.title(f"Product-Product Cosine Similarity (top {top_n_products} products)")
    out = PROJECT_ROOT / "images" / "eval_product_similarity_heatmap.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    print(f"Saved similarity heatmap to {out}")
    plt.show()


def recommendation_quality_offline(df_transactions: pd.DataFrame, top_k: int = 5, sample_users: int = 1000, seed: int = 42):
    """Simple offline evaluation for item-based recommendations using leave-one-out per user.

    Procedure:
    - For a sample of users with >=2 distinct products, hold out one randomly chosen product as test.
    - Build a train pivot excluding the held-out interaction.
    - For the query product (held-out), get top_k recommendations and check if held-out product appears.
    - Compute Precision@k and Recall@k approximations across users.

    This is a basic proxy metric for recommendation ability; more advanced evaluations require timestamp-aware splits and negative sampling.
    """
    random.seed(seed)
    users = df_transactions["CustomerID"].dropna().unique()
    # Build per-user item lists
    user_items = df_transactions.groupby("CustomerID")["Description"].apply(lambda s: list(s))

    # Filter users with at least 2 items
    eligible_users = [u for u, items in user_items.items() if len(items) >= 2]
    if not eligible_users:
        print("No eligible users for offline evaluation (need users with >=2 items).")
        return

    sample = random.sample(eligible_users, min(sample_users, len(eligible_users)))

    hits = 0
    total = 0
    for u in sample:
        items = user_items[u]
        test_item = random.choice(items)
        # train interactions exclude one occurrence of test_item
        df_train = df_transactions.drop(df_transactions[(df_transactions["CustomerID"] == u) & (df_transactions["Description"] == test_item)].index[:1])

        # Build pivot and recommender
        pivot = pd.pivot_table(df_train, index="CustomerID", columns="Description", values="Quantity", aggfunc="sum", fill_value=0)
        if test_item not in pivot.columns:
            # If test item not in training catalog, skip
            continue

        # Compute similarity for test_item
        product_matrix = pivot.T.values.astype(float)
        product_names = list(pivot.columns)
        idx_map = {p: i for i, p in enumerate(product_names)}
        test_idx = idx_map[test_item]
        sims = cosine_similarity(product_matrix[test_idx:test_idx+1], product_matrix).flatten()
        sims[test_idx] = -1  # exclude self
        top_idx = np.argsort(-sims)[:top_k]
        recommended = [product_names[i] for i in top_idx]

        total += 1
        if test_item in recommended:
            hits += 1

    precision_at_k = hits / total if total else 0
    print(f"Offline recommendation evaluation (leave-one-out) — Precision@{top_k}: {precision_at_k:.4f} over {total} users")
    print(textwrap.fill("Note: This is a simple proxy evaluation. For robust assessment use timestamped train/test splits, negative sampling, and metrics like MAP@K or NDCG.", 80))
    return precision_at_k


def business_interpretation(cluster_profile: pd.DataFrame, rec_precision: float):
    """Print a human-friendly business interpretation of evaluation results."""
    print("\nBusiness Interpretation:")
    print(textwrap.fill("- Elbow and silhouette analysis help choose the number of segments: look for stable silhouette peaks and an elbow in inertia. A higher silhouette indicates clearer cluster separation.", 120))
    print(textwrap.fill("- Cluster profiling shows which segments are high-value (high Monetary and Frequency, low Recency). Focus retention/upsell on these customers.", 120))
    print(textwrap.fill("- If recommendation precision@k is low, consider richer signals (e.g., product categories, session context) or hybrid approaches combining collaborative and content-based methods.", 120))
    print(textwrap.fill(f"- Current offline Precision@k: {rec_precision:.3f}. This gives a baseline for A/B testing — aim to improve it with feature engineering and algorithm tuning.", 120))


def main():
    # Loading and simple checks
    print("Loading data for evaluation...")
    try:
        df = pd.read_csv(TRANSACTIONS_FILE)
    except UnicodeDecodeError:
        df = pd.read_csv(TRANSACTIONS_FILE, encoding="ISO-8859-1")

    rfm, rfm_clusters = load_rfm_and_clusters()

    # If RFM clusters exist, analyze cluster profiling
    prof = None
    if not rfm_clusters.empty:
        prof = cluster_profiling(rfm_clusters)
        cluster_distribution(rfm_clusters)

    # Prepare feature matrix for clustering evaluation (use RFM if available)
    if not rfm.empty:
        features = rfm[["Recency", "Frequency", "Monetary"]].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(features)
        elbow_curve(X_scaled, k_range=range(1, 11))
        silhouette_analysis(X_scaled, k_range=range(2, 11))
    else:
        print("RFM features not found — skipping elbow/silhouette analysis.")

    # Similarity matrix visualization (top products)
    visualize_similarity_matrix(df, top_n_products=40)

    # Recommendation offline evaluation
    prec = recommendation_quality_offline(df, top_k=5, sample_users=500)

    # Business interpretation
    business_interpretation(prof, prec)


if __name__ == "__main__":
    main()
