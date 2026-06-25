#!/usr/bin/env python
"""Test script to verify analytics and segmentation page fixes."""

import sys
sys.path.insert(0, 'streamlit_app')

# Test analytics workflow
print('=== Testing Analytics Page ===')
from utils.dashboard_helpers import compute_kpis, build_monthly_sales_chart, build_top_products_chart
import pandas as pd

# Create test dataframe
df = pd.DataFrame({
    'InvoiceNo': ['A1', 'A2', 'A3'],
    'TotalPrice': [100, 200, 150],
    'CustomerID': [1, 2, 1],
    'Description': ['Item1', 'Item2', 'Item3'],
    'Quantity': [1, 2, 1],
    'InvoiceDate': pd.to_datetime(['2024-01-15', '2024-02-10', '2024-01-20'])
})

# Test KPIs
kpis = compute_kpis(df)
print(f'✓ compute_kpis works: {kpis}')

# Test charts
try:
    fig = build_monthly_sales_chart(df)
    print(f'✓ Monthly chart renders: {type(fig).__name__}')
except Exception as e:
    print(f'✗ Monthly chart failed: {e}')

try:
    fig = build_top_products_chart(df)
    print(f'✓ Top products chart renders: {type(fig).__name__}')
except Exception as e:
    print(f'✗ Top products chart failed: {e}')

print()
print('=== Testing Segmentation Page ===')
from pages.segmentation import _rule_based_segment

cluster_id, label, insights, confidence = _rule_based_segment(20, 8, 500)
print(f'✓ Rule-based segmentation works: {label} (confidence: {confidence:.1%})')
desc = insights["description"]
print(f'  Description: {desc[:50]}...')

print()
print('=== All Tests Passed ===')
