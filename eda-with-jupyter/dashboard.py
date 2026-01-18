"""
E-commerce Business Analytics Dashboard
Professional Streamlit dashboard for business metrics visualization
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings

# Import custom modules
from data_loader import EcommerceDataLoader
from business_metrics import (
    RevenueMetrics,
    OrderMetrics,
    CustomerExperienceMetrics,
    MetricsSummary
)

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }

    /* Header styling */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0 2rem 0;
    }

    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }

    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }

    .metric-trend {
        font-size: 0.9rem;
        font-weight: 600;
    }

    .trend-positive {
        color: #10b981;
    }

    .trend-negative {
        color: #ef4444;
    }

    /* Chart container */
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 400px;
    }

    /* Bottom card */
    .bottom-card {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .bottom-card-value {
        font-size: 3rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }

    .bottom-card-label {
        color: #666;
        font-size: 1rem;
    }

    /* Remove streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Filter container */
    .filter-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and cache all datasets"""
    loader = EcommerceDataLoader(data_dir='ecommerce_data')
    datasets = loader.load_all_datasets()
    return loader, datasets


@st.cache_data
def prepare_sales_data(_loader, year, month=None):
    """Prepare sales dataset for specific period"""
    return _loader.create_sales_dataset(
        year=year,
        month=month,
        status_filter='delivered'
    )


def format_currency(value):
    """Format value as currency with K/M suffix"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"


def create_trend_indicator(current, previous):
    """Create HTML for trend indicator"""
    change_pct = ((current - previous) / previous * 100) if previous != 0 else 0
    arrow = "↑" if change_pct >= 0 else "↓"
    color_class = "trend-positive" if change_pct >= 0 else "trend-negative"
    sign = "+" if change_pct >= 0 else ""

    return f'<span class="metric-trend {color_class}">{arrow} {sign}{change_pct:.2f}%</span>'


def create_metric_card(label, value, trend_html):
    """Create HTML for metric card"""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {trend_html}
    </div>
    """


