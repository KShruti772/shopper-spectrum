"""
05_item_based_cf.py

Item-based collaborative filtering recommendations for Shopper Spectrum.

This script:
- Builds a Customer x Product pivot table (by `Description`) using purchase quantities
- Computes cosine similarity between product vectors
- Creates a similarity DataFrame (products x products)
- Provides `recommend_similar_products(product_name, top_n=5)` to return top-N similar products with scores
- Handles product-not-found errors and suggests close matches

Requires: pandas, numpy, scikit-learn

Run as script:
    python notebooks/05_item_based_cf.py

"""

from pathlib import Path
import textwrap
import difflib
from typing import List, Tuple, Optional

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "online_retail.csv"


def load_data(path: Path) -> pd.DataFrame:
    """Load cleaned transactions if available; otherwise load CSV with safe encoding.

    Returns a DataFrame with expected columns including `Description`, `CustomerID`, and `Quantity`.
    """
    try:
        from utils.cleaning import clean_retail_data
        _, df = clean_retail_data(str(path))
        print("Loaded cleaned dataset via utils.cleaning.clean_retail_data")
        return df
    except Exception:
        try:
            df = pd.read_csv(path)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="ISO-8859-1")
        return df


def build_customer_product_matrix(df: pd.DataFrame, product_col: str = "Description", customer_col: str = "CustomerID", quantity_col: str = "Quantity") -> pd.DataFrame:
    """Create a sparse-friendly customer-product pivot table.

    - Normalizes product names (stripped) but preserves original names in the pivot columns.
    - Aggregates quantities per customer-product pair.
    - Fills missing with 0.
    """
    df = df.copy()
    # Normalize product text for search purposes (we keep original description in columns)
    df[product_col] = df[product_col].astype(str).str.strip()

    pivot = pd.pivot_table(df, index=customer_col, columns=product_col, values=quantity_col, aggfunc="sum", fill_value=0)
    return pivot


class ItemBasedRecommender:
    """Item-based collaborative filtering recommender with optimized similarity computation.

    Usage:
        rec = ItemBasedRecommender()
        rec.fit(pivot)
        rec.recommend('product name')
    """

    def __init__(self, pivot: Optional[pd.DataFrame] = None):
        self.pivot = pivot
        self.product_names: List[str] = []
        self.product_to_index = {}
        self.product_matrix = None  # shape (n_products, n_customers)
        self.norms = None
        self.popularity = None  # total quantity per product

    def fit(self, pivot: pd.DataFrame):
        """Fit recommender using a customer x product pivot (customers rows, products columns)."""
        self.pivot = pivot
        # product_matrix shape: (n_products, n_customers)
        product_matrix = pivot.T.values.astype(float)
        self.product_matrix = product_matrix
        self.product_names = list(pivot.columns)
        self.product_to_index = {p: i for i, p in enumerate(self.product_names)}

        # Precompute L2 norms for fast cosine computations
        self.norms = np.linalg.norm(product_matrix, axis=1)
        # Avoid zeros in norms by setting tiny value
        self.norms[self.norms == 0] = 1e-9

        # Popularity measure: total quantity sold per product
        self.popularity = product_matrix.sum(axis=1)

    def _find_matches(self, query: str, partial: bool = True) -> List[str]:
        """Return matching product names for a query (case-insensitive)."""
        q = query.strip().lower()
        # build lowercase mapping once
        lower_map = {p.lower(): p for p in self.product_names}

        # Exact match first
        if q in lower_map:
            return [lower_map[q]]

        # Partial substring matches
        matches = []
        if partial:
            for plower, porig in lower_map.items():
                if q in plower:
                    matches.append(porig)

        # If still no matches, use difflib close matches on original names (case-insensitive)
        if not matches:
            candidates = list(lower_map.keys())
            close = difflib.get_close_matches(q, candidates, n=5, cutoff=0.6)
            matches = [lower_map[c] for c in close]

        return matches

    def _compute_similarity_for_index(self, idx: int) -> np.ndarray:
        """Compute cosine similarity between product at idx and all products (vectorized).

        Returns a 1D array of similarity scores.
        """
        v = self.product_matrix[idx]  # shape (n_customers,)
        v_norm = self.norms[idx]
        # Dot product with all product vectors
        dots = self.product_matrix.dot(v)
        sims = dots / (self.norms * v_norm)
        # Numerical issues: clip to [-1, 1]
        sims = np.clip(sims, -1.0, 1.0)
        return sims

    def recommend(self, product_query: str, top_n: int = 5, partial: bool = True, fallback_top_n: int = 5) -> pd.DataFrame:
        """Return top-N recommended products for a product_query.

        Behavior:
        - Performs case-insensitive exact match, then partial substring matching, then fuzzy matching.
        - If multiple matches are found, picks the most popular match.
        - If no match is found, returns the top popular products as fallback.
        - Ranks recommendations by a combined score (similarity * popularity_weight).
        """
        matches = self._find_matches(product_query, partial=partial)

        if not matches:
            # Fallback: return popular products
            top_idx = np.argsort(-self.popularity)[:fallback_top_n]
            recs = [self.product_names[i] for i in top_idx]
            scores = (self.popularity[top_idx] / (self.popularity.max() + 1e-9)).tolist()
            df = pd.DataFrame({"product": recs, "score": scores})
            df["reason"] = "popular_fallback"
            return df

        # If multiple product matches, pick the one with highest popularity
        if len(matches) > 1:
            match_pops = [(m, self.popularity[self.product_to_index[m]]) for m in matches]
            matches = [sorted(match_pops, key=lambda x: -x[1])[0][0]]

        target = matches[0]
        target_idx = self.product_to_index[target]

        sims = self._compute_similarity_for_index(target_idx)

        # Build DataFrame of candidates
        df = pd.DataFrame({"product": self.product_names, "similarity": sims, "popularity": self.popularity})

        # Remove the target product
        df = df[df["product"] != target]

        # Compute confidence score: similarity scaled by popularity (normalized)
        pop_norm = df["popularity"] / (df["popularity"].max() + 1e-9)
        df["confidence"] = df["similarity"] * pop_norm

        # Remove duplicates (unlikely since product names are unique columns) but keep safe
        df = df.drop_duplicates(subset=["product"])

        # Better ranking: sort by confidence first, then similarity, then popularity
        df_sorted = df.sort_values(["confidence", "similarity", "popularity"], ascending=[False, False, False])

        # Keep top_n and only positive similarity
        df_sorted = df_sorted[df_sorted["similarity"] > 0]
        top = df_sorted.head(top_n).reset_index(drop=True)

        # Add metadata
        top.insert(0, "query_product", target)
        top["query_input"] = product_query

        # Reorder columns
        top = top[["query_input", "query_product", "product", "similarity", "confidence", "popularity"]]
        return top


