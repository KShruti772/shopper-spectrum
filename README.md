<!-- PROJECT SHIELD -->
# Shopper Spectrum: Customer Segmentation and Product Recommendations in E-Commerce

Elegant, production-oriented code for segmenting customers and recommending products using real e-commerce transactions.

---

## Project Overview

Shopper Spectrum is an end-to-end analytics project that demonstrates how to build customer segmentation (RFM + clustering) and item-based collaborative filtering recommendations for an online retail dataset. The repository includes data processing utilities, exploratory notebooks, model training scripts, a lightweight model persistence layer, and a Streamlit demo to explore results interactively.

## Problem Statement

Online retailers need to identify high-value customers for retention, understand purchase behavior for inventory planning, and recommend relevant products to increase average order value. This project shows how to: (1) compute RFM features, (2) segment customers using KMeans, and (3) recommend similar products using item-based collaborative filtering.

## Features

- Data loading & cleaning utilities
- Exploratory Data Analysis (EDA) notebooks with visualizations
- RFM feature engineering and RFM scoring
- KMeans customer segmentation with cluster profiling and visualization
- Item-based collaborative filtering recommender with search-friendly product matching
- Model persistence (save/load scaler & clustering model)
- Streamlit app for interactive exploration: KPIs, segmentation, and recommendations
- Evaluation scripts for clustering and recommendation quality

## Technologies Used

- Python 3.8+
- pandas, numpy
- scikit-learn
- matplotlib, seaborn, plotly
- Streamlit for the interactive demo
- joblib / pickle for model persistence

## Dataset Description

The project uses an online retail transactions dataset with the following core columns:

- `InvoiceNo` — Invoice identifier (string)
- `StockCode` — Product code
- `Description` — Product name / description
- `Quantity` — Number of product units in the transaction
- `InvoiceDate` — Invoice date/time
- `UnitPrice` — Unit price of the product
- `CustomerID` — Customer identifier
- `Country` — Customer country

Place the dataset file `online_retail.csv` in the project root (already included in this workspace). Processed datasets and generated artifacts are placed under `data/processed/`.

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
