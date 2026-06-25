import logging
import pickle
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional, Type

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"


def setup_logger(name: str = "shopper_spectrum", level: int = logging.INFO) -> logging.Logger:
    """Create a logger with a rotating file handler and console output."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.propagate = False
    logger.debug("Logger initialized at %s", LOG_FILE)
    return logger


def resolve_safe_path(path: Path, base_dir: Path = ROOT_DIR) -> Path:
    """Resolve a path and prevent path traversal outside the base directory."""
    candidate = path if path.is_absolute() else base_dir / path
    resolved = candidate.resolve()
    if base_dir not in resolved.parents and resolved != base_dir:
        raise ValueError("Unsafe path detected: path must remain within project root.")
    return resolved


def safe_read_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Read a CSV file with automatic encoding fallback."""
    try:
        return pd.read_csv(path, **kwargs)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="ISO-8859-1", **kwargs)


def safe_load_model(path: Path, base_dir: Path = ROOT_DIR) -> Any:
    """Load a pickle model safely and return a Python object."""
    safe_path = resolve_safe_path(path, base_dir=base_dir)
    if not safe_path.exists():
        raise FileNotFoundError(f"Model file not found: {safe_path}")

    try:
        with safe_path.open("rb") as file_obj:
            return pickle.load(file_obj)
    except (pickle.UnpicklingError, EOFError) as exc:
        raise ValueError(f"Model file is corrupted or invalid: {safe_path} - {exc}")
    except Exception as exc:
        raise ValueError(f"Unexpected error loading model: {exc}")


def safe_load_data(path: Path, **kwargs) -> pd.DataFrame:
    """Load a CSV dataset safely and handle common file errors."""
    safe_path = resolve_safe_path(path, base_dir=ROOT_DIR)
    if not safe_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {safe_path}")
    if safe_path.stat().st_size == 0:
        raise pd.errors.EmptyDataError(f"Dataset file is empty: {safe_path}")

    try:
        return safe_read_csv(safe_path, low_memory=False, **kwargs)
    except pd.errors.EmptyDataError:
        raise
    except pd.errors.ParserError as exc:
        raise ValueError(f"Dataset parsing failed: {exc}")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Dataset encoding error: {exc}")
    except Exception as exc:
        raise ValueError(f"Unknown error reading dataset: {exc}")


def validate_user_input(
    value: Any, 
    field_name: str = "value", 
    min_value: Optional[float] = None, 
    max_value: Optional[float] = None
) -> float:
    """Validate user-provided numeric input for Streamlit widgets."""
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required.")

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a number.")

    if min_value is not None and number < min_value:
        raise ValueError(f"{field_name} must be at least {min_value}.")
    if max_value is not None and number > max_value:
        raise ValueError(f"{field_name} must be at most {max_value}.")

    return number


def show_error_message(message: str, advice: str = "Please check the input and try again.") -> None:
    """Render a Streamlit-friendly error message with advice."""
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.markdown("⚠️")
    with col2:
        st.markdown(f"**{message}**")
    
    if advice:
        with st.expander("Details", expanded=False):
            st.markdown(f"{advice}")


