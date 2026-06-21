"""
01_eda_shopper_spectrum.py

Comprehensive Exploratory Data Analysis for Shopper Spectrum (online_retail.csv)

Visualizations included:
1. Transaction volume by country
2. Top-selling products
3. Monthly sales trends
4. Daily sales trends
5. Top customers by spending
6. Distribution of Quantity
7. Distribution of UnitPrice
8. Distribution of TotalPrice
9. Correlation heatmap

Each plotting function prints a short interpretation after the chart.

Run as script from project root:
    python notebooks/01_eda_shopper_spectrum.py

Requires: pandas, numpy, matplotlib, seaborn, plotly
"""

import os
from pathlib import Path
import textwrap

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

sns.set(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (12, 6)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "online_retail.csv"
OUTPUT_DIR = PROJECT_ROOT / "images"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_and_prepare(path: Path) -> pd.DataFrame:
    """Load dataset, ensure datetimes and TotalPrice column exist.

    Tries to use the project's cleaning utility if available, otherwise performs
    minimal safe preparation for EDA.
    """
    try:
        # Prefer the robust cleaning function if available in utils
        from utils.cleaning import clean_retail_data

        _, df = clean_retail_data(str(path))
        print("Loaded cleaned data using `utils.cleaning.clean_retail_data`")
        return df
    except Exception:
        # Fallback: load, parse dates, create TotalPrice
        print("Fallback load: reading CSV and performing minimal preprocessing")
        try:
            df = pd.read_csv(path)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="ISO-8859-1")

        # Ensure required columns exist
        required = {"InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns for EDA: {missing}")

        # Parse InvoiceDate
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

        # Create TotalPrice if missing
        if "TotalPrice" not in df.columns:
            df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

        return df


def save_fig(fig, name: str):
    out = OUTPUT_DIR / f"{name}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"Saved figure to {out}")


def transaction_volume_by_country(df: pd.DataFrame, top_n=15):
    """Plot transaction volume (count) by country (top N)."""
    counts = df["Country"].value_counts().nlargest(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=counts.values, y=counts.index, palette="viridis", ax=ax)
    ax.set_title("Transaction Volume by Country (Top %d)" % top_n)
    ax.set_xlabel("Number of Transactions")
    ax.set_ylabel("Country")
    save_fig(fig, "transactions_by_country")

    # Plotly interactive version
    fig_px = px.bar(x=counts.values, y=counts.index, orientation="h", labels={"x":"Number of Transactions","y":"Country"}, title=f"Transaction Volume by Country (Top {top_n})")
    fig_px.update_traces(marker_color=px.colors.sequential.Viridis)
    fig_px.show()

    print(textwrap.fill("Interpretation: This chart shows which countries generate the most transaction records. High counts often indicate where the business has the most customers or most activity; you should compare this to revenue (TotalPrice) to understand market value vs volume.", 80))


def top_selling_products(df: pd.DataFrame, top_n=20):
    """Show top-selling products by quantity and by revenue."""
    prod_qty = df.groupby(["StockCode", "Description"]) ["Quantity"].sum().reset_index()
    prod_qty = prod_qty.sort_values("Quantity", ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x="Quantity", y="Description", data=prod_qty, palette="magma", ax=ax)
    ax.set_title(f"Top {top_n} Products by Quantity Sold")
    ax.set_xlabel("Total Quantity Sold")
    ax.set_ylabel("")
    save_fig(fig, "top_products_by_quantity")
    plt.show()

    # Top by revenue
    prod_rev = df.groupby(["StockCode", "Description"])["TotalPrice"].sum().reset_index()
    prod_rev = prod_rev.sort_values("TotalPrice", ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x="TotalPrice", y="Description", data=prod_rev, palette="cubehelix", ax=ax)
    ax.set_title(f"Top {top_n} Products by Revenue")
    ax.set_xlabel("Total Revenue")
    ax.set_ylabel("")
    save_fig(fig, "top_products_by_revenue")
    plt.show()

    print(textwrap.fill("Interpretation: The first chart surfaces the products with the largest units sold, useful for inventory and replenishment. The second chart shows which products drive the most revenue — these may be high-price items or frequently-bundled SKUs. Differences between the two highlight high-margin vs high-volume SKUs.", 80))


def monthly_sales_trend(df: pd.DataFrame):
    """Plot monthly sales (TotalPrice) trend."""
    df = df.dropna(subset=["InvoiceDate"]).copy()
    df["YearMonth"] = df["InvoiceDate"].dt.to_period("M")
    monthly = df.groupby("YearMonth")["TotalPrice"].sum().reset_index()
    monthly["YearMonth"] = monthly["YearMonth"].dt.to_timestamp()

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x="YearMonth", y="TotalPrice", data=monthly, marker="o", color="#2b8cbe", ax=ax)
    ax.set_title("Monthly Sales Trend (Total Revenue)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Revenue")
    save_fig(fig, "monthly_sales_trend")
    plt.show()

    fig_px = px.line(monthly, x="YearMonth", y="TotalPrice", title="Monthly Sales Trend (Total Revenue)")
    fig_px.update_traces(line=dict(color="#2b8cbe"))
    fig_px.show()

    print(textwrap.fill("Interpretation: The monthly sales trend shows seasonality and growth/decline patterns. Look for peaks (promotions, holidays) and troughs (off-season). This helps plan inventory and marketing timing.", 80))


