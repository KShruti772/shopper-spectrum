from pathlib import Path

import pandas as pd
import streamlit as st
from pandas.errors import EmptyDataError, ParserError

from .helpers import LOG_DIR, resolve_safe_path, safe_read_csv, setup_logger
from .validators import validate_dataset

LOGGER = setup_logger(__name__)
ROOT_DIR = Path(__file__).resolve().parents[2]


@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    """Load the retail CSV file safely and return a validated DataFrame."""
    safe_path = resolve_safe_path(path, base_dir=ROOT_DIR)

    if not safe_path.exists():
        LOGGER.error("CSV file not found at %s", safe_path)
        raise FileNotFoundError(f"Retail dataset missing at {safe_path}")

    if safe_path.stat().st_size == 0:
        LOGGER.error("CSV file is empty: %s", safe_path)
        raise EmptyDataError(f"Dataset file is empty: {safe_path}")

    try:
        df = safe_read_csv(safe_path, low_memory=False)
    except UnicodeDecodeError as exc:
        LOGGER.warning("Unicode error reading %s, retrying with ISO-8859-1", safe_path)
        df = pd.read_csv(safe_path, encoding="ISO-8859-1", low_memory=False)
    except ParserError as exc:
        LOGGER.exception("ParserError loading CSV: %s", safe_path)
        raise ParserError(f"Could not parse CSV file: {exc}")
    except Exception as exc:
        LOGGER.exception("Unexpected error reading CSV: %s", safe_path)
        raise ValueError(f"Unable to read dataset file: {exc}")

    if df.empty:
        LOGGER.warning("Loaded dataset is empty after reading %s", safe_path)
        raise EmptyDataError(f"Dataset contains no rows after reading: {safe_path}")

    df.columns = df.columns.str.strip()

    report = validate_dataset(df)
    if report["severity"] == "fail":
        LOGGER.error("Validation failed for dataset: %s", report["issues"])
    elif report["issues"]:
        LOGGER.warning("Validation reported issues: %s", report["issues"])
    else:
        LOGGER.info("Dataset loaded and validated successfully from %s", safe_path)

    return df
