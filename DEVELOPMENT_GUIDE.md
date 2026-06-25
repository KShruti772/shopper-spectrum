# 🛠️ Development Guide — Shopper Spectrum

Guide for extending, modifying, and maintaining the Shopper Spectrum dashboard.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Adding New Features](#adding-new-features)
3. [Creating New Pages](#creating-new-pages)
4. [Modifying Existing Pages](#modifying-existing-pages)
5. [Working with Utilities](#working-with-utilities)
6. [Best Practices](#best-practices)
7. [Debugging Tips](#debugging-tips)

---

## Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────────┐
│   Streamlit Pages (UI Layer)            │
│  (home.py, analytics.py, etc.)          │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│   Utilities Layer                       │
│   (helpers.py, model_loader.py, etc.)   │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│   Data & Model Layer                    │
│   (data_loader.py, engines, etc.)       │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│   External Resources                    │
│   (CSV files, Pickle models)            │
└─────────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **app.py** | Entry point, routing | `streamlit_app/app.py` |
| **Pages** | UI for each section | `streamlit_app/pages/*.py` |
| **Helpers** | UI components & utilities | `streamlit_app/utils/helpers.py` |
| **Data Loaders** | Safe data/model loading | `streamlit_app/utils/data_loader.py` |
| **Engines** | ML logic (segmentation, CF) | `streamlit_app/utils/*_engine.py` |
| **Styling** | CSS & theme | `streamlit_app/styles/styles.css` |

---

## Adding New Features

### 1. Create a New Page

#### Step 1: Create page file

```python
# streamlit_app/pages/new_feature.py
"""
New Feature Page

Description of what this page does.
"""

import streamlit as st
from pathlib import Path
from streamlit_app.utils.helpers import render_section_header

def render():
    """Main render function called by app.py"""
    
    # Page header
    render_section_header(
        "✨ New Feature",
        "Brief description of the feature"
    )
    
    # Your feature code
    st.write("Welcome to the new feature!")


# IMPORTANT: Must have a render() function
# This is called from app.py
```

#### Step 2: Add to navigation in app.py

```python
# In render_sidebar() function
page = st.sidebar.radio(
    "📖 Navigate",
    ["Home", "New Feature", ...],  # Add here
    index=0,
)
```

#### Step 3: Add to page loader

```python
# In load_page() function
page_map = {
    "home": "streamlit_app.pages.home",
    "new_feature": "streamlit_app.pages.new_feature",  # Add this
    # ... other pages
}
```

### 2. Add New Utility Functions

```python
# In streamlit_app/utils/helpers.py

def new_utility_function(param1: str, param2: int) -> str:
    """
    Brief description of what this function does.
    
    Args:
        param1 (str): Description of param1
        param2 (int): Description of param2
    
    Returns:
        str: Description of return value
    
    Example:
        >>> result = new_utility_function("test", 42)
        >>> print(result)
        'Result: 42'
    """
    return f"Result: {param2}"
```

### 3. Add New Caching Layer

```python
# For data operations
@st.cache_data(ttl=3600, show_spinner=False)
def load_custom_data() -> pd.DataFrame:
    """Load and cache custom data"""
    return pd.read_csv("data.csv")

# For ML resources
@st.cache_resource
def load_custom_model():
    """Load and cache custom model"""
    return pickle.load(open("model.pkl", "rb"))
```

---

## Creating New Pages

### Template for New Page

```python
"""
Page Title

Detailed description of page functionality.
"""

import streamlit as st
from pathlib import Path
from streamlit_app.utils.helpers import (
    render_section_header,
    render_metric_card,
    render_info_card,
)

# Setup
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def render():
    """Main render function"""
    
    # 1. Page Header
    render_section_header(
        "📊 Page Title",
        "Brief description"
    )
    
    # 2. Load Data/Models
    try:
        # data = load_data()
        # model = load_model()
        pass
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return
    
    # 3. Main Content
    tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])
    
    with tab1:
        st.markdown("<div class='section-title'>Section 1</div>", unsafe_allow_html=True)
        # Content here
    
    with tab2:
        st.markdown("<div class='section-title'>Section 2</div>", unsafe_allow_html=True)
        # Content here
    
    # 4. Footer
    st.markdown("---")
    render_info_card(
        "📌 Summary",
        "Key takeaways or next steps"
    )


# Must have render() function
if __name__ == "__main__":
    render()
```

---

## Modifying Existing Pages

### Common Modifications

#### 1. Add a New Chart

```python
import plotly.express as px

# In your page
fig = px.bar(
    data,
    x='category',
    y='value',
    title='Chart Title',
    height=400
)

st.plotly_chart(fig, use_container_width=True)
```

#### 2. Add User Input

```python
# Text input
product_name = st.text_input("Enter product name")

# Slider
n_recommendations = st.slider("Number of recommendations", 1, 10, 5)

# Selectbox
segment = st.selectbox("Select segment", ["All", "High-Value", "Regular", "Occasional", "At-Risk"])

# Form
with st.form("my_form"):
    name = st.text_input("Name")
    age = st.slider("Age", 18, 100)
    submitted = st.form_submit_button("Submit")
```

#### 3. Add Conditional Logic

```python
if st.sidebar.checkbox("Show advanced options"):
    option1 = st.number_input("Option 1")
    option2 = st.number_input("Option 2")
    # Use options...

if len(data) == 0:
    st.warning("No data available")
else:
    st.dataframe(data)
```

#### 4. Add Error Handling

```python
try:
    result = expensive_operation()
    st.success(f"Operation completed: {result}")
except ValueError as e:
    st.error(f"Invalid input: {e}")
except Exception as e:
    st.error(f"Unexpected error: {e}")
    with st.expander("Details"):
        st.code(str(e))
```

---

## Working with Utilities

### Using Helper Functions

```python
from streamlit_app.utils.helpers import (
    render_metric_card,
    render_section_header,
    format_currency,
    format_number,
)

# Render components
render_section_header("Sales Report", "Monthly overview")
render_metric_card("Total Revenue", format_currency(50000), "Last 30 days")

# Format values
price = format_currency(1000)  # "₹1.00K"
count = format_number(150000)  # "150.00K"
```

### Loading Data Safely

```python
from streamlit_app.utils.data_loader import load_data

try:
    df = load_data(Path("data/online_retail.csv"))
    st.dataframe(df.head())
except FileNotFoundError:
    st.error("Dataset not found")
except Exception as e:
    st.error(f"Failed to load data: {e}")
```

### Loading Models Safely

```python
from streamlit_app.utils.model_loader import load_pickle_resource

try:
    model = load_pickle_resource(Path("models/kmeans_model.pkl"))
    predictions = model.predict(X)
except FileNotFoundError:
    st.error("Model file not found")
except ValueError as e:
    st.error(f"Model is corrupted: {e}")
```

---

## Best Practices

### 1. Use Type Hints

```python
# ✅ GOOD: Clear types
def process_data(df: pd.DataFrame, n_clusters: int) -> Dict[str, Any]:
    """Process data and return results"""
    pass

# ❌ AVOID: No type hints
def process_data(df, n_clusters):
    """Process data and return results"""
    pass
```

### 2. Add Docstrings

```python
# ✅ GOOD: Comprehensive docstring
def analyze_segment(segment_id: str) -> pd.DataFrame:
    """
    Analyze customer segment performance.
    
    Args:
        segment_id: Unique segment identifier
    
    Returns:
        DataFrame with segment metrics
    
    Raises:
        ValueError: If segment_id not found
    """
    pass

# ❌ AVOID: No docstring
def analyze_segment(segment_id):
    pass
```

### 3. Use Constants

```python
# ✅ GOOD: Define constants at top
DEFAULT_N_CLUSTERS = 4
CACHE_TTL_HOURS = 1
CACHE_TTL = CACHE_TTL_HOURS * 3600

@st.cache_data(ttl=CACHE_TTL)
def load_data():
    pass

# ❌ AVOID: Magic numbers
@st.cache_data(ttl=3600)
def load_data():
    pass
```

### 4. Error Handling

```python
# ✅ GOOD: Specific error handling
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    st.error(f"File not found: {file_path}")
except pd.errors.EmptyDataError:
    st.error("Dataset is empty")
except Exception as e:
    st.error(f"Unexpected error: {e}")
    LOGGER.exception("Error loading data")

# ❌ AVOID: Catching all exceptions silently
try:
    df = pd.read_csv(file_path)
except:
    pass
```

### 5. Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_data(df):
    logger.info("Processing data with shape %s", df.shape)
    try:
        result = df.groupby('category').sum()
        logger.info("Processing completed successfully")
        return result
    except Exception as e:
        logger.error("Processing failed: %s", e)
        raise
```

---

## Debugging Tips

### 1. Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug information: %s", variable)
```

### 2. Use Streamlit Debugging

```python
import streamlit as st

# Display variables for debugging
with st.expander("🐛 Debug Info"):
    st.write("DataFrame shape:", df.shape)
    st.write("Session state:", st.session_state)
    st.write("DataFrame columns:", df.columns.tolist())
    st.dataframe(df.head(3))
```

### 3. Check Cached Data

```python
# Force cache clear
if st.sidebar.button("Clear Cache"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.success("Cache cleared!")

# Display cache status
st.write("Cache info:", st.caching)
```

### 4. Profile Performance

```python
import time

@st.cache_data
def slow_function():
    start = time.time()
    # Your code
    result = expensive_operation()
    elapsed = time.time() - start
    print(f"Execution time: {elapsed:.2f}s")
    return result
```

### 5. Test Locally

```bash
# Run with debug logging
streamlit run streamlit_app/app.py --logger.level=debug

# Run with profile
streamlit run streamlit_app/app.py --profiler=speedscope
```

---

## File Organization

### When to create new files

**Create a new file if:**
- Function has 200+ lines
- Functionality is reusable across pages
- Logic is separate from UI

**Keep in same file if:**
- Function has < 50 lines
- Only used in one page
- Tightly coupled with page logic

### Naming conventions

```
utilities        → helpers.py, validators.py
engines          → segmentation_engine.py, recommendation_engine.py
loaders          → data_loader.py, model_loader.py
pages            → home.py, analytics.py (lowercase, no spaces)
classes          → SegmentationEngine, DataLoader (PascalCase)
functions        → load_data, validate_input (snake_case)
constants        → DEFAULT_CLUSTERS, CACHE_TTL (UPPER_CASE)
```

---

## Common Tasks

### How to add a new chart type

1. Import plotting library:
   ```python
   import plotly.express as px
   import plotly.graph_objects as go
   ```

2. Prepare data:
   ```python
   chart_data = df.groupby('category')['value'].sum()
   ```

3. Create figure:
   ```python
   fig = px.bar(chart_data, title="Chart Title")
   ```

4. Display in Streamlit:
   ```python
   st.plotly_chart(fig, use_container_width=True)
   ```

### How to add a new metric card

```python
from streamlit_app.utils.helpers import render_metric_card

render_metric_card(
    title="Total Revenue",
    value="₹50,000",
    description="Last 30 days",
    trend="+15%"
)
```

### How to add caching

```python
from streamlit import cache_data, cache_resource

# For data
@cache_data(ttl=3600)
def load_data():
    return pd.read_csv("data.csv")

# For resources
@cache_resource
def load_model():
    return pickle.load(open("model.pkl", "rb"))
```

---

## Testing Checklist

Before committing code:

- [ ] No syntax errors
- [ ] All imports are used
- [ ] Type hints correct
- [ ] Docstrings present
- [ ] Error handling implemented
- [ ] Logging in critical sections
- [ ] No hardcoded paths
- [ ] Works locally
- [ ] No console errors
- [ ] Performance acceptable

---

## Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- [Python Style Guide (PEP 8)](https://pep8.org)
- [Type Hints (PEP 484)](https://www.python.org/dev/peps/pep-0484/)

---

**Last Updated**: 2025  
**Version**: 1.0  
**Maintainer**: Vighnesh