def daily_sales_trend(df: pd.DataFrame):
    """Plot daily sales (TotalPrice) and a rolling average to smooth noise."""
    df = df.dropna(subset=["InvoiceDate"]).copy()
    daily = df.groupby(df["InvoiceDate"].dt.date)["TotalPrice"].sum().reset_index()
    daily["InvoiceDate"] = pd.to_datetime(daily["InvoiceDate"])  # convert back to datetime
    daily["7d_ma"] = daily["TotalPrice"].rolling(window=7, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(daily["InvoiceDate"], daily["TotalPrice"], color="#a1d99b", alpha=0.6, label="Daily")
    ax.plot(daily["InvoiceDate"], daily["7d_ma"], color="#31a354", linewidth=2, label="7-day MA")
    ax.set_title("Daily Sales Trend with 7-day Moving Average")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Revenue")
    ax.legend()
    save_fig(fig, "daily_sales_trend")
    plt.show()

    print(textwrap.fill("Interpretation: Daily totals are noisy; the 7-day moving average highlights underlying trends and helps identify real shifts in demand versus single-day spikes.", 80))


def top_customers_by_spending(df: pd.DataFrame, top_n=10):
    """Show top customers by total spending (TotalPrice)."""
    cust = df.groupby("CustomerID")["TotalPrice"].sum().sort_values(ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=cust.values, y=cust.index.astype(str), palette="Blues_d", ax=ax)
    ax.set_title(f"Top {top_n} Customers by Total Spend")
    ax.set_xlabel("Total Spend")
    ax.set_ylabel("CustomerID")
    save_fig(fig, "top_customers_spend")
    plt.show()

    print(textwrap.fill("Interpretation: Top customers represent the highest lifetime value in the dataset. Consider prioritizing retention and personalized offers for these customers. Analyze frequency and recency for deeper insights.", 80))


def distributions(df: pd.DataFrame):
    """Plot distributions for Quantity, UnitPrice, and TotalPrice with log scales where appropriate."""
    # Quantity distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df["Quantity"].clip(lower=0), bins=50, kde=False, color="#fdae6b", ax=ax)
    ax.set_title("Distribution of Quantity")
    ax.set_xlabel("Quantity")
    save_fig(fig, "distribution_quantity")
    plt.show()
    print(textwrap.fill("Interpretation: Quantity distribution helps find typical order sizes and outliers. Long right tails often indicate occasional bulk purchases.", 80))

    # UnitPrice distribution (use log scale to show long tail)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df["UnitPrice"].clip(lower=0.0001), bins=60, log_scale=(True, False), color="#9ecae1", ax=ax)
    ax.set_title("Distribution of UnitPrice (log x-scale)")
    ax.set_xlabel("UnitPrice (log scale)")
    save_fig(fig, "distribution_unitprice")
    plt.show()
    print(textwrap.fill("Interpretation: UnitPrice often has a long right tail (a few expensive items). Use log scale to inspect the bulk of products and identify high-priced outliers.", 80))

    # TotalPrice distribution (log scale recommended)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df["TotalPrice"].clip(lower=0.0001), bins=60, log_scale=(True, False), color="#bcbddc", ax=ax)
    ax.set_title("Distribution of TotalPrice (log x-scale)")
    ax.set_xlabel("TotalPrice (log scale)")
    save_fig(fig, "distribution_totalprice")
    plt.show()
    print(textwrap.fill("Interpretation: TotalPrice distribution combines price and quantity; log scale reveals the core distribution and separates a small number of very large transactions.", 80))


def correlation_heatmap(df: pd.DataFrame):
    """Show correlation heatmap for numeric features."""
    numeric = df.select_dtypes(include=[np.number]).copy()
    corr = numeric.corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Heatmap (numeric features)")
    save_fig(fig, "correlation_heatmap")
    plt.show()

    print(textwrap.fill("Interpretation: Correlation helps identify linear relationships between numeric variables (e.g., Quantity and TotalPrice). Use this as a guide for feature selection and to detect multicollinearity.", 80))


def main():
    df = load_and_prepare(DATA_FILE)

    print("Dataset snapshot:")
    print(df.shape)
    print(df.head(3).to_string(index=False))

    transaction_volume_by_country(df)
    top_selling_products(df)
    monthly_sales_trend(df)
    daily_sales_trend(df)
    top_customers_by_spending(df)
    distributions(df)
    correlation_heatmap(df)


if __name__ == "__main__":
    main()
