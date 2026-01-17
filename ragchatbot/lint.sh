#!/bin/bash

# Lint Python code using ruff and black (check mode)
# Run from the ragchatbot/ directory

set -e

echo "Checking formatting with black..."
uv run black --check .

echo ""
echo "Linting with ruff..."
uv run ruff check .

echo ""
echo "All checks passed!"
