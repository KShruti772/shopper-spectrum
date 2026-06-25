from typing import Any, Dict, List

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
}


def _check_required_columns(df: pd.DataFrame) -> List[str]:
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    return [f"Missing required column: {col}" for col in missing]


def _check_null_values(df: pd.DataFrame) -> List[str]:
    null_summary = df.isna().sum()
    issues = []
    for column, null_count in null_summary.items():
        if null_count > 0:
            issues.append(f"Column '{column}' contains {null_count} null values")
    return issues


def _check_invalid_types(df: pd.DataFrame) -> List[str]:
    issues = []
    if "Quantity" in df.columns:
        q_invalid = pd.to_numeric(df["Quantity"], errors="coerce").isna().sum()
        if q_invalid:
            issues.append(f"Quantity contains {q_invalid} invalid numeric values")
    if "UnitPrice" in df.columns:
        p_invalid = pd.to_numeric(df["UnitPrice"], errors="coerce").isna().sum()
        if p_invalid:
            issues.append(f"UnitPrice contains {p_invalid} invalid numeric values")
    if "InvoiceDate" in df.columns:
        date_invalid = pd.to_datetime(df["InvoiceDate"], errors="coerce").isna().sum()
        if date_invalid:
            issues.append(f"InvoiceDate contains {date_invalid} invalid or unparsable dates")
    return issues


def _check_duplicate_rows(df: pd.DataFrame) -> List[str]:
    duplicate_count = int(df.duplicated().sum())
    return [f"Dataset contains {duplicate_count} duplicate rows"] if duplicate_count else []


def _check_invalid_dates(df: pd.DataFrame) -> List[str]:
    issues = []
    if "InvoiceDate" in df.columns:
        parsed = pd.to_datetime(df["InvoiceDate"], errors="coerce")
        invalid_dates = parsed.isna().sum()
        if invalid_dates:
            issues.append(f"InvoiceDate has {invalid_dates} invalid timestamps")
    return issues


def _check_negative_quantities(df: pd.DataFrame) -> List[str]:
    if "Quantity" not in df.columns:
        return []
    quantities = pd.to_numeric(df["Quantity"], errors="coerce")
    negative = int((quantities <= 0).sum())
    return [f"Quantity has {negative} rows with non-positive values"] if negative else []


def _check_invalid_prices(df: pd.DataFrame) -> List[str]:
    if "UnitPrice" not in df.columns:
        return []
    prices = pd.to_numeric(df["UnitPrice"], errors="coerce")
    invalid = int((prices <= 0).sum())
    return [f"UnitPrice has {invalid} rows with non-positive values"] if invalid else []


def _check_missing_customer_ids(df: pd.DataFrame) -> List[str]:
    if "CustomerID" not in df.columns:
        return []
    missing = int(df["CustomerID"].isna().sum())
    return [f"CustomerID has {missing} missing values"] if missing else []


def validate_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """Return a validation report describing dataset issues and warnings."""
    issues = []
    issues.extend(_check_required_columns(df))
    if not issues:
        issues.extend(_check_null_values(df))
        issues.extend(_check_invalid_types(df))
        issues.extend(_check_duplicate_rows(df))
        issues.extend(_check_invalid_dates(df))
        issues.extend(_check_negative_quantities(df))
        issues.extend(_check_invalid_prices(df))
        issues.extend(_check_missing_customer_ids(df))

    severity = "ok"
    if issues:
        severity = "fail" if any("Missing required column" in issue for issue in issues) else "warning"

    return {
        "status": "validation_report",
        "severity": severity,
        "issues": issues,
        "summary": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "duplicate_rows": int(df.duplicated().sum()),
            "missing_values": int(df.isna().sum().sum()),
        },
    }
