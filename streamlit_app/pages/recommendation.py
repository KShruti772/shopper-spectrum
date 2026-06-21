import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

from ..utils.recommender import ItemBasedRecommender

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "online_retail.csv"
SIM_PATH = PROJECT_ROOT / "data" / "processed" / "product_similarity.csv"


@st.cache_data(show_spinner=False)
def load_transactions(path: Path) -> pd.DataFrame:
    """Load cleaned transactions if available; fallback to raw CSV."""
    try:
        from utils.cleaning import clean_retail_data
        _, df = clean_retail_data(str(path))
        return df
    except Exception:
        try:
            return pd.read_csv(path)
        except UnicodeDecodeError:
            return pd.read_csv(path, encoding="ISO-8859-1")


@st.cache_data(show_spinner=False)
def load_or_compute_similarity(df: pd.DataFrame, sim_path: Path) -> pd.DataFrame:
    """Load a saved product-product similarity DataFrame or compute and save it.

    The saved format is CSV with product names as both index and columns.
    """
    sim_path.parent.mkdir(parents=True, exist_ok=True)
    if sim_path.exists():
        try:
            sim_df = pd.read_csv(sim_path, index_col=0)
            return sim_df
        except Exception:
            # corrupted file, compute anew
            pass

    # Build pivot and compute similarity
    pivot = pd.pivot_table(df, index="CustomerID", columns="Description", values="Quantity", aggfunc="sum", fill_value=0)
    product_matrix = pivot.T.values.astype(float)
    sim_array = cosine_similarity(product_matrix)
    product_names = list(pivot.columns)
    sim_df = pd.DataFrame(sim_array, index=product_names, columns=product_names)

    # Save to CSV for future fast loads
    try:
        sim_df.to_csv(sim_path)
    except Exception:
        # non-fatal if save fails (e.g., permission issues)
        pass

    return sim_df


def render():
    st.title("Product Recommendation")
    st.markdown("Find similar products using item-based collaborative filtering.")

    df = load_transactions(DATA_FILE)
    st.sidebar.markdown(f"**Dataset:** {df.shape[0]:,} transactions — {df['Description'].nunique():,} products")

    # Input controls
    product_input = st.text_input("Product name (partial or full)")
    top_n = st.selectbox("Number of recommendations", options=[3,5,7,10], index=1)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("Enter a product name or keyword and click Recommend.")
    with col2:
        recommend_btn = st.button("Recommend")

    if recommend_btn:
        if not product_input or str(product_input).strip() == "":
            st.error("Please enter a product name to search for recommendations.")
            return

        # Compute or load similarity matrix (cached)
        with st.spinner("Preparing similarity matrix..."):
            sim_df = load_or_compute_similarity(df, SIM_PATH)

        # Build recommender (fast) and compute recommendations
        recommender = ItemBasedRecommender()
        recommender.fit(df)

        try:
            recs = recommender.recommend(product_input, top_n=top_n)
        except Exception as e:
            st.error(f"Error while finding matches: {e}")
            return

        # If recommender returned popular_fallback, show info and display fallback
        if not recs.empty and "reason" in recs.columns and recs.at[0, "reason"] == "popular_fallback":
            st.info("No close product match found — showing popular products as fallback.")

        if recs.empty:
            st.warning("No recommendations available for this query.")
            return

        # Display recommendations with expanders/cards
        st.markdown("### Top recommendations")
        for i, row in recs.iterrows():
            prod = row["product"]
            sim = float(row.get("similarity", 0.0))
            conf = float(row.get("confidence", 0.0))
            pop = int(row.get("popularity", 0))

            with st.expander(f"{i+1}. {prod} — Confidence: {conf:.2%}"):
                st.markdown(f"**Similarity score:** {sim:.4f}")
                st.markdown(f"**Confidence:** {conf:.2%}")
                st.markdown(f"**Popularity (total quantity):** {pop}")
                # Example action buttons
                btn_col1, btn_col2 = st.columns([1, 2])
                if btn_col1.button(f"View {i+1}", key=f"view_{i}"):
                    st.info(f"You clicked to view product: {prod}")
                if btn_col2.button(f"Add to promo list", key=f"promo_{i}"):
                    st.success(f"{prod} added to promo list")

        st.markdown("---")
        st.markdown("Tip: Use partial keywords or product fragments; the system attempts fuzzy matching and falls back to popular items if no close match is found.")

