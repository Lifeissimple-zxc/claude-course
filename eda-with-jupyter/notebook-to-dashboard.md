Convert @EDA_refactored.ipynb into a professional Streamlist dashboard with this exact layout:

## Layout Structure:
- **Header** Title + date range filter (applies globally)
    - Title: left
    - Date range filter: right
- **KPI Row**: 4 cards (Total Rev, Monthly Growth, Average Order Value, Total Orders)
    - Trend indicators for Total Revenue, Average Order Value and Total Orders.
    - Use red for negative trends and green for the positive ones.

- **Chart Grid** (2x2 layout)
    - Revenue trend line chart:
        - Solid line for the current period.
        - Dashed line for the previous period.
        - Add grid lines for easier reading.
        - Y-axis formatting - shows values as $300k instead of $300,000
    - Top 10 Categories bar chart sorted desc
        - Use blue gradient (lgiht shade for lower values).
        - Format values as $300K and $2M.
    - Revenue by state: US choropleth map Color-coded by revenue amount.
        - Use lavender gradient.
    - Scatter plot showing satisfaction vs delivery time (with a trendline):
        - x axis: delivery time buckets
        - y axis: review score

-- **Bottom Row**: 2 cards
    - Average delivery time with a trend indicator.
    - Review Score:
        - Large number with a star emoji.
        - Subtitle: Average Review Score.

## Key Requirements
- Use plotly for all charts.
- Filter update charts correctly.
- Professional styling with trend arrows / colours.
- DO NOT USE ICONS.
- Use uniform card heights for each row.
- Show two decimal places for each trend indicator.
- Include requirements.txt and a README.md.

If you are adding new dependencies, update requirements.txt and install them. Leave the testing to the user.