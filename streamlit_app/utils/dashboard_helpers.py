from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

EXPECTED_COLUMNS = {
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
}


def _empty_chart(title: str) -> go.Figure:
    """Return an empty placeholder chart."""
    fig = go.Figure()
    fig.add_annotation(
        text=f"{title}: No data available",
        showarrow=False,
        font=dict(size=16, color="rgba(155, 155, 155, 0.8)"),
    )
    fig.update_layout(
        title=title,
        xaxis={"visible": False},
        yaxis={"visible": False},
        template="plotly_dark",
        height=300,
    )
    return fig


def safe_line_chart(df: pd.DataFrame, chart_type: str, description: str) -> bool:
    """Validate data for line chart rendering."""
    if df.empty:
        return False
    if "InvoiceDate" not in df.columns or "TotalPrice" not in df.columns:
        return False
    return True


def safe_bar_chart(df: pd.DataFrame, chart_type: str, description: str) -> bool:
    """Validate data for bar chart rendering."""
    if df.empty:
        return False
    if chart_type == "top_products" and ("Description" not in df.columns or "Quantity" not in df.columns):
        return False
    return True


def safe_histogram(df: pd.DataFrame, chart_type: str, description: str) -> bool:
    """Validate data for histogram rendering."""
    if df.empty:
        return False
    if "TotalPrice" not in df.columns:
        return False
    return True


def _safe_read_csv(path: Path) -> pd.DataFrame:
    """Read CSV with an encoding fallback for common dataset encodings."""
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="ISO-8859-1")


def _ensure_total_price(df: pd.DataFrame) -> pd.DataFrame:
    if "TotalPrice" not in df.columns and {"Quantity", "UnitPrice"}.issubset(df.columns):
        df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
    return df


def _clean_core_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "InvoiceNo" in df.columns:
        df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
        df = df[~df["InvoiceNo"].str.upper().str.startswith("C")]
    if "Quantity" in df.columns:
        df = df[pd.to_numeric(df["Quantity"], errors="coerce") > 0]
    if "UnitPrice" in df.columns:
        df = df[pd.to_numeric(df["UnitPrice"], errors="coerce") > 0]
    if "CustomerID" in df.columns:
        df = df.dropna(subset=["CustomerID"])
    return df


@st.cache_data(show_spinner=False)
def load_transaction_data(path: Path) -> pd.DataFrame:
    """Load the retail dataset safely and return cleaned transactions."""
    if not path.exists():
        raise FileNotFoundError(f"Data file not found at {path}")

    df = _safe_read_csv(path)
    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df = _ensure_total_price(df)
    df = _clean_core_data(df)
    return df


@st.cache_data(show_spinner=False)
def load_rfm_segments(path: Path) -> pd.DataFrame:
    """Load saved segment labels if available, otherwise return an empty DataFrame."""
    if not path.exists():
        return pd.DataFrame()
    return _safe_read_csv(path)


def format_currency(value: float, currency_symbol: str = "₹") -> str:
    try:
        return f"{currency_symbol}{value:,.2f}"
    except Exception:
        return str(value)


def format_number(value: int) -> str:
    try:
        return f"{value:,}"
    except Exception:
        return str(value)


def summarize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.isna()
        .sum()
        .rename("missing")
        .reset_index()
        .rename(columns={"index": "column"})
    )
    summary["missing_pct"] = (summary["missing"] / len(df) * 100).round(2)
    return summary


