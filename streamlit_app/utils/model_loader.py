import pickle
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import streamlit as st

from .helpers import resolve_safe_path, safe_load_data, setup_logger, safe_load_model

LOGGER = setup_logger(__name__)
ROOT_DIR = Path(__file__).resolve().parents[2]


def _resolve_model_path(path: Path) -> Path:
    return resolve_safe_path(path, base_dir=ROOT_DIR)


@st.cache_resource(show_spinner=False)
def load_pickle_resource(path: Path) -> Any:
    safe_path = _resolve_model_path(path)
    if not safe_path.exists():
        LOGGER.error("Model file not found: %s", safe_path)
        raise FileNotFoundError(f"Model file not found: {safe_path}")

    try:
        model = safe_load_model(safe_path, base_dir=ROOT_DIR)
        LOGGER.info("Loaded model resource from %s", safe_path)
        return model
    except Exception as exc:
        LOGGER.exception("Failed to load pickle resource: %s", safe_path)
        raise


@st.cache_resource(show_spinner=False)
def load_similarity_matrix(path: Path) -> pd.DataFrame:
    model = load_pickle_resource(path)
    if isinstance(model, pd.DataFrame):
        return model
    if isinstance(model, (list, tuple)):
        return pd.DataFrame(model)
    if isinstance(model, dict):
        return pd.DataFrame(model)

    raise ValueError(f"Loaded similarity matrix is not a DataFrame or matrix-like object: {type(model)}")


@st.cache_data(show_spinner=False)
def load_data_resource(path: Path) -> pd.DataFrame:
    df = safe_load_data(_resolve_model_path(path), low_memory=False)
    LOGGER.info("Loaded dataset resource from %s", path)
    return df


def find_dataset_path() -> Optional[Path]:
    candidates = [
        ROOT_DIR / "data" / "OnlineRetail.csv",
        ROOT_DIR / "data" / "online_retail.csv",
        ROOT_DIR / "OnlineRetail.csv",
        ROOT_DIR / "online_retail.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None
