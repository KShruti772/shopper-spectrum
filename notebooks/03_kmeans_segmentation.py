"""
03_kmeans_segmentation.py

KMeans-based customer segmentation using RFM features.

Steps:
1. Standardize RFM features using StandardScaler
2. Use Elbow Method to inspect inertia for range of k
3. Use Silhouette Score to evaluate cluster quality and suggest k
4. Train final KMeans model and assign cluster labels
5. Show cluster-wise RFM averages
6. Create intuitive segment labels (High-Value, Regular, Occasional, At-Risk)
7. Visualize clusters in 2D (PCA) and interactive 3D (Plotly)
8. Explain business meaning of each cluster

Usage:
    python notebooks/03_kmeans_segmentation.py

Requires: scikit-learn, pandas, numpy, matplotlib, seaborn, plotly
"""

from pathlib import Path
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

sns.set(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (12, 6)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RFM_FILE = PROJECT_ROOT / "data" / "processed" / "rfm_customers.csv"
OUTPUT_DIR = PROJECT_ROOT / "images"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_rfm(path: Path) -> pd.DataFrame:
    """Load RFM scored data if available; otherwise compute RFM from raw transactions.

    Expected columns: CustomerID, Recency, Frequency, Monetary
    """
    if path.exists():
        df = pd.read_csv(path)
        print(f"Loaded RFM data from {path}")
        return df

    # Fallback: compute RFM using utils.cleaning
    try:
        from utils.cleaning import clean_retail_data
        raw, cleaned = clean_retail_data(str(PROJECT_ROOT / "online_retail.csv"))
        df = cleaned
        snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)
        grouped = df.groupby("CustomerID")
        recency = grouped["InvoiceDate"].max().apply(lambda x: (snapshot_date - x).days).rename("Recency")
        frequency = grouped["InvoiceNo"].nunique().rename("Frequency")
        monetary = grouped["TotalPrice"].sum().rename("Monetary")
        rfm = pd.concat([recency, frequency, monetary], axis=1).reset_index()
        rfm.to_csv(path, index=False)
        print(f"Computed and saved RFM data to {path}")
        return rfm
    except Exception as exc:
        raise RuntimeError("RFM file not found and fallback computation failed: " + str(exc))


def standardize_features(rfm: pd.DataFrame):
    """Standardize Recency, Frequency, Monetary and return scaler + numpy array."""
    features = ["Recency", "Frequency", "Monetary"]
    X = rfm[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return scaler, X_scaled


def elbow_and_silhouette(X_scaled, k_range=range(2, 11)):
    """Compute inertia and silhouette scores for a range of k values.

    Returns results dict and shows Elbow and Silhouette plots.
    """
    inertias = []
    silhouettes = []
    ks = list(k_range)
    for k in ks:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        # silhouette_score requires at least 2 clusters and less than n samples
        sil = silhouette_score(X_scaled, labels) if 1 < k < len(X_scaled) else np.nan
        silhouettes.append(sil)

    # Plot inertia (Elbow)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ks, inertias, marker="o")
    ax.set_xlabel("Number of clusters k")
    ax.set_ylabel("Inertia (sum of squared distances)")
    ax.set_title("Elbow Method: Inertia by k")
    out = OUTPUT_DIR / "elbow_inertia.png"
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    plt.show()

    # Plot silhouette
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ks, silhouettes, marker="o", color="#2b8cbe")
    ax.set_xlabel("Number of clusters k")
    ax.set_ylabel("Silhouette Score (higher = better)")
    ax.set_title("Silhouette Score by k")
    out = OUTPUT_DIR / "silhouette_scores.png"
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    plt.show()

    results = {"k": ks, "inertia": inertias, "silhouette": silhouettes}
    return results


def choose_k_by_silhouette(results):
    """Choose k with the highest silhouette score (excluding nan)."""
    ks = results["k"]
    sils = np.array(results["silhouette"])
    valid = ~np.isnan(sils)
    if valid.sum() == 0:
        return ks[0]
    best_idx = np.nanargmax(sils)
    return ks[best_idx]


def train_kmeans(X_scaled, n_clusters):
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    return km, labels


def cluster_summary(rfm: pd.DataFrame, labels: np.ndarray):
    rfm_copy = rfm.copy()
    rfm_copy["cluster"] = labels
    summary = rfm_copy.groupby("cluster")[ ["Recency", "Frequency", "Monetary"] ].mean()
    counts = rfm_copy["cluster"].value_counts().sort_index()
    summary["count"] = counts
    print("\nCluster-wise RFM averages and counts:")
    print(summary.round(2).to_string())
    return rfm_copy, summary


