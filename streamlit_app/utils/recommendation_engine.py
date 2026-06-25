from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from .helpers import resolve_safe_path, safe_load_model, setup_logger

LOGGER = setup_logger(__name__)
ROOT_DIR = Path(__file__).resolve().parents[2]


def _normalize_product_name(name: str) -> str:
    return str(name).strip().lower()


def build_similarity_index(products: List[str]) -> Dict[str, List[str]]:
    normalized = [ _normalize_product_name(name) for name in products ]
    return {normalized[i]: products[i] for i in range(len(products))}


def find_best_match(product: str, index: Dict[str, str]) -> Tuple[str, str]:
    normalized = _normalize_product_name(product)
    if normalized in index:
        return normalized, index[normalized]
    partial_matches = [key for key in index.keys() if normalized in key]
    if partial_matches:
        return partial_matches[0], index[partial_matches[0]]
    return normalized, ""


def compute_popular_products(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if "Description" not in df.columns or "Quantity" not in df.columns:
        return pd.DataFrame()
    popular = (
        df.groupby("Description", as_index=False)["Quantity"]
        .sum()
        .sort_values("Quantity", ascending=False)
        .head(top_n)
        .rename(columns={"Quantity": "TotalQuantity"})
    )
    return popular


def recommend_products(
    query: str,
    similarity_matrix: pd.DataFrame,
    product_index: Dict[str, str],
    top_n: int = 5,
    fallback: List[str] = None,
) -> pd.DataFrame:
    if not query or str(query).strip() == "":
        raise ValueError("Please provide a search query.")

    _, product_name = find_best_match(query, product_index)
    if not product_name or product_name not in similarity_matrix.index:
        if fallback:
            return pd.DataFrame({"product": fallback, "reason": ["popular_fallback"] * len(fallback)})
        raise ValueError("Product not found in similarity matrix.")

    similarities = similarity_matrix.loc[product_name].copy()
    similarities = similarities.drop(index=product_name, errors="ignore")
    recommendations = similarities.sort_values(ascending=False).head(top_n)
    results = pd.DataFrame(
        {
            "product": recommendations.index,
            "similarity": recommendations.values,
        }
    )
    results["confidence"] = (results["similarity"] - results["similarity"].min()) / (
        results["similarity"].max() - results["similarity"].min() + 1e-9
    )
    results["similarity_pct"] = (results["similarity"] * 100).round(1)
    return results


def load_similarity_resource(path: Path) -> pd.DataFrame:
    safe_path = resolve_safe_path(path, base_dir=ROOT_DIR)
    matrix = safe_load_model(safe_path, base_dir=ROOT_DIR)
    if isinstance(matrix, pd.DataFrame):
        return matrix
    if isinstance(matrix, np.ndarray):
        return pd.DataFrame(matrix)
    raise ValueError("Similarity matrix must be a DataFrame or numpy array.")


def build_product_index(similarity_matrix: pd.DataFrame) -> Dict[str, str]:
    products = list(similarity_matrix.index.astype(str))
    return build_similarity_index(products)
