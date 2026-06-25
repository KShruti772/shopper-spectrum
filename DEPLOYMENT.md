# 🚀 Deployment Guide — Shopper Spectrum

Production-ready deployment instructions for Shopper Spectrum on Streamlit Cloud, Render, Railway, and Hugging Face Spaces.

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [Alternative Deployments](#alternative-deployments)
4. [Performance Optimization](#performance-optimization)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

Before deploying to production, verify the following:

### ✅ Local Testing

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app locally
streamlit run streamlit_app/app.py

# 4. Test all pages and features
# - Home Dashboard
# - Customer Segmentation
# - Product Recommendations
# - Analytics Dashboard
# - Input Forms
```

### ✅ Code Quality

- [ ] All imports are in `requirements.txt` with pinned versions
- [ ] No hardcoded absolute paths (use `pathlib.Path`)
- [ ] All data files use relative paths
- [ ] Model files exist in `models/` directory
- [ ] CSS file loads successfully
- [ ] `.streamlit/config.toml` is present
- [ ] No API keys or secrets in code
- [ ] Health check system passes all checks

### ✅ File Structure

```
Shopper Spectrum/
├── streamlit_app/
│   ├── app.py                    ✓ Production-ready
│   ├── pages/
│   │   ├── home.py              ✓
│   │   ├── analytics.py         ✓
│   │   ├── segmentation.py      ✓
│   │   ├── recommendation.py    ✓
│   │   ├── segmentation_input.py ✓
│   │   └── insights.py          ✓
│   ├── utils/
│   │   ├── helpers.py           ✓ Enhanced with UI components
│   │   ├── model_loader.py      ✓
│   │   ├── data_loader.py       ✓
│   │   ├── dashboard_helpers.py ✓
│   │   └── validators.py        ✓
│   └── styles/
│       └── styles.css           ✓ Production-grade CSS
├── .streamlit/
│   └── config.toml              ✓ Optimized settings
├── models/                       ✓ Pre-trained models
├── data/                         ✓ Dataset files
├── requirements.txt              ✓ Pinned versions
└── README.md                     ✓ Updated documentation
```

---

## Streamlit Cloud Deployment

### Step 1: Prepare GitHub Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "🚀 Production-ready Shopper Spectrum dashboard"

# Push to GitHub
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/shopper-spectrum.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Visit [Streamlit Cloud Console](https://share.streamlit.io)
2. Click **"New app"**
3. Select your GitHub repository
4. Configure deployment:
   - **Repository**: YOUR_USERNAME/shopper-spectrum
   - **Branch**: main
   - **Main file path**: streamlit_app/app.py
5. Click **"Deploy"**

### Step 3: Monitor Deployment

- Streamlit Cloud will install dependencies from `requirements.txt`
- App will be available at `https://share.streamlit.io/YOUR_USERNAME/shopper-spectrum`
- Check deployment logs for any errors

### Step 4: Custom Domain (Optional)

1. Go to app settings
2. Configure custom domain
3. Update DNS records at your domain provider

---

## Alternative Deployments

### Render Deployment

```bash
# 1. Create render.yaml in project root
cat > render.yaml << 'EOF'
services:
  - type: web
    name: shopper-spectrum
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run streamlit_app/app.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: STREAMLIT_SERVER_HEADLESS
        value: true
      - key: STREAMLIT_SERVER_PORT
        value: 10000
EOF

# 2. Push to GitHub
git add render.yaml
git commit -m "Add Render configuration"
git push

# 3. Deploy on Render
# Visit https://render.com
# Connect GitHub account
# Create new Web Service
# Select your repository
# Service name: shopper-spectrum
# Runtime: Python 3
# Build command: pip install -r requirements.txt
# Start command: streamlit run streamlit_app/app.py --server.port $PORT --server.address 0.0.0.0
```

### Railway Deployment

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Create project
railway init

# 4. Create Procfile in project root
echo "web: streamlit run streamlit_app/app.py" > Procfile

# 5. Deploy
railway up

# 6. Get app URL
railway logs
```

### Hugging Face Spaces

1. Create new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Select **Streamlit** as Space SDK
3. Clone the space repository
4. Copy project files to the space
5. Commit and push changes
6. App will deploy automatically

---

## Performance Optimization

### Caching Best Practices

All data loading and ML model operations use Streamlit caching:

```python
# Already implemented in your codebase:
@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    """Cached data loading"""
    return pd.read_csv(path)

@st.cache_resource(show_spinner=False)
def load_model(path: Path):
    """Cached model loading"""
    return pickle.load(open(path, 'rb'))
```

### Production Recommendations

1. **Set appropriate cache TTL**:
   ```python
   @st.cache_data(ttl=3600)  # Cache for 1 hour
   def load_data():
       return pd.read_csv("data.csv")
   ```

2. **Monitor app performance**:
   - Use Streamlit Cloud analytics
   - Check response times
   - Monitor memory usage

3. **Optimize data processing**:
   - Lazy-load dataframes
   - Use vectorized operations
   - Avoid unnecessary computations

### CDN Setup (Optional)

For static assets, consider using a CDN:

```python
# Use relative paths for CSS/images
st.markdown(f"""
    <link rel="stylesheet" href="styles/styles.css">
""", unsafe_allow_html=True)
```

---

## Monitoring & Maintenance

### Health Checks

The app includes an automated health check system:

```python
# Visible in sidebar
✅ App Status: Operational

# Or with diagnostics
📋 System Diagnostics
  - Missing Files
  - Missing Modules
  - Missing Models
  - Dataset Status
```

### Log Monitoring

Logs are stored in `logs/app.log`:

```bash
# View logs locally
tail -f logs/app.log

# On Streamlit Cloud: check deployment logs
```

### Scheduled Maintenance

1. **Weekly**: Review error logs
2. **Monthly**: Update dependencies (if needed)
3. **Quarterly**: Performance optimization review

---

## Troubleshooting

### Common Issues

#### 1. **"Module not found" Error**

**Problem**: ImportError when deploying

**Solution**:
```bash
# Ensure all imports are in requirements.txt
pip freeze > requirements.txt

# Verify versions are compatible
pip install -r requirements.txt

# Test locally
streamlit run streamlit_app/app.py
```

#### 2. **"File not found" Error**

**Problem**: Models or data files missing in deployment

**Solution**:
```python
# Use pathlib for safe path handling
from pathlib import Path

# Always use relative paths
model_path = Path(__file__).parent.parent / "models" / "model.pkl"

# Never use absolute paths
# ✗ WRONG: "C:\Users\...\models\model.pkl"
# ✓ RIGHT: Path(__file__).parent.parent / "models" / "model.pkl"
```

#### 3. **Slow App Performance**

**Problem**: App takes too long to load

**Solution**:
```python
# Implement caching
@st.cache_data(show_spinner=False)
def expensive_operation():
    # Long-running operations
    return result

# Use st.cache_resource for models
@st.cache_resource
def load_model():
    return load_ml_model()
```

#### 4. **CSS Not Loading**

**Problem**: Styling looks broken

**Solution**:
```python
# Verify CSS file path
css_path = Path(__file__).parent / "styles" / "styles.css"
assert css_path.exists(), f"CSS not found at {css_path}"

# Load CSS explicitly
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
```

#### 5. **Out of Memory**

**Problem**: App crashes with memory error

**Solution**:
```python
# Use st.cache_data wisely
# Avoid caching very large dataframes
# Use efficient data types

df = pd.read_csv(file)
df['category'] = df['category'].astype('category')  # Save memory
df['date'] = pd.to_datetime(df['date'])

# Delete unnecessary data
del large_df  # Free memory
```

---

## Security Considerations

### ✅ Implemented Protections

- **Path Traversal Prevention**: All file paths validated
- **Safe Pickle Loading**: Error handling for corrupted models
- **Input Validation**: User inputs sanitized
- **Error Messages**: Safe error handling (no sensitive info exposed)
- **Logging**: All errors logged securely

### 🔐 Additional Recommendations

1. **Never commit secrets**:
   ```bash
   # Add to .gitignore
   .env
   *.key
   *.pem
   secrets.toml
   ```

2. **Use environment variables for sensitive data**:
   ```python
   import os
   api_key = os.getenv("API_KEY")
   ```

3. **Enable HTTPS**: Streamlit Cloud handles this automatically

---

## Continuous Integration/Deployment (CI/CD)

### GitHub Actions Setup

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: python -m pytest tests/
      
      - name: Deploy to Streamlit Cloud
        run: |
          streamlit run streamlit_app/app.py
```

---

## Performance Metrics

### Expected Performance (Production)

- **Initial Load**: 2-5 seconds (first visit)
- **Subsequent Loads**: < 1 second (cached)
- **Page Navigation**: < 500ms
- **Chart Rendering**: 1-2 seconds
- **Search/Filter**: < 1 second

### Monitoring Tools

- **Streamlit Cloud Analytics**: Built-in dashboard
- **Google Analytics**: Optional third-party integration
- **Custom Logging**: Implemented in `logs/app.log`

---

## Rollback Procedure

If deployment fails:

```bash
# On Streamlit Cloud:
1. Go to app settings
2. Select previous deployment
3. Click "Redeploy"

# On Render/Railway:
1. Access deployment history
2. Select previous version
3. Click "Redeploy"
```

---

## Support & Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Streamlit Community**: https://discuss.streamlit.io
- **GitHub Issues**: https://github.com/streamlit/streamlit/issues
- **Project Issues**: https://github.com/YOUR_USERNAME/shopper-spectrum/issues

---

## Update Procedure

To update the deployed app:

```bash
# 1. Make changes locally
git add .
git commit -m "Fix: description of changes"

# 2. Push to GitHub
git push origin main

# 3. Streamlit Cloud auto-deploys (may take 1-2 minutes)

# 4. Verify deployment
# Visit: https://share.streamlit.io/YOUR_USERNAME/shopper-spectrum
```

---

**Last Updated**: 2025  
**Version**: 2.0.0 (Production-Ready)  
**Maintainer**: Vighnesh
