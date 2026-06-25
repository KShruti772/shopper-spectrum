import streamlit as st
import plotly.express as px
import pandas as pd
from pathlib import Path

from utils.helpers import log_error, show_error_message
from utils.model_loader import find_dataset_path
from utils.recommendation_engine import (
    build_product_index,
    compute_popular_products,
    load_similarity_resource,
    recommend_products,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SIMILARITY_PATH = PROJECT_ROOT / "models" / "similarity_matrix.pkl"
DATA_PATH = find_dataset_path()


def _render_header():
    st.markdown("# Product Recommendation")
    st.markdown("Get targeted product suggestions using purchase-behavior similarity.")


def _render_sidebar():
    st.sidebar.header("Recommendation Controls")
    st.sidebar.markdown("Search by product keyword. If exact matches are missing, the engine falls back to popular items.")


def _render_search_controls():
    query = st.text_input("🔍 Product name or keyword", placeholder="Example: white cotton shirt")
    top_n = st.selectbox("How many recommendations", [3, 5, 7, 10], index=1)
    submit = st.button("Recommend")
    return query, top_n, submit


def _render_popular_products(df: pd.DataFrame):
    popular = compute_popular_products(df, top_n=10)
    if popular.empty:
        st.info("No popularity metrics available.")
        return
    st.markdown("### Popular Products")
    st.dataframe(popular, use_container_width=True)
    fig = px.bar(popular, x="TotalQuantity", y="Description", orientation="h", title="Top Popular Products")
    st.plotly_chart(fig, use_container_width=True)


def _render_recommendations(recommendations: pd.DataFrame, query: str):
    if recommendations.empty:
        st.warning("No recommendations available for this query.")
        return
    st.markdown(f"### Recommendations for '{query}'")
    for idx, row in recommendations.iterrows():
        similarity = float(row.get("similarity", 0.0))
        confidence = float(row.get("confidence", 0.0))
        with st.expander(f"{idx + 1}. {row['product']} ({similarity:.2%} similarity)"):
            st.write(f"**Product:** {row['product']}")
            st.write(f"**Similarity:** {similarity:.4f}")
            st.write(f"**Confidence:** {confidence:.2%}")
            st.write(f"**Popularity:** {int(row.get('popularity', 0))}")


def _render_analytics(df: pd.DataFrame, recommendations: pd.DataFrame):
    st.markdown("### Recommendation Analytics")
    if not df.empty:
        popular = compute_popular_products(df, top_n=8)
        fig = px.pie(popular, values="TotalQuantity", names="Description", title="Product Popularity Distribution")
        st.plotly_chart(fig, use_container_width=True)
    if not recommendations.empty:
        fig = px.bar(recommendations.head(5), x="product", y="similarity", title="Recommendation Similarity Scores")
        st.plotly_chart(fig, use_container_width=True)


def render():
    _render_header()
    _render_sidebar()

    if DATA_PATH is None:
        show_error_message("Retail dataset not found.", "Place the dataset in the project root or data/ folder and restart.")
        return

    try:
        df = pd.read_csv(DATA_PATH, low_memory=False)
    except Exception as exc:
        log_error(exc, "Loading product dataset")
        show_error_message("Could not load dataset.")
        return

    query, top_n, submit = _render_search_controls()
    if not submit:
        _render_popular_products(df)
        return

    if not query or not query.strip():
        show_error_message("Please provide a product name or keyword.")
        return

    try:
        similar_matrix = load_similarity_resource(SIMILARITY_PATH)
        product_index = build_product_index(similar_matrix)
        recommendations = recommend_products(query, similar_matrix, product_index, top_n=top_n)
    except FileNotFoundError:
        st.warning("Similarity data not available. Serving fallback popular products.")
        recommendations = compute_popular_products(df, top_n=top_n).rename(columns={"Description": "product"})
    except Exception as exc:
        log_error(exc, "Generating recommendations")
        show_error_message("Recommendation generation failed.")
        return

    if recommendations.empty:
        st.warning("No recommendations found. Try a broader keyword.")
        return

    _render_recommendations(recommendations, query)
    _render_analytics(df, recommendations)

    with st.expander("How recommendations work"):
        st.write(
            "This module uses a precomputed similarity matrix to compare products from the retail catalog. "
            "If the model resource is not available, it gracefully falls back to a popular-products list."
        )