def create_revenue_trend_chart(monthly_current, monthly_previous, current_year, previous_year):
    """Create revenue trend line chart with comparison"""
    fig = go.Figure()

    # Current year solid line
    fig.add_trace(go.Scatter(
        x=monthly_current['month'],
        y=monthly_current['revenue'],
        mode='lines+markers',
        name=f'{current_year}',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8)
    ))

    # Previous year dashed line
    fig.add_trace(go.Scatter(
        x=monthly_previous['month'],
        y=monthly_previous['revenue'],
        mode='lines+markers',
        name=f'{previous_year}',
        line=dict(color='#94a3b8', width=2, dash='dash'),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title='Monthly Revenue Trend',
        xaxis_title='Month',
        yaxis_title='Revenue',
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=350,
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            gridcolor='#e5e7eb'
        ),
        yaxis=dict(
            tickformat='$,.0f',
            gridcolor='#e5e7eb'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # Format y-axis with K/M suffix
    fig.update_yaxes(tickformat='$.2s')

    return fig


def create_category_chart(category_revenue):
    """Create top 10 categories bar chart"""
    top_10 = category_revenue.head(10).copy()
    top_10['category_display'] = top_10['category'].str.replace('_', ' ').str.title()

    # Create blue gradient colors (light for lower values, dark for higher)
    max_revenue = top_10['revenue'].max()
    colors = [f'rgba(59, 130, 246, {0.4 + (rev/max_revenue)*0.6})' for rev in top_10['revenue']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=top_10['category_display'],
        x=top_10['revenue'],
        orientation='h',
        marker=dict(color=colors),
        text=[format_currency(rev) for rev in top_10['revenue']],
        textposition='outside'
    ))

    fig.update_layout(
        title='Top 10 Product Categories',
        xaxis_title='Revenue',
        yaxis_title='',
        showlegend=False,
        margin=dict(l=150, r=60, t=60, b=40),
        height=350,
        xaxis=dict(
            tickformat='$.2s',
            gridcolor='#e5e7eb'
        ),
        yaxis=dict(autorange='reversed'),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig


def create_state_map(state_revenue):
    """Create US choropleth map with lavender gradient"""
    fig = go.Figure()

    fig.add_trace(go.Choropleth(
        locations=state_revenue['state'],
        z=state_revenue['revenue'],
        locationmode='USA-states',
        colorscale=[
            [0, '#f3e8ff'],      # Light lavender
            [0.5, '#c084fc'],    # Medium lavender
            [1, '#7c3aed']       # Deep lavender
        ],
        text=state_revenue['state'],
        colorbar=dict(
            title="Revenue",
            tickformat='$.2s',
            len=0.7
        ),
        hovertemplate='<b>%{text}</b><br>Revenue: %{z:$,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='Revenue by State',
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=False,
            bgcolor='rgba(0,0,0,0)'
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        height=350,
        paper_bgcolor='white'
    )

    return fig


def create_satisfaction_scatter(sales_df):
    """Create scatter plot showing satisfaction vs delivery time"""
    # Prepare data by delivery time buckets
    delivery_impact = CustomerExperienceMetrics.calculate_delivery_speed_impact(sales_df)

    # Map categories to numeric values for x-axis
    category_mapping = {'1-3 days': 2, '4-7 days': 5.5, '8+ days': 10}
    delivery_impact['delivery_numeric'] = delivery_impact['delivery_category'].map(category_mapping).astype(float)

    fig = go.Figure()

    # Scatter points
    fig.add_trace(go.Scatter(
        x=delivery_impact['delivery_numeric'],
        y=delivery_impact['avg_review_score'],
        mode='markers',
        marker=dict(
            size=20,
            color='#3b82f6',
            opacity=0.6
        ),
        text=delivery_impact['delivery_category'],
        hovertemplate='<b>%{text}</b><br>Avg Review: %{y:.2f}<extra></extra>',
        showlegend=False
    ))

    # Add trendline
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        delivery_impact['delivery_numeric'],
        delivery_impact['avg_review_score']
    )

    trendline_x = delivery_impact['delivery_numeric']
    trendline_y = slope * trendline_x + intercept

    fig.add_trace(go.Scatter(
        x=trendline_x,
        y=trendline_y,
        mode='lines',
        line=dict(color='#ef4444', width=2, dash='dash'),
        name='Trend',
        showlegend=True
    ))

    fig.update_layout(
        title='Customer Satisfaction vs Delivery Time',
        xaxis_title='Delivery Time',
        yaxis_title='Average Review Score',
        margin=dict(l=40, r=40, t=60, b=40),
        height=350,
        xaxis=dict(
            tickmode='array',
            tickvals=[2, 5.5, 10],
            ticktext=['1-3 days', '4-7 days', '8+ days'],
            gridcolor='#e5e7eb'
        ),
        yaxis=dict(
            range=[3.8, 4.4],
            gridcolor='#e5e7eb'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def main():
    # Load data
    loader, datasets = load_data()

    # Header with title and date filter
    col1, col2 = st.columns([2, 1])

    with col1:
        st.title("E-commerce Business Analytics Dashboard")

    with col2:
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        current_year = st.selectbox(
            "Analysis Period",
            options=[2023, 2022, 2021],
            index=0,
            key='year_filter'
        )
        st.markdown('</div>', unsafe_allow_html=True)

    comparison_year = current_year - 1

    # Prepare data for both periods
    sales_current = prepare_sales_data(loader, current_year)
    sales_comparison = prepare_sales_data(loader, comparison_year)

    # Calculate metrics
    revenue_current = RevenueMetrics.calculate_total_revenue(sales_current)
    revenue_previous = RevenueMetrics.calculate_total_revenue(sales_comparison)

    monthly_revenue_current = RevenueMetrics.calculate_monthly_revenue(sales_current)
    mom_growth = RevenueMetrics.calculate_mom_growth(sales_current)
    avg_mom_growth = mom_growth.mean()

    aov_current = OrderMetrics.calculate_average_order_value(sales_current)
    aov_previous = OrderMetrics.calculate_average_order_value(sales_comparison)

    orders_current = OrderMetrics.calculate_total_orders(sales_current)
    orders_previous = OrderMetrics.calculate_total_orders(sales_comparison)

    # KPI Row - 4 cards
    st.markdown("### Key Performance Indicators")
    kpi_cols = st.columns(4)

    with kpi_cols[0]:
        trend_html = create_trend_indicator(revenue_current, revenue_previous)
        st.markdown(
            create_metric_card(
                "Total Revenue",
                format_currency(revenue_current),
                trend_html
            ),
            unsafe_allow_html=True
        )

    with kpi_cols[1]:
        # For monthly growth, we compare average MoM growth to 0
        avg_mom_pct = avg_mom_growth * 100
        arrow = "↑" if avg_mom_pct >= 0 else "↓"
        color_class = "trend-positive" if avg_mom_pct >= 0 else "trend-negative"
        sign = "+" if avg_mom_pct >= 0 else ""
        trend_html = f'<span class="metric-trend {color_class}">{arrow} {sign}{avg_mom_pct:.2f}%</span>'

        st.markdown(
            create_metric_card(
                "Avg Monthly Growth",
                f"{avg_mom_pct:+.2f}%",
                trend_html
            ),
            unsafe_allow_html=True
        )

    with kpi_cols[2]:
        trend_html = create_trend_indicator(aov_current, aov_previous)
        st.markdown(
            create_metric_card(
                "Average Order Value",
                f"${aov_current:,.2f}",
                trend_html
            ),
            unsafe_allow_html=True
        )

    with kpi_cols[3]:
        trend_html = create_trend_indicator(orders_current, orders_previous)
        st.markdown(
            create_metric_card(
                "Total Orders",
                f"{orders_current:,}",
                trend_html
            ),
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart Grid - 2x2 layout
    st.markdown("### Business Insights")

    # Prepare data for charts
    monthly_revenue_previous = RevenueMetrics.calculate_monthly_revenue(sales_comparison)
    category_revenue = RevenueMetrics.calculate_revenue_by_category(sales_current)
    state_revenue = RevenueMetrics.calculate_revenue_by_state(sales_current)

    # Row 1
    chart_row1 = st.columns(2)

    with chart_row1[0]:
        st.plotly_chart(
            create_revenue_trend_chart(
                monthly_revenue_current,
                monthly_revenue_previous,
                current_year,
                comparison_year
            ),
            use_container_width=True,
            config={'displayModeBar': False}
        )

    with chart_row1[1]:
        st.plotly_chart(
            create_category_chart(category_revenue),
            use_container_width=True,
            config={'displayModeBar': False}
        )

    # Row 2
    chart_row2 = st.columns(2)

    with chart_row2[0]:
        st.plotly_chart(
            create_state_map(state_revenue),
            use_container_width=True,
            config={'displayModeBar': False}
        )

    with chart_row2[1]:
        st.plotly_chart(
            create_satisfaction_scatter(sales_current),
            use_container_width=True,
            config={'displayModeBar': False}
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Bottom Row - 2 cards
    st.markdown("### Customer Experience")
    bottom_cols = st.columns(2)

    # Calculate customer experience metrics
    avg_delivery = CustomerExperienceMetrics.calculate_average_delivery_time(sales_current)
    avg_delivery_prev = CustomerExperienceMetrics.calculate_average_delivery_time(sales_comparison)
    avg_review = CustomerExperienceMetrics.calculate_average_review_score(sales_current)

    with bottom_cols[0]:
        delivery_trend = create_trend_indicator(avg_delivery, avg_delivery_prev)
        st.markdown(f"""
        <div class="bottom-card">
            <div class="bottom-card-label">Average Delivery Time</div>
            <div class="bottom-card-value">{avg_delivery:.1f} days</div>
            {delivery_trend}
        </div>
        """, unsafe_allow_html=True)

    with bottom_cols[1]:
        st.markdown(f"""
        <div class="bottom-card">
            <div class="bottom-card-label">Average Review Score</div>
            <div class="bottom-card-value">{avg_review:.2f} ⭐</div>
            <div class="metric-label">out of 5.00</div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
