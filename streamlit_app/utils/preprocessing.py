from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from .helpers import setup_logger
from .validators import validate_dataset

LOGGER = setup_logger(__name__)
ROOT_DIR = Path(__file__).resolve().parents[2]


def _strip_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    text_columns = [col for col in df.columns if df[col].dtype == object]
    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()
    return df


def _remove_cancelled_invoices(df: pd.DataFrame) -> pd.DataFrame:
    if "InvoiceNo" not in df.columns:
        return df
    return df[~df["InvoiceNo"].astype(str).str.upper().str.startswith("C")]


def _drop_negative_or_zero(df: pd.DataFrame, column: str) -> pd.DataFrame:
    if column not in df.columns:
        return df
    values = pd.to_numeric(df[column], errors="coerce")
    return df[values > 0]


def _convert_invoice_date(df: pd.DataFrame) -> pd.DataFrame:
    if "InvoiceDate" not in df.columns:
        return df
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    return df


def _ensure_total_price(df: pd.DataFrame) -> pd.DataFrame:
    if "TotalPrice" not in df.columns and {"Quantity", "UnitPrice"}.issubset(df.columns):
        df["TotalPrice"] = pd.to_numeric(df["Quantity"], errors="coerce") * pd.to_numeric(df["UnitPrice"], errors="coerce")
    return df


def _remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def _remove_missing_customer_id(df: pd.DataFrame) -> pd.DataFrame:
    if "CustomerID" not in df.columns:
        return df
    return df.dropna(subset=["CustomerID"]).reset_index(drop=True)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw retail data and return a consistent cleaned DataFrame."""
    if df is None or df.empty:
        LOGGER.warning("clean_data received an empty DataFrame")
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.str.strip()
    df = _strip_text_columns(df)
    df = _remove_missing_customer_id(df)
    df = _remove_cancelled_invoices(df)
    df = _drop_negative_or_zero(df, "Quantity")
    df = _drop_negative_or_zero(df, "UnitPrice")
    df = _convert_invoice_date(df)
    df = _ensure_total_price(df)
    df = _remove_duplicates(df)
    df = df.dropna(subset=["InvoiceDate", "Quantity", "UnitPrice", "TotalPrice"]).reset_index(drop=True)

    report = validate_dataset(df)
    if report["severity"] != "ok":
        LOGGER.warning("Cleaned dataset still has validation issues: %s", report["issues"])
    else:
        LOGGER.info("Data cleaning completed successfully with %s rows", len(df))

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time-based features and keep the dataset ready for analytics."""
    if df is None or df.empty:
        LOGGER.warning("engineer_features received an empty DataFrame")
        return pd.DataFrame()

    df = df.copy()
    df = _convert_invoice_date(df)
    df = _ensure_total_price(df)
    df["Year"] = df["InvoiceDate"].dt.year
    df["Month"] = df["InvoiceDate"].dt.month
    df["Day"] = df["InvoiceDate"].dt.day
    df["Hour"] = df["InvoiceDate"].dt.hour
    df["PurchaseDayName"] = df["InvoiceDate"].dt.day_name()
    df["PurchaseMonthName"] = df["InvoiceDate"].dt.month_name()

    return df


def generate_data_report(df: pd.DataFrame) -> dict:
    """Generate diagnostics and high-level dataset metrics."""
    if df is None or df.empty:
        return {
            "shape": (0, 0),
            "missing_summary": {},
            "duplicate_count": 0,
            "dtypes": {},
            "unique_customers": 0,
            "unique_products": 0,
            "revenue_summary": {},
        }

    missing_summary = df.isna().sum().to_dict()
    revenue_summary = {}
    if "TotalPrice" in df.columns:
        revenue = pd.to_numeric(df["TotalPrice"], errors="coerce")
        revenue_summary = {
            "total_revenue": float(revenue.sum()),
            "average_order_value": float(revenue.mean()),
            "max_order_value": float(revenue.max()),
            "min_order_value": float(revenue.min()),
        }

    return {
        "shape": df.shape,
        "missing_summary": missing_summary,
        "duplicate_count": int(df.duplicated().sum()),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "unique_customers": int(df["CustomerID"].nunique(dropna=True)) if "CustomerID" in df.columns else 0,
        "unique_products": int(df["Description"].nunique(dropna=True)) if "Description" in df.columns else 0,
        "revenue_summary": revenue_summary,
    }
