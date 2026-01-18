The @EDA.ipynb contains a notebook with some basic padnas operations on e-commerce data stored in CSV files in @ecommerce_data. Generate code focusing on sales metrics for 2023. In some cases you will have to merge mutliple CSVs together. Start with analysing the esiting file. Improve its structure and documentation in the process.

Existing notebook review plan
- What business metrics are computed.
- What visuals are created.
- What data transformations are performed.
- Any code quality issues or inefficiencies?

## Requirements
1. Notebook structure and documentation.
    - Add proper documentation and markdown cells with clear header and brief explanation for sections.
    - Organize the info into logical sections:
        - Intro and business objectives.
        - Data loading and configuration.
        - Data prep and transformation.
        - Business metrics calculation (revenue, product, geo data, customer experience analysis).
        - Summary of observations.
    - Add a table of contents at the beginning.
    - Include data dictionary explaining key columns and business terms.

2. Code Quality Improvements.
    - Create reusable functions with docsrings.
    - Implement consistent naming and formatting.
    - Create Python files:
        - business_metrics.py containing business metrics calculations only.
        - data_loader.py for loading, processing and cleaning the data.

3. Enhanced visualisations.
    - Improve all plots with:
        - Clear and descriptive titles.
        - Proper axis labels with units.
        - Legends where needed.
        - Appropriate chart types for the data.
        - Include date range in the plot titles or captions.
        - use consistent color and business-oriented color schemes.

4. Configurable Analysis Framework.
The notebook shows the computation of metrics for a specific date range (entire 2023 and comparison with 2022). Refactor the code so that the data is first filtered according to configurable month and year and implement general-purpose metric calculations.

**Deliverables Expected**
- Refactored Jupyter notebook (EDA_refactored.ipynb) with all the improvements.
- Business metrics module (business_metrics.py) with documented functions.
- Requirements file (requirements.txt) listing all dependencies.
- README section explaining how to use the refactored analysis.
