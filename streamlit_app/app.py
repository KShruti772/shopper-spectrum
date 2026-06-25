"""
Shopper Spectrum: Production-Grade Customer Segmentation & Recommendation Dashboard

A premium SaaS-style analytics platform built with Streamlit. This app demonstrates
customer segmentation using RFM analysis + KMeans clustering and item-based
collaborative filtering recommendations.

Author: Vighnesh
Version: 2.0.0 (Production-Ready)
Last Updated: 2025
"""

import importlib
import importlib.util
import logging
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import streamlit as st

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Add streamlit_app directory to Python path for imports
sys.path.insert(0, str(BASE_DIR))
LOGS_DIR = PROJECT_ROOT / "logs"
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"

APP_VERSION = "2.0.0"
APP_NAME = "Shopper Spectrum"
STYLES_PATH = BASE_DIR / "styles" / "styles.css"

PAGES = [
    {"label": "🏠 Home", "key": "home", "description": "Overview, dataset metrics, and sales insights."},
    {"label": "📊 Analytics", "key": "analytics", "description": "Revenue, product, and customer performance analytics."},
    {"label": "👥 Customer Segmentation", "key": "segmentation", "description": "Predict customer segments with RFM and KMeans."},
    {"label": "🛍️ Product Recommendation", "key": "recommendation", "description": "Item similarity recommendations for catalog products."},
    {"label": "💡 ML Insights", "key": "insights", "description": "Actionable recommendations and operational guidance."},
]
PAGE_MAP = {page["label"]: page["key"] for page in PAGES}

# ============================================================================
# STREAMLIT PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title=f"{APP_NAME} Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/yourusername/shopper-spectrum",
        "Report a bug": "https://github.com/yourusername/shopper-spectrum/issues",
        "About": f"{APP_NAME} v{APP_VERSION} — Production-Ready E-Commerce Analytics"
    }
)

# ============================================================================
# SETUP & UTILITIES
# ============================================================================

