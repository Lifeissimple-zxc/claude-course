#!/bin/bash

# Format Python code using black and ruff
# Run from the ragchatbot/ directory

set -e

echo "Formatting Python code with black..."
uv run black .

echo ""
echo "Sorting imports with ruff..."
uv run ruff check --fix --select I .

echo ""
echo "Formatting complete!"
