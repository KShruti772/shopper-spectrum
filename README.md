<!-- PROJECT SHIELD -->
# Shopper Spectrum: Customer Segmentation and Product Recommendations in E-Commerce

**🚀 Production-Grade Analytics Dashboard**  
Elegant, industry-level code for customer segmentation and intelligent product recommendations using real e-commerce transactions.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 🎯 Project Overview

Shopper Spectrum is a **production-ready SaaS-style analytics platform** that demonstrates how to build enterprise-grade customer segmentation (RFM + KMeans clustering) and item-based collaborative filtering recommendations for e-commerce. The project includes:

- ✅ **Production-Grade Streamlit Dashboard** with premium UI/UX design
- ✅ **Data Processing Pipeline** with safety checks and error handling
- ✅ **ML Models** (RFM scoring, KMeans clustering, similarity-based recommendations)
- ✅ **Comprehensive Testing & Health Checks** for deployment reliability
- ✅ **Deployment-Ready** with documentation for 4+ platforms
- ✅ **Performance Optimization** with intelligent caching strategies
- ✅ **Professional CSS Styling** with responsive design

---

## 💼 Problem Statement

Online retailers face three critical challenges:

1. **Customer Retention**: Identifying high-value customers at risk of churn
2. **Inventory Optimization**: Understanding purchase behavior for stock planning
3. **Revenue Growth**: Recommending relevant products to increase AOV

Shopper Spectrum demonstrates production-ready solutions for all three.

---

## ✨ Key Features

### Dashboard & UI
- 🎨 **Premium Dark Theme** with modern glassmorphism design
- 📊 **Real-Time KPI Cards** showing revenue, customers, transactions, products
- 📈 **Interactive Charts** built with Plotly for exploration
- 🎯 **Responsive Layout** optimized for desktop, tablet, and mobile
- ⚡ **Performance-Optimized** with aggressive caching strategies

### Analytics & ML
- 🏷️ **Customer Segmentation** using RFM analysis + KMeans clustering
- 💰 **Recency-Frequency-Monetary (RFM)** feature engineering
- 🔍 **Item-Based Collaborative Filtering** for product recommendations
- 📉 **Cluster Profiling** with actionable business insights
- 📊 **Evaluation Metrics** (Elbow Method, Silhouette Score, Precision@K)

### Data & Infrastructure
- 🔒 **Safe Data Loading** with automatic encoding detection
- 🛡️ **Path Traversal Protection** for secure file access
- 📝 **Comprehensive Logging** to `logs/app.log`
- ⚙️ **Health Check System** for production monitoring
- 🚀 **Deployment-Ready** configuration for Streamlit Cloud, Render, Railway

### Code Quality
- 🧹 **Type Hints** throughout the codebase
- 📚 **Docstrings** for all functions
- ✅ **Input Validation** on all user inputs
- 🐛 **Error Handling** with graceful fallbacks
- 🔧 **Modular Architecture** for easy maintenance

---

## 🛠️ Technologies

| Category | Technologies |
|----------|--------------|
| **Frontend** | Streamlit, Plotly, HTML/CSS |
| **Data Science** | Pandas, NumPy, Scikit-learn |
| **ML Models** | KMeans, Cosine Similarity, StandardScaler |
| **Deployment** | Streamlit Cloud, Docker, GitHub Actions |
| **Code Quality** | Type hints, Docstrings, Logging |

---

## 📊 Dataset Description

Uses real e-commerce transactions with these core columns:

| Column | Type | Description |
|--------|------|-------------|
| `InvoiceNo` | String | Unique invoice identifier |
| `StockCode` | String | Product SKU code |
| `Description` | String | Product name/description |
| `Quantity` | Integer | Units purchased |
| `InvoiceDate` | DateTime | Transaction timestamp |
| `UnitPrice` | Float | Price per unit |
| `CustomerID` | String | Unique customer identifier |
| `Country` | String | Customer location |

**Download**: Place `online_retail.csv` in the project root. Dataset already included in workspace.

---

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/shopper-spectrum.git
cd shopper-spectrum

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Locally

```bash
# Start the Streamlit app
streamlit run streamlit_app/app.py

# App opens at: http://localhost:8501
```

### 3. Explore the Dashboard

- **Home** → KPIs and dataset overview
- **Analytics** → Revenue trends and customer insights
- **Customer Segmentation** → View clusters and segment profiles
- **Product Recommendation** → Search and get recommendations
- **Segmentation Input** → Predict segment for new customer
- **Insights** → Advanced analysis and business recommendations

---

## 📁 Project Structure

