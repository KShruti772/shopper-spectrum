import streamlit as st
from pathlib import Path

# App meta
st.set_page_config(page_title="Shopper Spectrum", layout="wide")

BASE_DIR = Path(__file__).resolve().parents[1]

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css(BASE_DIR / "styles.css")


def apply_theme(theme: str):
    """Inject CSS to toggle dark/light mode using CSS variables defined in styles.css."""
    if theme == "dark":
        # Add a wrapper class on the html element via CSS variable overrides
        css = """
        <style>
        :root{ --bg: #0b1220; --card-bg: #071126; --text: #e6eef8; --muted: #9aa8bd; --accent: #6ec1ff; }
        </style>
        """
    else:
        css = """
        <style>
        :root{ --bg: #f7f7f8; --card-bg: #ffffff; --text: #0f1720; --muted: #6c6c6c; --accent: #2b8cbe; }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)


def main():
    # Sidebar navigation
    st.sidebar.title("Shopper Spectrum")

    # Theme toggle
    theme = st.sidebar.radio("Theme", ["light", "dark"], index=0)
    apply_theme(theme)

    page = st.sidebar.radio("Navigation", ["Home", "Customer Segmentation", "Product Recommendation", "Segmentation Input"])

    # Render pages
    if page == "Home":
        from .pages import home
        home.render()
    elif page == "Customer Segmentation":
        from .pages import segmentation
        segmentation.render()
    elif page == "Product Recommendation":
        from .pages import recommendation
        recommendation.render()
    elif page == "Segmentation Input":
        from .pages import segmentation_input
        segmentation_input.render()

    # Footer
    st.markdown("---")
    st.markdown("<div class='footer'>© Shopper Spectrum — E-commerce analytics demo</div>", unsafe_allow_html=True)


if __name__ == '__main__':
    main()
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Shopper Spectrum Demo")

st.title("Shopper Spectrum — Customer Segmentation & Recommendations")

DATA_PATH = os.path.join("..", "online_retail.csv")

@st.cache_data
def load_data(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df = load_data(DATA_PATH)

if df.empty:
    st.warning("Dataset not found at root. Place `online_retail.csv` in the project root.")
else:
    st.write("Dataset preview:")
    st.dataframe(df.head())