def pretty_display_recommendations(df: pd.DataFrame):
    """Print recommendations in readable format including confidence scores."""
    if df.empty:
        print("No recommendations available.")
        return
    query = df.at[0, "query_input"]
    target = df.at[0, "query_product"]
    print(f"\nTop {len(df)} recommendations for query '{query}' (matched product: '{target}'):")
    for i, row in df.iterrows():
        print(f"{i+1}. {row['product']}  (similarity: {row['similarity']:.4f}, confidence: {row['confidence']:.4f}, popularity: {int(row['popularity'])})")


def explain_collaborative_filtering():
    """Print a simple explanation of item-based collaborative filtering."""
    explanation = (
        "Item-based collaborative filtering recommends products by finding items that have similar purchase patterns across customers. "
        "If many customers buy product A and product B, we consider them similar and recommend B to buyers of A. "
        "This implementation uses cosine similarity between product purchase vectors and incorporates product popularity to provide confidence scores."
    )
    print(textwrap.fill(explanation, 100))


def main():
    df = load_data(DATA_FILE)
    print("Loaded data shape:", df.shape)

    pivot = build_customer_product_matrix(df)
    print("Customer-Product matrix shape:", pivot.shape)

    # Fit recommender
    rec = ItemBasedRecommender()
    rec.fit(pivot)

    # Choose example product (most purchased)
    product_example = pivot.sum(axis=0).sort_values(ascending=False).index[0]
    print(f"Using example product: {product_example}")

    # Example queries demonstrating improved search
    queries = [product_example, product_example.lower(), product_example.split()[0]]

    for q in queries:
        print(f"\nQuery: {q}")
        try:
            top = rec.recommend(q, top_n=5)
            pretty_display_recommendations(top)
        except Exception as e:
            print("Error while recommending:", str(e))

    # Demonstrate fallback
    print("\nDemonstrating fallback for nonexistent product:")
    fall = rec.recommend("this product does not exist xyz", top_n=5)
    pretty_display_recommendations(fall)

    print("\nExplanation of collaborative filtering:")
    explain_collaborative_filtering()


if __name__ == "__main__":
    main()
