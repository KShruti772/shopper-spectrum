"""
02_rfm_analysis.py

RFM analysis for Shopper Spectrum (e-commerce transactions).

Tasks implemented:
1. Create Recency, Frequency, Monetary features
2. Build final RFM dataframe
3. Explain meanings of R, F, M
4. Show top customers by RFM score and monetary value
5. Visualize RFM distributions (histograms and boxplots)
6. Detect outliers using the IQR method

Usage:
    python notebooks/02_rfm_analysis.py

Requires: pandas, numpy, matplotlib, seaborn
"""

from pathlib import Path
import textwrap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (12, 6)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "online_retail.csv"
OUTPUT_DIR = PROJECT_ROOT / "images"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data(path: Path) -> pd.DataFrame:
    """Load dataset and ensure basic preprocessing for RFM.

    This function will attempt to use the cleaned dataset if available (TotalPrice,
    InvoiceDate parsed). Otherwise it applies minimal preprocessing so the RFM
    calculations can proceed.
    """
    try:
        from utils.cleaning import clean_retail_data

        _, df = clean_retail_data(str(path))
        print("Loaded cleaned data via utils.cleaning.clean_retail_data")
        return df
    except Exception:
        # Fallback load
        try:
            df = pd.read_csv(path)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="ISO-8859-1")

        # Minimal preprocessing
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
        if "TotalPrice" not in df.columns:
            df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
        return df