```
Shopper Spectrum/
│
├── streamlit_app/                    # Main Streamlit application
│   ├── app.py                        # Entry point with health checks
│   ├── styles/
│   │   └── styles.css                # Production-grade CSS (2000+ lines)
│   ├── pages/
│   │   ├── home.py                   # KPI dashboard
│   │   ├── analytics.py              # Revenue analytics
│   │   ├── segmentation.py           # Customer segments
│   │   ├── recommendation.py         # Product recommendations
│   │   ├── segmentation_input.py     # Prediction form
│   │   └── insights.py               # Business insights
│   ├── utils/
│   │   ├── helpers.py                # UI components & utilities
│   │   ├── model_loader.py           # Safe model loading
│   │   ├── data_loader.py            # Safe data loading
│   │   ├── dashboard_helpers.py      # Chart/metric functions
│   │   ├── preprocessing.py          # Data transformations
│   │   ├── validators.py             # Input validation
│   │   ├── recommendation_engine.py  # CF recommendations
│   │   └── segmentation_engine.py    # Clustering logic
│   └── assets/                       # Images, logos, icons
│
├── notebooks/                        # Jupyter notebooks
│   ├── 01_eda_shopper_spectrum.py
│   ├── 02_rfm_analysis.py
│   ├── 03_kmeans_segmentation.py
│   ├── 04_model_persistence_test.py
│   ├── 05_item_based_cf.py
│   └── 06_evaluation.py
│
├── utils/                            # Core utilities
│   ├── cleaning.py
│   ├── data_utils.py
│   ├── feature_engineering.py
│   └── model_persistence.py
│
├── models/                           # Pre-trained ML models
│   ├── kmeans_model.pkl
│   ├── kmeans_scaler.pkl
│   └── similarity_matrix.pkl
│
├── data/                             # Data files
│   ├── online_retail.csv             # Raw dataset
│   ├── processed/                    # Generated artifacts
│   └── README.md
│
├── .streamlit/
│   └── config.toml                   # Streamlit configuration
│
├── logs/                             # Application logs
│   └── app.log
│
├── requirements.txt                  # Production dependencies
├── DEPLOYMENT.md                     # Deployment guide
└── README.md                         # This file
```

---

## 🎨 UI/UX Improvements (v2.0)

### Design System
- **Dark Analytics Theme** inspired by Power BI and Tableau
- **Design Tokens**: CSS variables for consistent styling
- **12-Column Grid Layout** for responsive design
- **Premium Spacing Scale**: Consistent padding/margins
- **Smooth Animations**: Fade-in, slide-in, pulse effects

### Components
- **Metric Cards** with gradient backgrounds and hover effects
- **Segment Cards** with color-coded borders by customer type
- **Recommendation Cards** with similarity scores
- **Info Panels** with clear typography hierarchy
- **Responsive Tables** with alternating row colors
- **Modern Buttons** with gradient fills and hover states

### Responsive Design
- ✅ Desktop (1200px+)
- ✅ Laptop (1024px)
- ✅ Tablet (768px)
- ✅ Mobile (480px)

---

## ⚡ Performance Optimizations

### Caching Strategy
```python
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Cached data loading"""
    return safe_read_csv(path)

@st.cache_resource
def load_model():
    """Cached model loading"""
    return safe_load_model(path)
```

### Expected Performance
- **Initial Load**: 2-5 seconds (first visit)
- **Cached Loads**: < 1 second
- **Chart Rendering**: 1-2 seconds
- **Page Navigation**: < 500ms

---

## 🏥 Health Check System

Automatic monitoring of critical components:

```
✅ App Status: Operational

📋 System Diagnostics
  ✓ CSS Files
  ✓ Configuration
  ✓ Critical Modules
  ✓ ML Models
  ✓ Dataset
```

---

## 🚀 Deployment

### Streamlit Cloud (Recommended)

```bash
# 1. Push to GitHub
git add .
git commit -m "Production release"
git push origin main

# 2. Deploy on Streamlit Cloud
# Visit: https://share.streamlit.io
# Click "New app"
# Select your repository
# Main file: streamlit_app/app.py

# 3. Share publicly
# Your app: https://share.streamlit.io/YOUR_USERNAME/shopper-spectrum
```

### Other Platforms
- **Render**: See `DEPLOYMENT.md` for instructions
- **Railway**: See `DEPLOYMENT.md` for instructions
- **Hugging Face Spaces**: See `DEPLOYMENT.md` for instructions
- **Docker**: Create Dockerfile for custom deployments

**📖 Full Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📊 Machine Learning Techniques

### Customer Segmentation
1. **RFM Analysis**
   - Recency: Days since last purchase
   - Frequency: Number of transactions
   - Monetary: Total spending
   
2. **KMeans Clustering**
   - Standardized RFM features
   - Elbow method for optimal K
   - Silhouette score for validation

### Product Recommendations
1. **Item-Based Collaborative Filtering**
   - TF-IDF vectorization of items
   - Cosine similarity matrix
   - Top-K recommendations

2. **Evaluation Metrics**
   - Precision@K
   - Recall@K
   - NDCG@K

---

## 📈 Evaluation & Metrics

### Clustering Quality
- **Silhouette Score**: Measures cluster cohesion (higher is better)
- **Inertia**: Within-cluster sum of squares
- **Davies-Bouldin Index**: Average similarity ratio

### Recommendation Quality
- **Precision@K**: Relevance of top-K recommendations
- **Recall@K**: Coverage of relevant items
- **NDCG@K**: Ranking quality metric

---

## 🔒 Security Features

