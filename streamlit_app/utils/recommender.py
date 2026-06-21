"""Lightweight item-based recommender for Streamlit app.

This is a trimmed, dependency-light version of the ItemBasedRecommender
designed to work inside the Streamlit app. It builds a customer-product
pivot from the provided DataFrame and computes similarity on demand.
"""
from typing import List, Optional
import difflib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class ItemBasedRecommender:
    def __init__(self):
        self.pivot = None
        self.product_names = []
        self.product_to_index = {}
        self.product_matrix = None
        self.norms = None
        self.popularity = None

    def fit(self, df: pd.DataFrame, product_col: str = "Description", customer_col: str = "CustomerID", quantity_col: str = "Quantity"):
        df = df.copy()
        df[product_col] = df[product_col].astype(str).str.strip()
        pivot = pd.pivot_table(df, index=customer_col, columns=product_col, values=quantity_col, aggfunc="sum", fill_value=0)
        self.pivot = pivot
        self.product_names = list(pivot.columns)
        self.product_to_index = {p: i for i, p in enumerate(self.product_names)}
        self.product_matrix = pivot.T.values.astype(float)
        self.norms = np.linalg.norm(self.product_matrix, axis=1)
        self.norms[self.norms == 0] = 1e-9
        self.popularity = self.product_matrix.sum(axis=1)

    def _find_matches(self, query: str, partial: bool = True) -> List[str]:
        q = query.strip().lower()
        lower_map = {p.lower(): p for p in self.product_names}
        if q in lower_map:
            return [lower_map[q]]
        matches = []
        if partial:
            for plower, porig in lower_map.items():
                if q in plower:
                    matches.append(porig)
        if not matches:
            candidates = list(lower_map.keys())
            close = difflib.get_close_matches(q, candidates, n=5, cutoff=0.6)
            matches = [lower_map[c] for c in close]
        return matches

    def _compute_similarity_for_index(self, idx: int) -> np.ndarray:
        v = self.product_matrix[idx]
        v_norm = self.norms[idx]
        dots = self.product_matrix.dot(v)
        sims = dots / (self.norms * v_norm)
        sims = np.clip(sims, -1.0, 1.0)
        return sims

    def recommend(self, product_query: str, top_n: int = 5, partial: bool = True, fallback_top_n: int = 5):
        matches = self._find_matches(product_query, partial=partial)
        if not matches:
            top_idx = np.argsort(-self.popularity)[:fallback_top_n]
            recs = [self.product_names[i] for i in top_idx]
            scores = (self.popularity[top_idx] / (self.popularity.max() + 1e-9)).tolist()
            df = pd.DataFrame({"product": recs, "score": scores})
            df["reason"] = "popular_fallback"
            return df
        if len(matches) > 1:
            match_pops = [(m, self.popularity[self.product_to_index[m]]) for m in matches]
            matches = [sorted(match_pops, key=lambda x: -x[1])[0][0]]
        target = matches[0]
        target_idx = self.product_to_index[target]
        sims = self._compute_similarity_for_index(target_idx)
        df = pd.DataFrame({"product": self.product_names, "similarity": sims, "popularity": self.popularity})
        df = df[df["product"] != target]
        pop_norm = df["popularity"] / (df["popularity"].max() + 1e-9)
        df["confidence"] = df["similarity"] * pop_norm
        df = df.drop_duplicates(subset=["product"])
        df_sorted = df.sort_values(["confidence", "similarity", "popularity"], ascending=[False, False, False])
        df_sorted = df_sorted[df_sorted["similarity"] > 0]
        top = df_sorted.head(top_n).reset_index(drop=True)
        top.insert(0, "query_product", target)
        top["query_input"] = product_query
        top = top[["query_input", "query_product", "product", "similarity", "confidence", "popularity"]]
        return top
