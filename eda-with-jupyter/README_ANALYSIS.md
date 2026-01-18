# E-commerce Business Analytics

This project provides a comprehensive, configurable framework for analyzing e-commerce business performance with focus on revenue metrics, customer experience, and operational efficiency.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Features](#features)
- [Code Modules](#code-modules)
- [Usage Examples](#usage-examples)
- [Extending the Analysis](#extending-the-analysis)

## 🎯 Overview

This analysis framework helps answer critical business questions:

- **Revenue Performance**: How is revenue trending? What's the YoY growth?
- **Order Metrics**: What's the average order value? How many orders are we processing?
- **Product Insights**: Which product categories drive the most revenue?
- **Geographic Distribution**: Where are our best-performing markets?
- **Customer Experience**: How satisfied are customers? How does delivery speed impact reviews?

### Key Features

✅ **Configurable Analysis**: Easily analyze different time periods (years, months, quarters)
✅ **Modular Design**: Reusable functions in separate modules for maintainability
✅ **Rich Visualizations**: Professional charts with clear labels and business context
✅ **Comprehensive Metrics**: Revenue, orders, products, geography, and customer experience
✅ **YoY Comparisons**: Built-in support for period-over-period analysis

## 📁 Project Structure

```
eda-with-jupyter/
├── EDA_refactored.ipynb      # Main analysis notebook
├── data_loader.py             # Data loading and preprocessing
├── business_metrics.py        # Business metric calculations
├── requirements.txt           # Python dependencies
├── README_ANALYSIS.md         # This file
└── ecommerce_data/            # CSV data files
    ├── orders_dataset.csv
    ├── order_items_dataset.csv
    ├── products_dataset.csv
    ├── customers_dataset.csv
    ├── order_reviews_dataset.csv
    └── order_payments_dataset.csv
```

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. **Clone or navigate to the project directory**

```bash
cd eda-with-jupyter
```

2. **Create a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Verify installation**

```bash
jupyter --version
python -c "import pandas; import plotly; print('All packages installed successfully')"
```

## 🎬 Quick Start

1. **Launch Jupyter Notebook**

```bash
jupyter notebook
```

2. **Open `EDA_refactored.ipynb`**

3. **Run all cells**

   - Click `Kernel` → `Restart & Run All`
   - Or use keyboard shortcut: `Shift + Enter` to run cells sequentially

4. **View the results**

   The notebook will generate:
   - Summary statistics
   - Revenue trends and comparisons
   - Product category performance
   - Geographic revenue maps
   - Customer satisfaction metrics
   - Delivery performance analysis

## ⚙️ Configuration

### Analyzing Different Time Periods

The analysis is fully configurable. To analyze different periods, modify the configuration section in the notebook (Section 3):

```python
# CONFIGURATION PARAMETERS

# Analyze 2023 data
CURRENT_YEAR = 2023
COMPARISON_YEAR = 2022

# Optional: Analyze specific months
CURRENT_MONTH = None  # None = entire year
COMPARISON_MONTH = None

# Data settings
DATA_DIR = 'ecommerce_data'
ORDER_STATUS = 'delivered'  # Focus on completed orders
```

### Example Configurations

**Analyze Q4 2023 vs Q4 2022:**

```python
# For October
CURRENT_YEAR = 2023
CURRENT_MONTH = 10
COMPARISON_YEAR = 2022
COMPARISON_MONTH = 10
```

**Analyze full year 2022:**

```python
CURRENT_YEAR = 2022
COMPARISON_YEAR = 2021  # If you have 2021 data
CURRENT_MONTH = None
COMPARISON_MONTH = None
```

**Analyze all order statuses:**

```python
ORDER_STATUS = None  # Include canceled, pending, etc.
```

## 🎨 Features

### 1. Revenue Analysis

- Total revenue calculation
- Year-over-year growth
- Month-over-month trends
- Revenue by product category
- Revenue by geographic region

**Visualizations:**
- Monthly revenue trend line chart
- Product category bar chart
- Geographic choropleth map

### 2. Order Metrics

- Total order count
- Average order value (AOV)
- Items per order
- Order status distribution

**Visualizations:**
- Order status distribution chart

### 3. Customer Experience

- Average review score
- Review score distribution
- Average delivery time
- On-time delivery rate
- Delivery speed impact on satisfaction

**Visualizations:**
- Review distribution chart
- Delivery speed vs satisfaction analysis

## 📚 Code Modules

### `data_loader.py`

Handles all data loading and preprocessing operations.

**Key Class:**
- `EcommerceDataLoader`: Main class for data operations

**Key Methods:**
- `load_all_datasets()`: Load all CSV files
- `create_sales_dataset(year, month, status_filter)`: Create merged sales dataset
- `get_data_summary()`: Get dataset statistics

**Example Usage:**

```python
from data_loader import EcommerceDataLoader

loader = EcommerceDataLoader('ecommerce_data')
datasets = loader.load_all_datasets()

# Create sales data for 2023
sales_2023 = loader.create_sales_dataset(
    year=2023,
    status_filter='delivered'
)
```

### `business_metrics.py`

Contains all business metric calculation functions.

**Key Classes:**

1. **`RevenueMetrics`**
   - `calculate_total_revenue()`
   - `calculate_revenue_growth()`
   - `calculate_monthly_revenue()`
   - `calculate_mom_growth()`
   - `calculate_revenue_by_category()`
   - `calculate_revenue_by_state()`

2. **`OrderMetrics`**
   - `calculate_total_orders()`
   - `calculate_average_order_value()`
   - `calculate_order_growth()`
   - `calculate_items_per_order()`
   - `calculate_order_status_distribution()`

3. **`CustomerExperienceMetrics`**
   - `calculate_average_review_score()`
   - `calculate_review_distribution()`
   - `calculate_average_delivery_time()`
   - `calculate_delivery_speed_impact()`
   - `calculate_on_time_delivery_rate()`

4. **`MetricsSummary`**
   - `generate_summary()`: Create comprehensive metrics report

**Example Usage:**

```python
from business_metrics import RevenueMetrics, OrderMetrics

# Calculate revenue
total_revenue = RevenueMetrics.calculate_total_revenue(sales_df)

# Calculate growth
growth = RevenueMetrics.calculate_revenue_growth(
    current_df=sales_2023,
    previous_df=sales_2022
)

# Calculate AOV
aov = OrderMetrics.calculate_average_order_value(sales_df)
```

## 💡 Usage Examples

### Example 1: Analyze Specific Month

```python
# In the configuration section:
CURRENT_YEAR = 2023
CURRENT_MONTH = 12  # December
COMPARISON_YEAR = 2023
COMPARISON_MONTH = 11  # November

# Run the notebook to see December vs November comparison
```

### Example 2: Custom Analysis Outside Notebook

```python
from data_loader import EcommerceDataLoader
from business_metrics import RevenueMetrics

# Load data
loader = EcommerceDataLoader()
sales_q1 = loader.create_sales_dataset(year=2023, month=None)

# Filter for Q1 manually
sales_q1 = sales_q1[sales_q1['quarter'] == 1]

# Calculate metrics
q1_revenue = RevenueMetrics.calculate_total_revenue(sales_q1)
print(f"Q1 2023 Revenue: ${q1_revenue:,.2f}")
```

### Example 3: Export Metrics to JSON

```python
from business_metrics import MetricsSummary
import json

# Generate summary
summary = MetricsSummary.generate_summary(
    current_sales=sales_2023,
    previous_sales=sales_2022,
    orders_df=orders_2023
)

# Export to JSON
with open('metrics_2023.json', 'w') as f:
    json.dump(summary, f, indent=2)
```

## 🔧 Extending the Analysis

### Adding New Metrics

1. **Add function to `business_metrics.py`:**

```python
class RevenueMetrics:
    # ... existing methods ...

    @staticmethod
    def calculate_revenue_per_customer(sales_df: pd.DataFrame) -> float:
        """Calculate average revenue per unique customer."""
        total_revenue = sales_df['price'].sum()
        unique_customers = sales_df['customer_id'].nunique()
        return total_revenue / unique_customers if unique_customers > 0 else 0.0
```

2. **Use in notebook:**

```python
# In a new notebook cell
rpc = RevenueMetrics.calculate_revenue_per_customer(sales_current)
print(f"Revenue per Customer: ${rpc:,.2f}")
```

### Adding New Visualizations

```python
# Example: Revenue by day of week
import matplotlib.pyplot as plt

dow_revenue = sales_current.groupby('day_of_week')['price'].sum()
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

plt.figure(figsize=(10, 6))
plt.bar(days, dow_revenue.values, color='steelblue')
plt.title('Revenue by Day of Week - 2023', fontsize=14, fontweight='bold')
plt.xlabel('Day of Week')
plt.ylabel('Revenue ($)')
plt.show()
```

### Creating Custom Reports

```python
def create_executive_summary(sales_df, previous_df):
    """Generate executive summary report."""

    from business_metrics import RevenueMetrics, OrderMetrics

    report = f"""
    EXECUTIVE SUMMARY
    ==================

    Revenue: ${RevenueMetrics.calculate_total_revenue(sales_df):,.2f}
    Growth: {RevenueMetrics.calculate_revenue_growth(sales_df, previous_df)*100:+.1f}%

    Orders: {OrderMetrics.calculate_total_orders(sales_df):,}
    AOV: ${OrderMetrics.calculate_average_order_value(sales_df):.2f}
    """

    return report

# Use it
print(create_executive_summary(sales_2023, sales_2022))
```

## 📊 Data Dictionary

### Orders Dataset
- `order_id`: Unique identifier for each order
- `customer_id`: Customer identifier
- `order_status`: Status (delivered, canceled, pending, etc.)
- `order_purchase_timestamp`: When order was placed
- `order_delivered_customer_date`: Actual delivery date

### Order Items Dataset
- `order_id`: Links to orders
- `product_id`: Product identifier
- `price`: Item price (excluding freight)
- `freight_value`: Shipping cost

### Products Dataset
- `product_id`: Unique product identifier
- `product_category_name`: Product category

### Customers Dataset
- `customer_id`: Unique customer identifier
- `customer_state`: US state code
- `customer_city`: City name

### Reviews Dataset
- `order_id`: Links to orders
- `review_score`: Rating from 1 (worst) to 5 (best)

## 🛠️ Troubleshooting

### Common Issues

**Issue: `ModuleNotFoundError: No module named 'data_loader'`**

**Solution:** Ensure you're running Jupyter from the project directory:

```bash
cd /path/to/eda-with-jupyter
jupyter notebook
```

**Issue: `FileNotFoundError: [Errno 2] No such file or directory: 'ecommerce_data/orders_dataset.csv'`**

**Solution:** Verify data files exist in the `ecommerce_data` directory. Check the `DATA_DIR` configuration.

**Issue: Visualizations not displaying**

**Solution:**
- For matplotlib/seaborn: Add `%matplotlib inline` at the start
- For plotly: Run `pip install plotly --upgrade`

**Issue: SettingWithCopyWarning**

**Solution:** The refactored code uses `.copy()` to avoid these warnings. If you modify the code, ensure you create explicit copies when filtering DataFrames.

## 📝 Best Practices

1. **Always use delivered orders** for revenue analysis to focus on completed transactions
2. **Document configuration changes** in the notebook markdown cells
3. **Export key metrics** to JSON or CSV for further analysis or reporting
4. **Version control your configurations** if analyzing different periods regularly
5. **Validate data** before analysis (check for nulls, outliers)

## 🤝 Contributing

To add new features or improvements:

1. Add new metric functions to appropriate classes in `business_metrics.py`
2. Update `data_loader.py` if new data transformations are needed
3. Add corresponding visualizations and analysis in the notebook
4. Update this README with new features and examples

## 📄 License

This project is for educational and analytical purposes.

## 📧 Support

For questions or issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the inline documentation in the notebook
3. Examine the docstrings in the Python modules

---

**Happy Analyzing! 📊**