def render_error_card(title: str, message: str, details: str = "") -> None:
    """Render a professional error card with expandable details."""
    st.markdown(
        f"""
        <div class='error-panel'>
            <h3>{title}</h3>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if details:
        with st.expander("Technical details"):
            st.code(details)


def render_warning_card(title: str, message: str) -> None:
    """Render a warning card."""
    st.markdown(
        f"""
        <div class='warning-panel'>
            <h4>⚠️ {title}</h4>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def log_error(exc: Exception, context: str = "", logger: Optional[logging.Logger] = None) -> None:
    """Log exceptions with context and optional logger."""
    log = logger or setup_logger()
    if context:
        log.exception("%s: %s", context, exc)
    else:
        log.exception("Unhandled exception: %s", exc)


# ============================================================================
# ENHANCED UI COMPONENTS & UTILITIES
# ============================================================================

def render_metric_card(title: str, value: str, description: str = "", trend: str = "") -> None:
    """
    Render a professional metric card with optional trend indicator.
    
    Args:
        title: Metric title
        value: Metric value (formatted as string)
        description: Optional description text
        trend: Optional trend indicator (e.g., "+15%", "-3%")
    """
    trend_html = ""
    if trend:
        trend_class = "positive" if trend.startswith("+") else "negative" if trend.startswith("-") else "neutral"
        trend_html = f'<div class="metric-trend {trend_class}">{trend}</div>'
    
    st.markdown(
        f"""
        <div class='metric-card'>
            <h4>{title}</h4>
            <div class='metric-value'>{value}</div>
            {f'<div class="metric-meta">{description}</div>' if description else ''}
            {trend_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str = "") -> None:
    """Render a professional section header with optional subtitle."""
    st.markdown(
        f"""
        <div>
            <h2 class='section-title'>{title}</h2>
            {f'<p class="section-subtitle">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_card(title: str, content: str) -> None:
    """Render an information card."""
    st.markdown(
        f"""
        <div class='info-card'>
            <h4>{title}</h4>
            <p>{content}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_segment_card(
    segment_name: str,
    stats: dict,
    segment_class: str = "regular"
) -> None:
    """
    Render a customer segment card.
    
    Args:
        segment_name: Name of the segment
        stats: Dictionary of {label: value} pairs
        segment_class: CSS class for styling (high-value, regular, occasional, at-risk)
    """
    stats_html = ""
    for label, value in stats.items():
        stats_html += f"""
        <div class='segment-card-stat'>
            <span class='segment-card-stat-label'>{label}</span>
            <span class='segment-card-stat-value'>{value}</span>
        </div>
        """
    
    st.markdown(
        f"""
        <div class='segment-card {segment_class}'>
            <h3>{segment_name}</h3>
            {stats_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(
    product_name: str,
    similarity_score: float,
    additional_info: str = ""
) -> None:
    """
    Render a product recommendation card.
    
    Args:
        product_name: Product name/title
        similarity_score: Similarity score (0-1) formatted as percentage
        additional_info: Optional additional information
    """
    st.markdown(
        f"""
        <div class='recommendation-card'>
            <h4>{product_name}</h4>
            {f'<p style="font-size: 0.9rem; color: var(--muted);">{additional_info}</p>' if additional_info else ''}
            <div class='recommendation-score'>
                <span class='recommendation-score-label'>Match Score</span>
                <span class='recommendation-score-value'>{similarity_score:.1%}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_currency(value: float, currency: str = "₹") -> str:
    """Format numeric value as currency string."""
    try:
        if value >= 1_000_000:
            return f"{currency}{value / 1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{currency}{value / 1_000:.2f}K"
        return f"{currency}{value:.2f}"
    except Exception:
        return str(value)


def format_number(value: int) -> str:
    """Format numeric value with commas."""
    try:
        return f"{value:,}"
    except Exception:
        return str(value)


def format_currency(value: float, currency: str = "₹") -> str:
    """Format numeric value as currency string."""
    if value >= 1_000_000:
        return f"{currency}{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{currency}{value / 1_000:.2f}K"
    return f"{currency}{value:.2f}"


def format_number(value: int) -> str:
    """Format numeric value with thousands separator."""
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    return f"{value:,}"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text


# ============================================================================
# PERFORMANCE OPTIMIZATION HELPERS
# ============================================================================

@st.cache_data(show_spinner=False)
def get_cached_data(data_source):
    """Generic cache wrapper for data retrieval."""
    return data_source()


def get_session_state(key: str, default: Any = None) -> Any:
    """Get value from Streamlit session state with default."""
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


def set_session_state(key: str, value: Any) -> None:
    """Set value in Streamlit session state."""
    st.session_state[key] = value
