# 🚀 Quick Reference Guide — Shopper Spectrum

Fast lookup for common commands and operations.

---

## 🎯 Quick Links

| Need | Link | Time |
|------|------|------|
| **Getting Started** | [README.md](README.md) | 5 min |
| **Deploy to Cloud** | [DEPLOYMENT.md](DEPLOYMENT.md) | 15 min |
| **Optimize Performance** | [OPTIMIZATION_TIPS.md](OPTIMIZATION_TIPS.md) | 10 min |
| **Extend Features** | [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) | 15 min |
| **Pre-Deploy Check** | [PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md) | 10 min |
| **What's New** | [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md) | 10 min |

---

## 💻 Essential Commands

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Locally

```bash
# Start the app
streamlit run streamlit_app/app.py

# Run with debug logging
streamlit run streamlit_app/app.py --logger.level=debug

# Clear cache on startup
streamlit run streamlit_app/app.py --cache

# Run on specific port
streamlit run streamlit_app/app.py --server.port 8502
```

### Docker

```bash
# Build image
docker build -t shopper-spectrum .

# Run container
docker run -p 8501:8501 shopper-spectrum

# Run with docker-compose
docker-compose up

# Stop container
docker-compose down
```

### Git

```bash
# Add all changes
git add .

# Commit with message
git commit -m "🚀 Production release"

# Push to GitHub
git push origin main

# View logs
git log --oneline

# Create feature branch
git checkout -b feature/new-feature
```

### Testing & Validation

```bash
# Check for syntax errors
python -m py_compile streamlit_app/app.py

# Install test dependencies
pip install pytest flake8

# Run linter
flake8 streamlit_app/

# List installed packages
pip list

# Freeze requirements
pip freeze > requirements.txt
```

---

## 📁 Directory Structure

```
Shopper Spectrum/
├── streamlit_app/              # Main app
│   ├── app.py                  # Entry point
│   ├── pages/                  # Page files
│   ├── utils/                  # Utility functions
│   ├── styles/                 # CSS styling
│   └── assets/                 # Images, icons
├── models/                     # ML models
├── data/                       # Dataset files
├── logs/                       # Application logs
├── notebooks/                  # Jupyter notebooks
├── .streamlit/                 # Streamlit config
├── .github/workflows/          # CI/CD
├── requirements.txt            # Dependencies
├── Dockerfile                  # Docker setup
├── docker-compose.yml          # Dev environment
├── Procfile                    # Render config
└── README.md                   # Documentation
```

---

## 🔑 Key Concepts

### Caching

```python
# Cache data (1 hour)
@st.cache_data(ttl=3600)
def load_data():
    return pd.read_csv("data.csv")

# Cache resource (lifetime)
@st.cache_resource
def load_model():
    return pickle.load(open("model.pkl", "rb"))

# Clear cache manually
st.cache_data.clear()
st.cache_resource.clear()
```

### Components

```python
# Section header
render_section_header("Title", "Subtitle")

# Metric card
render_metric_card("Revenue", "₹50,000", "Last 30 days")

# Info card
render_info_card("Title", "Description text")

# Format values
format_currency(50000)  # "₹50.00K"
format_number(150000)   # "150.00K"
```

### Error Handling

```python
try:
    result = expensive_operation()
except ValueError as e:
    st.error(f"Invalid value: {e}")
except Exception as e:
    st.error(f"Error: {e}")
    with st.expander("Details"):
        st.code(str(e))
```

---

## 🌐 Deployment Quick Links

### Streamlit Cloud
1. Push to GitHub
2. Visit https://share.streamlit.io
3. Click "New app"
4. Select repository & main file
5. Deploy (auto-scales)

**URL Pattern**: `share.streamlit.io/USERNAME/shopper-spectrum`

### Render
1. Connect GitHub
2. Create Web Service
3. Build: `pip install -r requirements.txt`
4. Start: `streamlit run streamlit_app/app.py --server.port $PORT --server.address 0.0.0.0`

### Docker
```bash
docker build -t shopper-spectrum .
docker run -p 8501:8501 shopper-spectrum
```

### Local Compose
```bash
docker-compose up
# Open http://localhost:8501
```

---

## 🔍 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| **Module not found** | `pip install -r requirements.txt` |
| **File not found** | Check relative paths use `pathlib.Path` |
| **CSS not loading** | Verify `styles/styles.css` exists |
| **App too slow** | Add `@st.cache_data` decorator |
| **Out of memory** | Sample large dataframes |
| **Health check fails** | Check all files/models exist |
| **Port already in use** | `streamlit run app.py --server.port 8502` |
| **Cache issues** | `st.cache_data.clear()` |