def compute_rfm(df: pd.DataFrame, snapshot_date: pd.Timestamp = None) -> pd.DataFrame:
    """Compute Recency, Frequency, and Monetary for each customer.

    Args:
        df: transactions DataFrame with columns `CustomerID`, `InvoiceDate`, `InvoiceNo`, `TotalPrice`.
        snapshot_date: date to compute recency from; defaults to max(InvoiceDate) + 1 day.

    Returns:
        rfm: DataFrame indexed by `CustomerID` with `Recency`, `Frequency`, `Monetary`.
    """
    # Validate input
    required = {"CustomerID", "InvoiceDate", "InvoiceNo", "TotalPrice"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns for RFM computation: {missing}")

    # Use a snapshot date that is one day after the last transaction date by default
    if snapshot_date is None:
        snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    # Group by customer
    grouped = df.groupby("CustomerID")

    # Recency: number of days since the customer's last purchase
    recency = grouped["InvoiceDate"].max().apply(lambda x: (snapshot_date - x).days).rename("Recency")

    # Frequency: number of unique invoices (transactions) for the customer
    frequency = grouped["InvoiceNo"].nunique().rename("Frequency")

    # Monetary: total spend by the customer
    monetary = grouped["TotalPrice"].sum().rename("Monetary")

    # Combine into a single DataFrame
    rfm = pd.concat([recency, frequency, monetary], axis=1).reset_index()

    # Ensure numeric types
    rfm["Recency"] = rfm["Recency"].astype(int)
    rfm["Frequency"] = rfm["Frequency"].astype(int)
    rfm["Monetary"] = rfm["Monetary"].astype(float)

    return rfm


def explain_rfm():
    """Print beginner-friendly explanations for R, F, and M."""
    print("\nRFM metric meanings:")
    print(textwrap.fill("- Recency: How recently did the customer make a purchase? Lower recency (fewer days) means more recent activity.", 80))
    print(textwrap.fill("- Frequency: How often does the customer purchase? Higher frequency indicates more repeat behavior.", 80))
    print(textwrap.fill("- Monetary: How much money has the customer spent? Higher monetary value indicates higher customer value.", 80))


def score_rfm(rfm: pd.DataFrame, recency_bins=5, frequency_bins=5, monetary_bins=5) -> pd.DataFrame:
    """Add R, F, M scores (1-5) and a combined RFM score.

    We use quantile-based binning (`qcut`) so scores are distributed across customers.
    For Recency, smaller recency is better, therefore we invert the recency score.
    """
    rfm_scored = rfm.copy()

    # Recency score: lower recency -> higher score
    rfm_scored["R_score"] = pd.qcut(rfm_scored["Recency"], recency_bins, labels=False, duplicates="drop")
    # Invert so that 5 = most recent
    rfm_scored["R_score"] = (rfm_scored["R_score"].max() - rfm_scored["R_score"]).astype(int) + 1

    # Frequency score: higher is better
    rfm_scored["F_score"] = pd.qcut(rfm_scored["Frequency"].rank(method="first"), frequency_bins, labels=False, duplicates="drop").astype(int) + 1

    # Monetary score: higher is better
    rfm_scored["M_score"] = pd.qcut(rfm_scored["Monetary"].rank(method="first"), monetary_bins, labels=False, duplicates="drop").astype(int) + 1

    # Combined RFM score as string and numeric
    rfm_scored["RFM_score"] = rfm_scored["R_score"].map(str) + rfm_scored["F_score"].map(str) + rfm_scored["M_score"].map(str)
    rfm_scored["RFM_score_num"] = rfm_scored[["R_score", "F_score", "M_score"]].sum(axis=1)

    return rfm_scored


def top_customers(rfm_scored: pd.DataFrame, top_n=10):
    """Display top customers by monetary and by RFM score."""
    print(f"\nTop {top_n} customers by Monetary value:")
    top_money = rfm_scored.sort_values("Monetary", ascending=False).head(top_n)
    print(top_money[["CustomerID", "Monetary", "Frequency", "Recency"]].to_string(index=False))

    print(f"\nTop {top_n} customers by RFM combined score (numeric):")
    top_rfm = rfm_scored.sort_values(["RFM_score_num", "Monetary"], ascending=[False, False]).head(top_n)
    print(top_rfm[["CustomerID", "RFM_score", "RFM_score_num", "Monetary"]].to_string(index=False))


def plot_rfm_distributions(rfm: pd.DataFrame):
    """Plot histograms and boxplots for Recency, Frequency, Monetary."""
    metrics = ["Recency", "Frequency", "Monetary"]
    for metric in metrics:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Histogram
        sns.histplot(rfm[metric], bins=50, kde=True, ax=axes[0], color="#66c2a5")
        axes[0].set_title(f"Distribution of {metric}")
        axes[0].set_xlabel(metric)

        # Boxplot (log scale for Monetary to reduce skew if needed)
        if metric == "Monetary":
            sns.boxplot(x=np.log1p(rfm[metric]), ax=axes[1], color="#8da0cb")
            axes[1].set_xlabel(f"log1p({metric})")
            axes[1].set_title(f"Boxplot of log-transformed {metric}")
        else:
            sns.boxplot(x=rfm[metric], ax=axes[1], color="#8da0cb")
            axes[1].set_title(f"Boxplot of {metric}")

        plt.tight_layout()
        out_file = OUTPUT_DIR / f"rfm_{metric.lower()}_dist.png"
        fig.savefig(out_file, dpi=150)
        print(f"Saved {out_file}")
        plt.show()

        # Short interpretation
        if metric == "Recency":
            print(textwrap.fill("Interpretation: Lower recency values mean customers bought more recently. A right-skewed distribution indicates many inactive customers.", 80))
        elif metric == "Frequency":
            print(textwrap.fill("Interpretation: Frequency shows how often customers purchase. Heavy right tails indicate a few highly active customers.", 80))
        else:
            print(textwrap.fill("Interpretation: Monetary shows total spend; it is usually skewed with a small set of high-value customers.", 80))


def detect_outliers_iqr(rfm: pd.DataFrame, factor=1.5) -> pd.DataFrame:
    """Detect outliers using the IQR method for each RFM metric.

    Returns the input DataFrame with additional boolean columns: `<metric>_outlier`.
    """
    rfm_out = rfm.copy()
    for metric in ["Recency", "Frequency", "Monetary"]:
        q1 = rfm_out[metric].quantile(0.25)
        q3 = rfm_out[metric].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr

        # For Recency, unusually high recency (very inactive) can be considered an outlier on the high side.
        rfm_out[f"{metric}_outlier"] = ~rfm_out[metric].between(lower, upper)

        n_out = rfm_out[f"{metric}_outlier"].sum()
        print(f"Detected {n_out} outliers in {metric} using IQR method (factor={factor})")

    # Show some example outliers for Monetary and Frequency
    print("\nExample high Monetary outliers:")
    print(rfm_out[rfm_out["Monetary_outlier"]].sort_values("Monetary", ascending=False).head(10).to_string(index=False))

    return rfm_out


def main():
    df = load_data(DATA_FILE)
    print("Data loaded. Preparing RFM features...")

    rfm = compute_rfm(df)
    print("RFM head:")
    print(rfm.head().to_string(index=False))

    explain_rfm()

    rfm_scored = score_rfm(rfm)
    print("\nSample scored RFM:")
    print(rfm_scored.head().to_string(index=False))

    top_customers(rfm_scored, top_n=10)

    plot_rfm_distributions(rfm)

    rfm_outliers = detect_outliers_iqr(rfm)

    # Optionally save RFM results for downstream use
    out_path = PROJECT_ROOT / "data" / "processed"
    out_path.mkdir(parents=True, exist_ok=True)
    rfm_scored.to_csv(out_path / "rfm_customers.csv", index=False)
    print(f"Saved RFM scored customers to {out_path / 'rfm_customers.csv'}")


if __name__ == "__main__":
    main()
