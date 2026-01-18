# E-commerce Business Analytics Dashboard

Professional Streamlit dashboard for visualizing and analyzing e-commerce business metrics.

## Features

- **Interactive Date Filtering**: Analyze different years with automatic comparison to previous periods
- **Key Performance Indicators**: Track Total Revenue, Monthly Growth, Average Order Value, and Total Orders with trend indicators
- **Revenue Analysis**: Monthly revenue trends with year-over-year comparisons
- **Product Insights**: Top 10 performing product categories
- **Geographic Distribution**: US choropleth map showing revenue by state
- **Customer Experience**: Satisfaction analysis correlated with delivery times
- **Professional Styling**: Clean, modern interface with responsive design

## Dashboard Layout

### Header
- Title and year selection filter (applies to all metrics)

### KPI Row
Four metric cards displaying:
1. Total Revenue (with YoY trend)
2. Average Monthly Growth
3. Average Order Value (with YoY trend)
4. Total Orders (with YoY trend)

Trend indicators use green for positive changes and red for negative changes.

### Chart Grid (2x2)
1. **Revenue Trend Line Chart**: Monthly revenue with current year (solid) vs previous year (dashed)
2. **Top 10 Categories Bar Chart**: Horizontal bar chart with blue gradient
3. **Revenue by State Map**: US choropleth with lavender gradient
4. **Satisfaction vs Delivery Scatter**: Shows correlation between delivery time and review scores with trendline

### Bottom Row
1. **Average Delivery Time**: Large metric card with trend indicator
2. **Review Score**: Star rating display with average score

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd /path/to/eda-with-jupyter
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On macOS/Linux
   source venv/bin/activate

   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify data directory**
   Ensure the `ecommerce_data` directory exists with the following CSV files:
   - `orders_dataset.csv`
   - `order_items_dataset.csv`
   - `products_dataset.csv`
   - `customers_dataset.csv`
   - `order_reviews_dataset.csv`
   - `order_payments_dataset.csv`

## Running the Dashboard

### Start the Streamlit Application

```bash
streamlit run dashboard.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`.

### Using the Dashboard

1. **Select Analysis Period**: Use the dropdown in the top-right to select which year to analyze (2023, 2022, or 2021)
2. **View KPIs**: The four metric cards update automatically to show the selected period with comparison to the previous year
3. **Explore Charts**: All visualizations are interactive - hover over data points for detailed information
4. **Compare Trends**: The revenue trend chart shows both current and previous year for easy comparison

## Project Structure

```
eda-with-jupyter/
├── dashboard.py              # Main Streamlit dashboard application
├── data_loader.py            # Data loading and preprocessing module
├── business_metrics.py       # Business metrics calculation module
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── EDA_refactored.ipynb     # Original Jupyter notebook analysis
└── ecommerce_data/          # Data directory
    ├── orders_dataset.csv
    ├── order_items_dataset.csv
    ├── products_dataset.csv
    ├── customers_dataset.csv
    ├── order_reviews_dataset.csv
    └── order_payments_dataset.csv
```

## Key Technologies

- **Streamlit**: Web application framework for data dashboards
- **Plotly**: Interactive visualization library
- **Pandas**: Data manipulation and analysis
- **NumPy & SciPy**: Numerical computing and statistical analysis

## Data Flow

1. **Data Loading**: `EcommerceDataLoader` loads and preprocesses CSV files
2. **Metric Calculation**: Business metrics modules calculate KPIs
3. **Visualization**: Plotly creates interactive charts
4. **Dashboard Rendering**: Streamlit displays the complete interface

## Customization

### Adding New Metrics

1. Add metric calculation to `business_metrics.py`
2. Update `dashboard.py` to display the new metric
3. Optionally add new visualizations

### Changing the Layout

Edit the `dashboard.py` file:
- Modify column configurations (e.g., `st.columns([2, 1])`)
- Adjust CSS styling in the `st.markdown()` section
- Reorder components as needed

### Styling

All CSS styling is contained in the custom CSS section at the top of `dashboard.py`. Modify colors, fonts, spacing, and layout properties there.

## Performance Optimization

- Data loading is cached using `@st.cache_data` decorator
- Sales data preparation is cached per year/month combination
- Charts use `config={'displayModeBar': False}` for cleaner interface

## Troubleshooting

### Dashboard doesn't load
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check that the `ecommerce_data` directory exists with all CSV files
- Ensure you're running from the correct directory

### Charts not displaying
- Check browser console for JavaScript errors
- Try clearing Streamlit cache: Add `?clear_cache=true` to the URL or restart the server

### Performance issues
- Consider filtering data to smaller date ranges
- Check available system memory
- Streamlit may need to recompile - refresh the page

## Contributing

This dashboard is part of an e-commerce analytics project. To contribute:

1. Test changes thoroughly with sample data
2. Ensure all visualizations render correctly
3. Maintain professional styling consistency
4. Update this README with any new features

## License

This project is for educational and analytical purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Streamlit documentation: https://docs.streamlit.io
3. Review Plotly documentation: https://plotly.com/python/