---

## 📊 Performance Checklist

- [ ] Using `@st.cache_data` for data loading
- [ ] Using `@st.cache_resource` for models
- [ ] Sampling large dataframes (> 10k rows)
- [ ] No unnecessary computations
- [ ] Logging enabled
- [ ] Error handling present
- [ ] Memory usage monitored
- [ ] Load time < 5 seconds

---

## 🔒 Security Checklist

- [ ] No hardcoded credentials
- [ ] No absolute file paths
- [ ] Using `pathlib.Path` for paths
- [ ] Input validation present
- [ ] Error messages safe
- [ ] Logging configured
- [ ] `.gitignore` configured
- [ ] No sensitive files committed

---

## 📚 API Quick Reference

### Streamlit Widgets

```python
# Input
st.text_input("Name")
st.number_input("Age", 0, 100)
st.selectbox("Choose", ["Option 1", "Option 2"])
st.multiselect("Select multiple", ["A", "B", "C"])
st.slider("Value", 0, 100)
st.checkbox("Enable")
st.radio("Choose", ["A", "B"])

# Display
st.write("Text")
st.metric("Label", "Value")
st.dataframe(df)
st.table(df)
st.image("image.png")

# Charts
st.line_chart(df)
st.bar_chart(df)
st.plotly_chart(fig)

# Layout
st.sidebar.write("Sidebar")
col1, col2 = st.columns(2)
with col1:
    st.write("Column 1")
with st.expander("Details"):
    st.write("Hidden content")

# Alerts
st.success("Success")
st.warning("Warning")
st.error("Error")
st.info("Info")
```

---

## 🎨 CSS Classes Quick Reference

```html
<!-- Containers -->
<div class="dashboard-card">Content</div>
<div class="metric-card">KPI</div>
<div class="info-card">Info</div>

<!-- Text -->
<div class="section-title">Title</div>
<div class="section-subtitle">Subtitle</div>

<!-- Colors -->
<span class="text-success">Success</span>
<span class="text-danger">Error</span>
<span class="text-warning">Warning</span>
<span class="text-muted">Muted</span>
```

---

## 🚀 Deployment Checklist (Quick)

```
□ Local testing passed
□ All caches configured
□ Health check passes
□ No errors in logs
□ requirements.txt updated
□ .gitignore configured
□ Push to GitHub
□ Deploy on Streamlit Cloud
□ Verify app loads
□ Test all features
```

---

## 📞 Resources

| Resource | Link |
|----------|------|
| **Streamlit Docs** | https://docs.streamlit.io |
| **Streamlit Gallery** | https://streamlit.io/gallery |
| **Pandas Docs** | https://pandas.pydata.org/docs |
| **Plotly Docs** | https://plotly.com/python |
| **Scikit-learn** | https://scikit-learn.org |

---

## 💡 Tips & Tricks

### Speed up development

```bash
# Use auto-reload
streamlit run app.py --logger.level=warning

# Clear cache on file change
streamlit run app.py --client.caching enabled=false
```

### Debug effectively

```python
with st.expander("🐛 Debug"):
    st.write("Variable:", my_var)
    st.write("Type:", type(my_var))
    st.write("Shape:", my_var.shape)
```

### Optimize charts

```python
# Sample data for large datasets
if len(df) > 10000:
    df = df.sample(10000)

st.plotly_chart(fig, use_container_width=True)
```

### Session state

```python
# Get with default
value = st.session_state.get("key", "default")

# Set value
st.session_state["key"] = "value"

# Clear all
st.session_state.clear()
```

---

## 🎓 Learning Paths

### For Beginners
1. Read README.md (5 min)
2. Run locally (5 min)
3. Explore each page (15 min)
4. Read DEVELOPMENT_GUIDE.md (15 min)

### For Developers
1. Read DEVELOPMENT_GUIDE.md (15 min)
2. Review code structure (15 min)
3. Try adding a feature (30 min)
4. Review OPTIMIZATION_TIPS.md (10 min)

### For DevOps
1. Read DEPLOYMENT.md (15 min)
2. Review config files (10 min)
3. Test local deployment (15 min)
4. Try Streamlit Cloud (15 min)

---

## ✨ Version Info

- **Version**: 2.0.0
- **Status**: Production Ready ✅
- **Last Updated**: 2025
- **Python**: 3.8+
- **License**: MIT

---

**Created for rapid reference. See full documentation for detailed guides.**

🚀 **Happy Coding!**