def map_clusters_to_segments(summary: pd.DataFrame):
    """Map numeric clusters to intuitive segment labels.

    Approach: create a composite score per cluster that rewards high Monetary and Frequency and penalizes Recency.
    Then rank clusters by the composite and map top->High-Value, next->Regular, next->Occasional, bottom->At-Risk.
    If there are more than 4 clusters, groups are assigned by quantiles of the composite score.
    """
    s = summary.copy()
    # compute z-scores within clusters for each metric
    s_stats = s[["Recency", "Frequency", "Monetary"]]
    z_mon = (s_stats["Monetary"] - s_stats["Monetary"].mean()) / s_stats["Monetary"].std()
    z_freq = (s_stats["Frequency"] - s_stats["Frequency"].mean()) / s_stats["Frequency"].std()
    z_rec = (s_stats["Recency"] - s_stats["Recency"].mean()) / s_stats["Recency"].std()

    composite = z_mon + z_freq - z_rec
    s["composite"] = composite

    # rank clusters by composite
    s = s.sort_values("composite", ascending=False)
    clusters_sorted = s.index.tolist()

    n_clusters = len(clusters_sorted)
    # Define target labels
    labels_target = ["High-Value", "Regular", "Occasional", "At-Risk"]
    # If more clusters than labels, assign by quartile
    if n_clusters <= 4:
        mapping = {cluster: labels_target[i] for i, cluster in enumerate(clusters_sorted)}
    else:
        # Split into 4 roughly equal groups by rank
        grouping = np.array_split(clusters_sorted, 4)
        mapping = {}
        for i, group in enumerate(grouping):
            for c in group:
                mapping[int(c)] = labels_target[i]

    print("\nCluster to segment mapping:")
    for c, seg in mapping.items():
        print(f"Cluster {c}: {seg}")

    return mapping


def add_cluster_segment_labels(rfm_labeled: pd.DataFrame, mapping: dict):
    rfm_labeled = rfm_labeled.copy()
    rfm_labeled["segment"] = rfm_labeled["cluster"].map(mapping)
    return rfm_labeled


def plot_2d_clusters(X_scaled, labels, rfm_indexed):
    """Reduce to 2D with PCA and plot clusters."""
    pca = PCA(n_components=2, random_state=42)
    comps = pca.fit_transform(X_scaled)

    df_plot = pd.DataFrame(comps, columns=["PC1", "PC2"])
    df_plot["cluster"] = labels

    fig, ax = plt.subplots(figsize=(10, 7))
    palette = sns.color_palette("tab10", np.unique(labels).size)
    sns.scatterplot(x="PC1", y="PC2", hue="cluster", data=df_plot, palette=palette, s=60, ax=ax)
    ax.set_title("Customer Segments (2D PCA)")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    out = OUTPUT_DIR / "clusters_2d_pca.png"
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    plt.show()


def plot_3d_clusters(X_scaled, labels):
    """3D interactive scatter using PCA components and Plotly."""
    pca = PCA(n_components=3, random_state=42)
    comps3 = pca.fit_transform(X_scaled)
    df3 = pd.DataFrame(comps3, columns=["PC1", "PC2", "PC3"])
    df3["cluster"] = labels.astype(str)

    fig = px.scatter_3d(df3, x="PC1", y="PC2", z="PC3", color="cluster", title="3D PCA Customer Segments", width=900, height=700)
    fig.update_traces(marker=dict(size=4))
    fig.show()


def explain_clusters(mapping: dict, summary: pd.DataFrame):
    """Print business-oriented descriptions for each mapped segment."""
    print("\nBusiness meaning for each segment:")
    for cluster, seg in mapping.items():
        stats = summary.loc[cluster]
        rec = stats["Recency"]
        freq = stats["Frequency"]
        mon = stats["Monetary"]
        desc = f"Cluster {cluster} ({seg}): Avg Recency={rec:.1f} days, Frequency={freq:.1f}, Monetary={mon:.2f}."
        if seg == "High-Value":
            extra = "These customers buy frequently, spend the most, and purchased recently — priority for retention and VIP programs."
        elif seg == "Regular":
            extra = "Steady customers with regular purchases; good candidates for upsell and loyalty incentives."
        elif seg == "Occasional":
            extra = "Lower frequency and moderate spend — target with reactivation campaigns and occasional promotions."
        else:
            extra = "At-risk customers: low spend and infrequent / long-ago purchases — target with win-back campaigns or analyze churn reasons."

        print(textwrap.fill(desc + " " + extra, 120))


def main(k: int = None):
    rfm = load_rfm(RFM_FILE)
    print("RFM sample:")
    print(rfm.head().to_string(index=False))

    # 1) Standardize
    scaler, X_scaled = standardize_features(rfm)

    # 2-3) Elbow and silhouette
    results = elbow_and_silhouette(X_scaled, k_range=range(2, 11))
    suggested_k = choose_k_by_silhouette(results)
    print(f"Suggested k by silhouette: {suggested_k}")

    # Allow user override
    if k is None:
        k_final = suggested_k
    else:
        k_final = k

    # 4) Train KMeans
    km, labels = train_kmeans(X_scaled, n_clusters=k_final)

    # 5) Assign labels and show cluster-wise averages
    rfm_labeled, summary = cluster_summary(rfm, labels)

    # 6) Map to segments
    mapping = map_clusters_to_segments(summary)
    rfm_segmented = add_cluster_segment_labels(rfm_labeled, mapping)

    # Show top customers per segment
    print("\nTop customers per segment (by Monetary):")
    for seg in rfm_segmented["segment"].unique():
        print(f"\nSegment: {seg}")
        top = rfm_segmented[rfm_segmented["segment"] == seg].sort_values("Monetary", ascending=False).head(5)
        print(top[["CustomerID", "Recency", "Frequency", "Monetary"]].to_string(index=False))

    # 8) Visualize clusters
    plot_2d_clusters(X_scaled, labels, rfm_segmented)
    plot_3d_clusters(X_scaled, labels)

    # 9) Explain business meaning
    explain_clusters(mapping, summary)

    # Save labeled customers
    out_csv = PROJECT_ROOT / "data" / "processed" / "rfm_clusters.csv"
    rfm_segmented.to_csv(out_csv, index=False)
    print(f"Saved clustered RFM to {out_csv}")


if __name__ == "__main__":
    main()
