"""
Data Loading and Processing Module for E-commerce Analysis

This module provides functions to load, clean, and prepare e-commerce data
from CSV files for analysis.
"""

import pandas as pd
from typing import Dict, Tuple, Optional
from pathlib import Path


class EcommerceDataLoader:
    """Handles loading and preprocessing of e-commerce datasets."""

    def __init__(self, data_dir: str = 'ecommerce_data'):
        """
        Initialize the data loader.

        Parameters
        ----------
        data_dir : str
            Path to the directory containing CSV files
        """
        self.data_dir = Path(data_dir)
        self.datasets = {}

    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all e-commerce datasets from CSV files.

        Returns
        -------
        Dict[str, pd.DataFrame]
            Dictionary containing all loaded datasets
        """
        datasets = {
            'orders': self._load_orders(),
            'order_items': self._load_order_items(),
            'products': self._load_products(),
            'customers': self._load_customers(),
            'reviews': self._load_reviews(),
            'payments': self._load_payments()
        }
        self.datasets = datasets
        return datasets

    def _load_orders(self) -> pd.DataFrame:
        """Load and preprocess orders dataset."""
        df = pd.read_csv(self.data_dir / 'orders_dataset.csv')

        # Convert timestamp columns to datetime
        timestamp_cols = [
            'order_purchase_timestamp',
            'order_approved_at',
            'order_delivered_carrier_date',
            'order_delivered_customer_date',
            'order_estimated_delivery_date'
        ]
        for col in timestamp_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        return df

    def _load_order_items(self) -> pd.DataFrame:
        """Load and preprocess order items dataset."""
        df = pd.read_csv(self.data_dir / 'order_items_dataset.csv')

        # Convert shipping limit date to datetime
        df['shipping_limit_date'] = pd.to_datetime(df['shipping_limit_date'], errors='coerce')

        return df

    def _load_products(self) -> pd.DataFrame:
        """Load and preprocess products dataset."""
        return pd.read_csv(self.data_dir / 'products_dataset.csv')

    def _load_customers(self) -> pd.DataFrame:
        """Load and preprocess customers dataset."""
        return pd.read_csv(self.data_dir / 'customers_dataset.csv')

    def _load_reviews(self) -> pd.DataFrame:
        """Load and preprocess reviews dataset."""
        df = pd.read_csv(self.data_dir / 'order_reviews_dataset.csv')

        # Convert timestamp columns to datetime
        df['review_creation_date'] = pd.to_datetime(df['review_creation_date'], errors='coerce')
        df['review_answer_timestamp'] = pd.to_datetime(df['review_answer_timestamp'], errors='coerce')

        return df

    def _load_payments(self) -> pd.DataFrame:
        """Load and preprocess payments dataset."""
        return pd.read_csv(self.data_dir / 'order_payments_dataset.csv')

    def create_sales_dataset(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        status_filter: str = 'delivered'
    ) -> pd.DataFrame:
        """
        Create a comprehensive sales dataset by merging relevant tables.

        Parameters
        ----------
        year : int, optional
            Filter data for specific year
        month : int, optional
            Filter data for specific month
        status_filter : str
            Order status to filter (default: 'delivered')

        Returns
        -------
        pd.DataFrame
            Merged and filtered sales dataset
        """
        # Ensure datasets are loaded
        if not self.datasets:
            self.load_all_datasets()

        orders = self.datasets['orders'].copy()
        order_items = self.datasets['order_items'].copy()
        products = self.datasets['products'].copy()
        customers = self.datasets['customers'].copy()
        reviews = self.datasets['reviews'].copy()

        # Merge order items with orders
        sales = pd.merge(
            order_items[['order_id', 'order_item_id', 'product_id', 'seller_id', 'price', 'freight_value']],
            orders[['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp',
                   'order_delivered_customer_date', 'order_estimated_delivery_date']],
            on='order_id',
            how='left'
        )

        # Filter by order status
        if status_filter:
            sales = sales[sales['order_status'] == status_filter].copy()

        # Add time-based columns
        sales['year'] = sales['order_purchase_timestamp'].dt.year
        sales['month'] = sales['order_purchase_timestamp'].dt.month
        sales['quarter'] = sales['order_purchase_timestamp'].dt.quarter
        sales['day_of_week'] = sales['order_purchase_timestamp'].dt.dayofweek

        # Calculate delivery speed (in days)
        sales['delivery_days'] = (
            sales['order_delivered_customer_date'] - sales['order_purchase_timestamp']
        ).dt.days

        # Calculate delivery delay (actual vs estimated)
        sales['delivery_delay_days'] = (
            sales['order_delivered_customer_date'] - sales['order_estimated_delivery_date']
        ).dt.days

        # Filter by year and month if specified
        if year is not None:
            sales = sales[sales['year'] == year].copy()
        if month is not None:
            sales = sales[sales['month'] == month].copy()

        # Merge with products to get category information
        sales = pd.merge(
            sales,
            products[['product_id', 'product_category_name']],
            on='product_id',
            how='left'
        )

        # Merge with customers to get location information
        sales = pd.merge(
            sales,
            customers[['customer_id', 'customer_state', 'customer_city']],
            on='customer_id',
            how='left'
        )

        # Merge with reviews to get review scores
        sales = pd.merge(
            sales,
            reviews[['order_id', 'review_score']],
            on='order_id',
            how='left'
        )

        return sales

    def get_data_summary(self) -> Dict[str, Dict]:
        """
        Get summary statistics for all loaded datasets.

        Returns
        -------
        Dict[str, Dict]
            Summary statistics for each dataset
        """
        if not self.datasets:
            self.load_all_datasets()

        summary = {}
        for name, df in self.datasets.items():
            summary[name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
                'missing_values': df.isnull().sum().to_dict()
            }

        return summary
