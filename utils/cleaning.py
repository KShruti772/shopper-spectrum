"""Cleaning utilities for Shopper Spectrum e-commerce dataset.

Functions:
 - clean_retail_data: load and clean the dataset according to standard rules

The cleaning steps performed:
 1. Remove rows with missing CustomerID
 2. Remove cancelled invoices where InvoiceNo starts with 'C'
 3. Remove rows with Quantity <= 0
 4. Remove rows with UnitPrice <= 0
 5. Convert InvoiceDate to datetime
 6. Create a new column TotalPrice = Quantity * UnitPrice

This module is written to be safe for production use: it logs changes,
validates expected columns, and returns the cleaned DataFrame.
"""

from pathlib import Path
import logging
from typing import Tuple

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def _read_csv(path: Path) -> pd.DataFrame:
    """Read CSV with a safe encoding fallback."""
    try:
        df = pd.read_csv(path)
        return df
    except UnicodeDecodeError:
        logger.warning("UnicodeDecodeError reading CSV; retrying with ISO-8859-1")
        return pd.read_csv(path, encoding="ISO-8859-1")


def clean_retail_data(csv_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load and clean the e-commerce retail dataset.

    Args:
        csv_path: Path to `online_retail.csv`.

    Returns:
        tuple: (raw_df, cleaned_df)

    The function logs the number of rows removed at each step and prints
    shapes before and after cleaning so the user can audit the transformation.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found at {csv_path}")

    df = _read_csv(path)
    raw_shape = df.shape
    logger.info("Loaded data with shape: %s", raw_shape)

    # Verify expected columns exist
    expected = {"InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"}
    missing_cols = expected - set(df.columns)
    if missing_cols:
        logger.error("Missing expected columns: %s", missing_cols)
        raise ValueError(f"Dataset is missing expected columns: {missing_cols}")

    # Work on a copy to avoid side-effects
    cleaned = df.copy()

    # 1) Remove rows with missing CustomerID
    # Why: CustomerID is required for customer-level analytics (segmentation, lifetime value,
    # and personalized recommendations). Rows without a CustomerID cannot be tied to a customer,
    # so they are typically removed or handled separately.
    before = len(cleaned)
    cleaned = cleaned.dropna(subset=["CustomerID"])  # removes rows where CustomerID is NaN
    removed = before - len(cleaned)
    logger.info("Removed %d rows with missing CustomerID", removed)

    # 2) Remove cancelled invoices where InvoiceNo starts with 'C'
    # Why: Cancelled transactions (commonly denoted by 'C' prefix) represent returns/cancellations
    # and should not be treated as normal sales when computing revenue or purchase frequency.
    before = len(cleaned)
    # Ensure InvoiceNo is string for startswith checks
    cleaned["InvoiceNo"] = cleaned["InvoiceNo"].astype(str)
    cancelled_mask = cleaned["InvoiceNo"].str.startswith("C")
    cleaned = cleaned.loc[~cancelled_mask]
    removed = before - len(cleaned)
    logger.info("Removed %d cancelled invoice rows (InvoiceNo starts with 'C')", removed)

    # 3) Remove rows with Quantity <= 0
    # Why: Non-positive quantities indicate returns, corrections, or invalid data. For sales analysis
    # we normally consider only positive quantities. If you need to analyze returns, store them separately.
    before = len(cleaned)
    cleaned = cleaned[cleaned["Quantity"] > 0]
    removed = before - len(cleaned)
    logger.info("Removed %d rows with Quantity <= 0", removed)

    # 4) Remove rows with UnitPrice <= 0
    # Why: Zero or negative prices are often promotional giveaways or data errors; they distort
    # revenue calculations and per-unit metrics.
    before = len(cleaned)
    cleaned = cleaned[cleaned["UnitPrice"] > 0]
    removed = before - len(cleaned)
    logger.info("Removed %d rows with UnitPrice <= 0", removed)

    # 5) Convert InvoiceDate to datetime
    # Why: Datetime dtype is required for time-based features (recency, cohorting, seasonal analysis).
    cleaned["InvoiceDate"] = pd.to_datetime(cleaned["InvoiceDate"], errors="coerce")
    unparsable_dates = cleaned["InvoiceDate"].isna().sum()
    if unparsable_dates:
        logger.warning("Found %d unparsable InvoiceDate values; they are set to NaT", unparsable_dates)

    # 6) Create TotalPrice column
    # Why: TotalPrice = Quantity * UnitPrice is the revenue contribution per row and used
    # for monetary calculations such as total spend, average order value, and RFM.
    cleaned["TotalPrice"] = cleaned["Quantity"] * cleaned["UnitPrice"]

    # Final shapes
    final_shape = cleaned.shape
    logger.info("Shape before cleaning: %s", raw_shape)
    logger.info("Shape after cleaning: %s", final_shape)

    # Print a concise before/after summary for user visibility
    print("Dataset shape before cleaning:", raw_shape)
    print("Dataset shape after cleaning:", final_shape)

    return df, cleaned


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clean online_retail.csv for Shopper Spectrum project")
    parser.add_argument("--input", default="../online_retail.csv", help="Path to online_retail.csv")
    parser.add_argument("--output", default=None, help="Optional path to write cleaned CSV")
    args = parser.parse_args()

    try:
        raw, cleaned = clean_retail_data(args.input)
        if args.output:
            out_path = Path(args.output)
            cleaned.to_csv(out_path, index=False)
            logger.info("Cleaned data written to %s", out_path)
    except Exception as exc:
        logger.exception("An error occurred during cleaning: %s", exc)