def compute_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Compute KPI metrics with safe fallbacks."""
    try:
        total_revenue = float(df["TotalPrice"].sum()) if "TotalPrice" in df.columns else 0.0
        total_customers = int(df["CustomerID"].nunique(dropna=True)) if "CustomerID" in df.columns else 0
        total_transactions = int(len(df))
        total_products = int(df["Description"].nunique()) if "Description" in df.columns else 0
        return {
            "total_revenue": total_revenue,
            "total_customers": total_customers,
            "total_transactions": total_transactions,
            "total_products": total_products,
        }
    except Exception:
        return {
            "total_revenue": 0.0,
            "total_customers": 0,
            "total_transactions": 0,
            "total_products": 0,
        }


def build_monthly_sales_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "InvoiceDate" not in df.columns or "TotalPrice" not in df.columns:
        return _empty_chart("Monthly Revenue Trend")
    
    try:
        df_clean = df.dropna(subset=["InvoiceDate", "TotalPrice"]).copy()
        if df_clean.empty:
            return _empty_chart("Monthly Revenue Trend")
        
        monthly = (
            df_clean
            .assign(YearMonth=lambda d: pd.to_datetime(d["InvoiceDate"]).dt.to_period("M").dt.to_timestamp())
            .groupby("YearMonth", as_index=False)["TotalPrice"]
            .sum()
        )
        
        if monthly.empty:
            return _empty_chart("Monthly Revenue Trend")
        
        fig = px.line(
            monthly,
            x="YearMonth",
            y="TotalPrice",
            markers=True,
            title="Monthly Revenue Trend",
            labels={"YearMonth": "Month", "TotalPrice": "Revenue"},
        )
        fig.update_layout(template="plotly_dark", hovermode="x unified")
        fig.update_traces(line=dict(width=3, color="#5BC0EB"))
        return fig
    except Exception:
        return _empty_chart("Monthly Revenue Trend")


def build_country_sales_chart(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    country = (
        df.groupby("Country", as_index=False)["TotalPrice"]
        .sum()
        .sort_values("TotalPrice", ascending=False)
        .head(top_n)
    )
    fig = px.bar(
        country,
        x="TotalPrice",
        y="Country",
        orientation="h",
        title="Top Countries by Revenue",
        labels={"TotalPrice": "Revenue", "Country": "Country"},
    )
    fig.update_layout(template="plotly_dark", yaxis=dict(autorange="reversed"), margin=dict(l=0, r=0, t=40, b=20))
    fig.update_traces(marker_color="#64D2FF", hovertemplate="%{y}: ₹%{x:,.0f}<extra></extra>")
    return fig


def build_top_products_chart(df: pd.DataFrame, top_n: int = 12) -> go.Figure:
    if df.empty or "Description" not in df.columns or "Quantity" not in df.columns:
        return _empty_chart("Top Selling Products")
    
    try:
        products = (
            df.groupby("Description", as_index=False)["Quantity"]
            .sum()
            .sort_values("Quantity", ascending=False)
            .head(top_n)
        )
        
        if products.empty:
            return _empty_chart("Top Selling Products")
        
        fig = px.bar(
            products,
            x="Quantity",
            y="Description",
            orientation="h",
            title="Top Selling Products",
            labels={"Quantity": "Units Sold", "Description": "Product"},
        )
        fig.update_layout(template="plotly_dark", yaxis=dict(autorange="reversed"), margin=dict(l=0, r=0, t=40, b=20))
        fig.update_traces(marker_color="#8ED081", hovertemplate="%{y}: %{x:,}<extra></extra>")
        return fig
    except Exception:
        return _empty_chart("Top Selling Products")


def build_revenue_distribution_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "TotalPrice" not in df.columns:
        return _empty_chart("Revenue Distribution")
    
    try:
        valid_prices = df[df["TotalPrice"] > 0].copy()
        if valid_prices.empty:
            return _empty_chart("Revenue Distribution")
        
        fig = px.histogram(
            valid_prices,
            x="TotalPrice",
            nbins=40,
            title="Revenue Distribution",
            labels={"TotalPrice": "Order Value"},
        )
        fig.update_layout(template="plotly_dark", bargap=0.05, margin=dict(l=0, r=0, t=40, b=20))
        fig.update_traces(marker_color="#FFA500", hovertemplate="₹%{x:.2f} - %{y} orders<extra></extra>")
        return fig
    except Exception:
        return _empty_chart("Revenue Distribution")


def build_daily_transactions_chart(df: pd.DataFrame) -> go.Figure:
    daily = (
        df.dropna(subset=["InvoiceDate"])
        .assign(InvoiceDate=lambda d: d["InvoiceDate"].dt.date)
        .groupby("InvoiceDate", as_index=False)["InvoiceNo"]
        .nunique()
        .rename(columns={"InvoiceNo": "Transactions"})
    )
    fig = px.area(
        daily,
        x="InvoiceDate",
        y="Transactions",
        title="Daily Transaction Trend",
        labels={"InvoiceDate": "Date", "Transactions": "Unique Orders"},
    )
    fig.update_layout(template="plotly_dark", hovermode="x unified")
    fig.update_traces(line_color="#E78AC3", fillcolor="rgba(231, 138, 195, 0.25)")
    return fig


def build_segment_distribution_chart(segment_counts: pd.Series) -> go.Figure:
    fig = px.pie(
        names=segment_counts.index,
        values=segment_counts.values,
        hole=0.44,
        title="Customer Segment Breakdown",
    )
    fig.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=40, b=20))
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def get_customer_insights(df: pd.DataFrame) -> Dict[str, str]:
    insights = {
        "highest_spending_country": "N/A",
        "top_customer": "N/A",
        "busiest_month": "N/A",
        "average_order_value": "N/A",
    }

    if df.empty:
        return insights

    if "Country" in df.columns:
        country = (
            df.groupby("Country", as_index=False)["TotalPrice"]
            .sum()
            .sort_values("TotalPrice", ascending=False)
            .head(1)
        )
        if not country.empty:
            insights["highest_spending_country"] = f"{country.iloc[0]['Country']} (₹{country.iloc[0]['TotalPrice']:,.0f})"

    if "CustomerID" in df.columns:
        customer = (
            df.groupby("CustomerID", as_index=False)["TotalPrice"]
            .sum()
            .sort_values("TotalPrice", ascending=False)
            .head(1)
        )
        if not customer.empty:
            insights["top_customer"] = f"ID {customer.iloc[0]['CustomerID']} (₹{customer.iloc[0]['TotalPrice']:,.0f})"

    if "InvoiceDate" in df.columns:
        monthly = (
            df.dropna(subset=["InvoiceDate"])
            .assign(YearMonth=lambda d: d["InvoiceDate"].dt.to_period("M").dt.to_timestamp())
            .groupby("YearMonth", as_index=False)["TotalPrice"]
            .sum()
        )
        if not monthly.empty:
            month_label = monthly.iloc[monthly["TotalPrice"].idxmax()]["YearMonth"].strftime("%b %Y")
            insights["busiest_month"] = month_label

    if "TotalPrice" in df.columns and "InvoiceNo" in df.columns:
        orders = df["InvoiceNo"].nunique()
        if orders:
            insights["average_order_value"] = f"₹{(df['TotalPrice'].sum() / orders):,.2f}"

    return insights


def get_top_products(df: pd.DataFrame, top_n: int = 6) -> pd.DataFrame:
    if df.empty or "Description" not in df.columns or "Quantity" not in df.columns:
        return pd.DataFrame()
    products = (
        df.groupby("Description", as_index=False)
        .agg({"Quantity": "sum", "TotalPrice": "sum"})
        .sort_values("Quantity", ascending=False)
        .head(top_n)
    )
    products = products.rename(columns={"Description": "Product", "Quantity": "Units Sold", "TotalPrice": "Revenue"})
    return products


def generate_customer_segments(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "CustomerID" not in df.columns or "InvoiceDate" not in df.columns:
        return pd.DataFrame()

    summary = (
        df.groupby("CustomerID", as_index=False)
        .agg(
            last_purchase=("InvoiceDate", "max"),
            frequency=("InvoiceNo", "nunique"),
            monetary=("TotalPrice", "sum"),
        )
    )
    latest_date = summary["last_purchase"].max()
    summary["recency"] = (latest_date - summary["last_purchase"]).dt.days
    quantiles = summary[["recency", "frequency", "monetary"]].quantile([0.33, 0.66])
    q1 = quantiles.loc[0.33]
    q2 = quantiles.loc[0.66]

    conditions = [
        (summary["recency"] <= q1["recency"]) & (summary["frequency"] >= q2["frequency"]) & (summary["monetary"] >= q2["monetary"]),
        (summary["recency"] <= q2["recency"]) & (summary["frequency"] >= q1["frequency"]),
        (summary["recency"] > q2["recency"]) & (summary["frequency"] <= q1["frequency"]),
    ]
    choices = ["High-Value Customers", "Regular Customers", "Occasional Customers"]
    summary["segment"] = np.select(conditions, choices, default="At-Risk Customers")
    return summary


def build_recommendation_preview(df: pd.DataFrame, top_n: int = 6) -> Dict[str, pd.DataFrame]:
    result = {
        "popular_products": pd.DataFrame(),
        "recommendations": pd.DataFrame(),
        "summary": "No recommendation preview available.",
    }

    if df.empty or "Description" not in df.columns or "Quantity" not in df.columns:
        return result

    result["popular_products"] = get_top_products(df, top_n=top_n)
    if result["popular_products"].empty:
        return result

    seed_product = result["popular_products"].iloc[0]["Product"]
    try:
        from utils.recommender import ItemBasedRecommender

        recommender = ItemBasedRecommender()
        recommender.fit(df)
        result["recommendations"] = recommender.recommend(seed_product, top_n=top_n)
        result["summary"] = (
            f"Sample recommendations generated for the top product: {seed_product}. "
            "This preview uses item similarity and popularity to suggest items.")
    except Exception:
        result["recommendations"] = pd.DataFrame()
        result["summary"] = "Recommendation preview is not available because the collaborative model could not be built from the current dataset."

    return result
