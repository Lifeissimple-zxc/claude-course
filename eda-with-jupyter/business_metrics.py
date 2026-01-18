"""
Business Metrics Module for E-commerce Analysis

This module provides functions to calculate key business metrics including
revenue, order statistics, product performance, and customer experience metrics.
"""

import pandas as pd
from typing import Dict, Optional


class RevenueMetrics:
    """Calculate revenue-related business metrics."""

    @staticmethod
    def calculate_total_revenue(sales_df: pd.DataFrame) -> float:
        """
        Calculate total revenue from sales data.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset containing 'price' column

        Returns
        -------
        float
            Total revenue
        """
        return sales_df['price'].sum()

    @staticmethod
    def calculate_revenue_growth(
        current_df: pd.DataFrame,
        previous_df: pd.DataFrame
    ) -> float:
        """
        Calculate revenue growth percentage between two periods.

        Parameters
        ----------
        current_df : pd.DataFrame
            Current period sales data
        previous_df : pd.DataFrame
            Previous period sales data

        Returns
        -------
        float
            Growth percentage (e.g., 0.15 for 15% growth)
        """
        current_revenue = RevenueMetrics.calculate_total_revenue(current_df)
        previous_revenue = RevenueMetrics.calculate_total_revenue(previous_df)

        if previous_revenue == 0:
            return 0.0

        return (current_revenue - previous_revenue) / previous_revenue

    @staticmethod
    def calculate_monthly_revenue(sales_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate revenue by month.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset with 'year', 'month', and 'price' columns

        Returns
        -------
        pd.DataFrame
            Monthly revenue data
        """
        monthly = sales_df.groupby(['year', 'month'])['price'].sum().reset_index()
        monthly.columns = ['year', 'month', 'revenue']
        return monthly

    @staticmethod
    def calculate_mom_growth(sales_df: pd.DataFrame) -> pd.Series:
        """
        Calculate month-over-month growth rate.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset with 'month' and 'price' columns

        Returns
        -------
        pd.Series
            Month-over-month growth rates
        """
        monthly_revenue = sales_df.groupby('month')['price'].sum().sort_index()
        return monthly_revenue.pct_change()

    @staticmethod
    def calculate_revenue_by_category(sales_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate revenue by product category.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset with 'product_category_name' and 'price' columns

        Returns
        -------
        pd.DataFrame
            Revenue by category, sorted descending
        """
        category_revenue = (
            sales_df.groupby('product_category_name')['price']
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        category_revenue.columns = ['category', 'revenue']
        return category_revenue

    @staticmethod
    def calculate_revenue_by_state(sales_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate revenue by customer state.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset with 'customer_state' and 'price' columns

        Returns
        -------
        pd.DataFrame
            Revenue by state, sorted descending
        """
        state_revenue = (
            sales_df.groupby('customer_state')['price']
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        state_revenue.columns = ['state', 'revenue']
        return state_revenue


class OrderMetrics:
    """Calculate order-related business metrics."""

    @staticmethod
    def calculate_total_orders(sales_df: pd.DataFrame) -> int:
        """
        Calculate total number of unique orders.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset containing 'order_id' column

        Returns
        -------
        int
            Number of unique orders
        """
        return sales_df['order_id'].nunique()

    @staticmethod
    def calculate_average_order_value(sales_df: pd.DataFrame) -> float:
        """
        Calculate average order value (AOV).

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset with 'order_id' and 'price' columns

        Returns
        -------
        float
            Average order value
        """
        order_totals = sales_df.groupby('order_id')['price'].sum()
        return order_totals.mean()

    @staticmethod
    def calculate_order_growth(
        current_df: pd.DataFrame,
        previous_df: pd.DataFrame
    ) -> float:
        """
        Calculate order count growth percentage between two periods.

        Parameters
        ----------
        current_df : pd.DataFrame
            Current period sales data
        previous_df : pd.DataFrame
            Previous period sales data

        Returns
        -------
        float
            Growth percentage
        """
        current_orders = OrderMetrics.calculate_total_orders(current_df)
        previous_orders = OrderMetrics.calculate_total_orders(previous_df)

        if previous_orders == 0:
            return 0.0

        return (current_orders - previous_orders) / previous_orders

    @staticmethod
    def calculate_items_per_order(sales_df: pd.DataFrame) -> float:
        """
        Calculate average number of items per order.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset with 'order_id' and 'order_item_id' columns

        Returns
        -------
        float
            Average items per order
        """
        items_per_order = sales_df.groupby('order_id')['order_item_id'].count()
        return items_per_order.mean()

    @staticmethod
    def calculate_order_status_distribution(orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate distribution of order statuses.

        Parameters
        ----------
        orders_df : pd.DataFrame
            Orders dataset with 'order_status' column

        Returns
        -------
        pd.DataFrame
            Order status distribution with counts and percentages
        """
        status_dist = orders_df['order_status'].value_counts()
        status_pct = orders_df['order_status'].value_counts(normalize=True)

        result = pd.DataFrame({
            'status': status_dist.index,
            'count': status_dist.values,
            'percentage': status_pct.values * 100
        })

        return result


class CustomerExperienceMetrics:
    """Calculate customer experience metrics."""

    @staticmethod
    def calculate_average_review_score(sales_df: pd.DataFrame) -> float:
        """
        Calculate average review score.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset with 'review_score' column

        Returns
        -------
        float
            Average review score
        """
        return sales_df['review_score'].mean()

    @staticmethod
    def calculate_review_distribution(sales_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate distribution of review scores.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset with 'review_score' column

        Returns
        -------
        pd.DataFrame
            Review score distribution
        """
        review_dist = sales_df['review_score'].value_counts(normalize=True).sort_index()
        result = pd.DataFrame({
            'score': review_dist.index,
            'percentage': review_dist.values * 100
        })
        return result

    @staticmethod
    def calculate_average_delivery_time(sales_df: pd.DataFrame) -> float:
        """
        Calculate average delivery time in days.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset with 'delivery_days' column

        Returns
        -------
        float
            Average delivery time in days
        """
        return sales_df['delivery_days'].mean()

    @staticmethod
    def categorize_delivery_speed(days: float) -> str:
        """
        Categorize delivery speed into buckets.

        Parameters
        ----------
        days : float
            Number of delivery days

        Returns
        -------
        str
            Delivery speed category
        """
        if days <= 3:
            return '1-3 days'
        elif days <= 7:
            return '4-7 days'
        else:
            return '8+ days'

    @staticmethod
    def calculate_delivery_speed_impact(sales_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate impact of delivery speed on review scores.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset with 'delivery_days' and 'review_score' columns

        Returns
        -------
        pd.DataFrame
            Average review score by delivery speed category
        """
        # Create a copy to avoid SettingWithCopyWarning
        df = sales_df[['order_id', 'delivery_days', 'review_score']].drop_duplicates().copy()

        # Categorize delivery speed
        df['delivery_category'] = df['delivery_days'].apply(
            CustomerExperienceMetrics.categorize_delivery_speed
        )

        # Calculate average review score by category
        result = (
            df.groupby('delivery_category')['review_score']
            .mean()
            .reset_index()
        )
        result.columns = ['delivery_category', 'avg_review_score']

        # Order categories logically
        category_order = ['1-3 days', '4-7 days', '8+ days']
        result['delivery_category'] = pd.Categorical(
            result['delivery_category'],
            categories=category_order,
            ordered=True
        )
        result = result.sort_values('delivery_category')

        return result

    @staticmethod
    def calculate_on_time_delivery_rate(sales_df: pd.DataFrame) -> float:
        """
        Calculate percentage of orders delivered on or before estimated date.

        Parameters
        ----------
        sales_df : pd.DataFrame
            Sales dataset with 'delivery_delay_days' column

        Returns
        -------
        float
            On-time delivery rate (0-1)
        """
        on_time = (sales_df['delivery_delay_days'] <= 0).sum()
        total = len(sales_df)

        if total == 0:
            return 0.0

        return on_time / total


class MetricsSummary:
    """Generate comprehensive business metrics summary."""

    @staticmethod
    def generate_summary(
        current_sales: pd.DataFrame,
        previous_sales: Optional[pd.DataFrame] = None,
        orders_df: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Generate a comprehensive metrics summary.

        Parameters
        ----------
        current_sales : pd.DataFrame
            Current period sales data
        previous_sales : pd.DataFrame, optional
            Previous period sales data for comparison
        orders_df : pd.DataFrame, optional
            Orders dataset for status distribution

        Returns
        -------
        Dict
            Dictionary containing all calculated metrics
        """
        summary = {}

        # Revenue metrics
        summary['revenue'] = {
            'total': RevenueMetrics.calculate_total_revenue(current_sales),
            'by_month': RevenueMetrics.calculate_monthly_revenue(current_sales).to_dict('records'),
            'by_category': RevenueMetrics.calculate_revenue_by_category(current_sales).to_dict('records'),
            'by_state': RevenueMetrics.calculate_revenue_by_state(current_sales).to_dict('records')
        }

        if previous_sales is not None:
            summary['revenue']['growth_pct'] = (
                RevenueMetrics.calculate_revenue_growth(current_sales, previous_sales) * 100
            )

        # Order metrics
        summary['orders'] = {
            'total_orders': OrderMetrics.calculate_total_orders(current_sales),
            'average_order_value': OrderMetrics.calculate_average_order_value(current_sales),
            'items_per_order': OrderMetrics.calculate_items_per_order(current_sales)
        }

        if previous_sales is not None:
            summary['orders']['order_growth_pct'] = (
                OrderMetrics.calculate_order_growth(current_sales, previous_sales) * 100
            )

        if orders_df is not None:
            summary['orders']['status_distribution'] = (
                OrderMetrics.calculate_order_status_distribution(orders_df).to_dict('records')
            )

        # Customer experience metrics
        summary['customer_experience'] = {
            'avg_review_score': CustomerExperienceMetrics.calculate_average_review_score(current_sales),
            'avg_delivery_days': CustomerExperienceMetrics.calculate_average_delivery_time(current_sales),
            'on_time_delivery_rate': CustomerExperienceMetrics.calculate_on_time_delivery_rate(current_sales),
            'review_distribution': CustomerExperienceMetrics.calculate_review_distribution(current_sales).to_dict('records'),
            'delivery_speed_impact': CustomerExperienceMetrics.calculate_delivery_speed_impact(current_sales).to_dict('records')
        }

        return summary
