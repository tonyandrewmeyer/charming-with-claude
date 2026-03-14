
# We're using Make as a command runner, so always make (avoids need for .PHONY)
MAKEFLAGS += --always-make

help:  # Display help
	@echo "Usage: make [target]\n\nTargets:"
	@awk -F'#' '/^[a-z0-9-]+:/ { sub(":.*", "", $$1); print " ", $$1, "#", $$2 }' Makefile | column -t -s '#'

all: format lint typecheck  # Run all checks

# Please keep the list below in alphabetical order.

check: format lint typecheck  # Alias for all

clean:  # Remove build artefacts and caches
	rm -rf review.db __pycache__ review_tool/__pycache__ .ruff_cache

dev:  # Install development dependencies
	uv pip install -e ".[dev]" 2>/dev/null || uv pip install -e . && uv pip install ruff ty

format:  # Format the Python code
	ruff format review_tool/

install:  # Install the package
	uv pip install -e .

lint:  # Perform linting checks
	ruff check review_tool/ --fix

typecheck:  # Run type checking
	ty check review_tool/