- ✅ **Safe Path Handling**: No path traversal attacks
- ✅ **Input Validation**: All user inputs sanitized
- ✅ **Error Handling**: Safe exception handling
- ✅ **Logging**: Secure event tracking
- ✅ **No Secrets**: No hardcoded credentials
- ✅ **Data Safety**: Safe pickle loading

---

## 🐛 Troubleshooting

### "Module not found" Error
```bash
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

### "File not found" Error
Ensure models and data files are in correct directories:
```
models/kmeans_model.pkl
models/kmeans_scaler.pkl
models/similarity_matrix.pkl
online_retail.csv (or data/online_retail.csv)
```

### CSS Not Loading
```python
# Verify CSS file path
from pathlib import Path
css_path = Path("streamlit_app/styles/styles.css")
assert css_path.exists(), f"CSS not found at {css_path}"
```

### Slow Performance
- Ensure caching is working: `@st.cache_data`
- Check logs: `tail -f logs/app.log`
- Reduce dataset size if testing locally

**📖 Full Troubleshooting Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting)

---

## 🔄 Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and test locally
streamlit run streamlit_app/app.py

# 3. Commit changes
git add .
git commit -m "feat: description"

# 4. Push to GitHub
git push origin feature/new-feature

# 5. Create Pull Request

# 6. Deploy to production
git merge main
git push origin main
# Auto-deploys on Streamlit Cloud
```

---

## 📚 Resources & Documentation

- **Streamlit Docs**: https://docs.streamlit.io
- **Scikit-Learn**: https://scikit-learn.org
- **Plotly**: https://plotly.com/python
- **Pandas**: https://pandas.pydata.org

---

## 🎓 Use Cases

This project is suitable for:

- 📌 **Portfolio Projects** - Showcase on GitHub
- 🏢 **Internships** - Demonstrate ML + UI skills
- 💼 **Job Applications** - Real-world analytics project
- 🚀 **Hackathons** - Complete SaaS template
- 👨‍💼 **LinkedIn** - Professional project showcase
- 📊 **Learning** - Understanding ML + Streamlit + Deployment

---

## 🎯 Future Enhancements

- 📱 Mobile app (React Native)
- 🔄 Real-time data pipelines (Kafka)
- 🤖 Advanced ML (LightGBM, XGBoost)
- 🌐 Multi-language support
- 📊 Advanced analytics (Cohort analysis, LTV)
- 🔐 User authentication & RBAC
- 📈 A/B testing framework
- 🎯 Business metrics dashboard

---

## 👨‍💻 Author

**Vighnesh**  
Data Analyst & ML Engineer

- 🔗 [GitHub](https://github.com/YOUR_USERNAME)
- 💼 [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)
- 📧 your.email@example.com

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- Dataset source: Online Retail Dataset
- Inspired by real-world e-commerce analytics
- Built with ❤️ for the data science community

---

## 📞 Support

- 🐛 **Report Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/shopper-spectrum/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/shopper-spectrum/discussions)
- 📖 **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md) and [README.md](README.md)

---

**Version**: 2.0.0 (Production-Ready)  
**Last Updated**: 2025  
**Status**: 🟢 Active & Maintained

## Machine Learning Techniques

- RFM (Recency, Frequency, Monetary) feature engineering for customer behavioral summarization
- KMeans clustering for customer segmentation
- StandardScaler for feature standardization
- Cosine similarity for item-based collaborative filtering
- Elbow method and Silhouette score for cluster validation

## Installation

1. Create a Python virtual environment and activate it:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) If you plan to use the notebooks, install Jupyter:

```bash
pip install jupyterlab
```

## Running the Streamlit App

Start the interactive demo (from the project root):

```bash
streamlit run streamlit_app/app.py
```

Pages available in the app:
- Home — KPIs and interactive charts
- Customer Segmentation — cluster overviews and sample customers
- Product Recommendation — search a product and get top-N similar items
- Segmentation Input — manual RFM -> predicted segment

## Screenshots

Add application screenshots to the `images/` folder and reference them here. Example:

![Home Screenshot](images/home_screenshot.png)
![Recommendations Screenshot](images/recommendations_screenshot.png)

_If screenshots are not available yet, take snapshots after running the Streamlit app._

## Evaluation and Metrics

- Elbow curve and Silhouette score are used to guide the number of clusters.
- Cluster profiling tables reveal average Recency, Frequency, and Monetary per segment.
- Recommendation quality is evaluated with a simple leave-one-out Precision@K offline test. For production, use timestamped splits and rank-aware metrics such as MAP@K or NDCG.

## Future Improvements

- Integrate session/context features and product metadata for hybrid recommendations
- Use time-aware train/test splits and negative sampling for more robust evaluation
- Add automated model training pipelines and CI/CD for model promotion
- Add real-time inference endpoint (FastAPI) for serving recommendations at scale
- Improve UI with authentication and user personalization

## Business Impact

This project demonstrates practical levers for e-commerce teams:

- Identify and retain high-value customers with targeted offers
- Increase average order value with personalized recommendations
- Optimize inventory and marketing spend by focusing on products that drive revenue and customer lifetime value

## Author

Vighnesh (Project maintainer)

---

For questions or help running the project, open an issue or contact the author.