def setup_logging() -> logging.Logger:
    """Setup application logging."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(APP_NAME)
    if not logger.handlers:
        handler = logging.FileHandler(LOGS_DIR / "app.log")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


LOGGER = setup_logging()


def load_local_css(path: Path) -> None:
    """Load local CSS file safely."""
    try:
        if not path.exists():
            LOGGER.warning(f"CSS file not found: {path}")
            return
        css = path.read_text(encoding="utf8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        LOGGER.debug(f"Loaded CSS from {path}")
    except Exception as exc:
        LOGGER.error(f"Failed to load CSS: {exc}")


def inject_global_css() -> None:
    """Hide Streamlit default UI elements and support custom navigation."""
    st.markdown(
        """
        <style>
            #MainMenu {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            header {visibility: hidden !important;}
            .stSidebar [data-testid="stSidebarNav"] {display: none !important;}
            .css-1q8dd3e {display: none !important;}
            .css-18e3th9 {visibility: hidden !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_theme(theme: str = "dark") -> None:
    """Inject CSS theme variables."""
    if theme == "dark":
        css = """
        <style>
        :root {
            --bg: #071023;
            --surface: #0d172f;
            --surface-soft: #111f40;
            --text: #eef2fc;
            --muted: #9ab0cc;
            --accent: #5fd0ff;
            --accent-strong: #3da8ff;
        }
        </style>
        """
    else:
        css = """
        <style>
        :root {
            --bg: #f4f7fb;
            --surface: #ffffff;
            --surface-soft: #f2f6fb;
            --text: #192734;
            --muted: #6b7b8c;
            --accent: #3578e5;
            --accent-strong: #2353b7;
        }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)


def safe_import(module_path: str) -> Optional[object]:
    """Import a module safely."""
    try:
        return importlib.import_module(module_path)
    except ImportError as exc:
        LOGGER.error(f"Failed to import {module_path}: {exc}")
        return None
    except Exception as exc:
        LOGGER.error(f"Unexpected error importing {module_path}: {exc}")
        return None


# ============================================================================
# HEALTH CHECK SYSTEM
# ============================================================================

@st.cache_data(show_spinner=False)
def check_app_health() -> Dict[str, Dict[str, bool]]:
    """
    Comprehensive health check for app dependencies.
    
    Returns:
        dict: Health status of all critical components
    """
    health = {
        "files": {},
        "modules": {},
        "models": {},
        "data": {}
    }

    # Check critical files
    critical_files = {
        "CSS": BASE_DIR / "styles" / "styles.css",
        "Config": PROJECT_ROOT / ".streamlit" / "config.toml",
    }
    
    for name, file_path in critical_files.items():
        health["files"][name] = file_path.exists()
        if not health["files"][name]:
            LOGGER.warning(f"Missing critical file: {name} ({file_path})")

    # Check critical modules
    critical_modules = {
        "pandas": "pandas",
        "numpy": "numpy",
        "sklearn": "sklearn",
        "streamlit": "streamlit",
        "plotly": "plotly",
    }
    
    for name, module_name in critical_modules.items():
        try:
            __import__(module_name)
            health["modules"][name] = True
        except ImportError:
            health["modules"][name] = False
            LOGGER.error(f"Missing module: {name}")

    # Check model files
    model_files = {
        "KMeans Scaler": MODELS_DIR / "kmeans_scaler.pkl",
        "KMeans Model": MODELS_DIR / "kmeans_model.pkl",
        "Similarity Matrix": MODELS_DIR / "similarity_matrix.pkl",
    }
    
    for name, model_path in model_files.items():
        health["models"][name] = model_path.exists()
        if not health["models"][name]:
            LOGGER.warning(f"Missing model file: {name} ({model_path})")

    # Check data files
    data_candidates = [
        DATA_DIR / "online_retail.csv",
        DATA_DIR / "OnlineRetail.csv",
        PROJECT_ROOT / "online_retail.csv",
    ]
    
    data_exists = any(f.exists() for f in data_candidates)
    health["data"]["dataset"] = data_exists
    if not data_exists:
        LOGGER.warning("Primary dataset not found in expected locations")

    return health


def display_health_check() -> bool:
    """
    Display health check status in sidebar.
    
    Returns:
        bool: True if all critical components are healthy
    """
    health = check_app_health()
    
    all_healthy = (
        all(health["files"].values()) and
        all(health["modules"].values()) and
        health["data"]["dataset"]
    )

    with st.sidebar:
        if all_healthy:
            st.success("✅ App Status: Operational", icon="✅")
        else:
            st.warning("⚠️ App Status: Check Issues Below", icon="⚠️")
            
            with st.expander("📋 System Diagnostics"):
                # Files status
                if not all(health["files"].values()):
                    st.warning("**Missing Files:**")
                    for name, status in health["files"].items():
                        icon = "✓" if status else "✗"
                        st.text(f"  {icon} {name}")
                
                # Modules status
                if not all(health["modules"].values()):
                    st.error("**Missing Modules:**")
                    for name, status in health["modules"].items():
                        icon = "✓" if status else "✗"
                        st.text(f"  {icon} {name}")
                
                # Models status
                if not all(health["models"].values()):
                    st.info("**Missing Models:**")
                    for name, status in health["models"].items():
                        icon = "✓" if status else "✗"
                        st.text(f"  {icon} {name}")
                
                # Data status
                if not health["data"]["dataset"]:
                    st.error("**Dataset Issue:** Primary dataset not found")
    
    return all_healthy


# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

def render_sidebar() -> str:
    """Render polished sidebar navigation and metadata."""
    with st.sidebar:
        st.markdown(
            "<div class='sidebar-panel'>"
            "  <div class='sidebar-brand'>"
            "    <div class='sidebar-badge'>🛒</div>"
            "    <div>"
            "      <p class='sidebar-title'>Shopper Spectrum</p>"
            "      <p class='sidebar-subtitle'>Customer segmentation and product recommendation analytics.</p>"
            "    </div>"
            "  </div>"
            "  <p class='sidebar-description'>A modern analytics dashboard built for portfolio-grade e-commerce intelligence.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='nav-divider'></div>", unsafe_allow_html=True)

        selected_label = st.radio(
            "",
            [page["label"] for page in PAGES],
            index=0,
            label_visibility="collapsed",
            key="page_navigation",
        )

        st.markdown("<div class='nav-hint'>Select a page to explore business insights and models.</div>", unsafe_allow_html=True)

        st.markdown("<div class='nav-divider'></div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='sidebar-card'>"
            "  <h4>Appearance</h4>"
            "  <p class='sidebar-note'>Dark mode is recommended for dashboard analytics.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        if st.button("🔄 Refresh dashboard", key="refresh_button"):
            st.experimental_rerun()

        st.markdown(
            "<div class='sidebar-card'>"
            f"  <h4>Version</h4>"
            f"  <p class='sidebar-note'>{APP_NAME} v{APP_VERSION}</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='sidebar-card'>"
            "  <h4>Developer</h4>"
            "  <p class='sidebar-note'>Vighnesh — Data Analyst & ML Engineer for portfolio and production demos.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    return PAGE_MAP[selected_label]


# ============================================================================
# PAGE LOADER
# ============================================================================

def load_page(page_key: str) -> Optional[object]:
    """Dynamically import a page module from the pages directory."""
    page_file = BASE_DIR / "pages" / f"{page_key}.py"
    if not page_file.exists():
        LOGGER.error("Page file missing: %s", page_file)
        return None

    try:
        spec = importlib.util.spec_from_file_location(f"streamlit_app.pages.{page_key}", page_file)
        if spec is None or spec.loader is None:
            LOGGER.error("Failed to create spec for: %s", page_file)
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"streamlit_app.pages.{page_key}"] = module
        spec.loader.exec_module(module)

        if not hasattr(module, "render"):
            LOGGER.error("Page module %s missing render()", page_key)
            return None

        return module
    except Exception as exc:
        LOGGER.exception("Failed to load page module %s: %s", page_key, exc)
        return None


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main() -> None:
    """Main application entry point."""
    inject_global_css()
    load_local_css(STYLES_PATH)
    apply_theme("dark")

    page_key = render_sidebar()
    display_health_check()

    page_module = load_page(page_key)
    if page_module is None:
        st.markdown(
            "<div class='error-panel'><h3>Page unavailable</h3><p>The selected page could not be loaded. Please refresh the dashboard or choose another section.</p></div>",
            unsafe_allow_html=True,
        )
        return

    try:
        page_module.render()
        LOGGER.info("Rendered page: %s", page_key)
    except Exception as exc:
        LOGGER.exception("Failed to render page %s: %s", page_key, exc)
        st.markdown(
            "<div class='error-panel'><h3>Rendering failed</h3><p>An unexpected issue occurred while loading this page. Refresh the app or verify dataset/model files.</p></div>",
            unsafe_allow_html=True,
        )
        with st.expander("Debug details"):
            st.code(str(exc))


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()

    st.markdown("---")
    st.markdown(
        "<div class='footer-panel'>" 
        "<strong>Shopper Spectrum</strong> • Built with Python, Streamlit, pandas, Plotly, NumPy and scikit-learn. "
        "<br>GitHub: <a href='#'>github.com/your-repo</a> • LinkedIn: <a href='#'>linkedin.com/in/your-name</a></div>",
        unsafe_allow_html=True,
    )
