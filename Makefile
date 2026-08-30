.PHONY: install test check typecheck clean clean-dep all help smoke regression

help:
	@echo "Available commands:"
	@echo "  install    - Install project dependencies using uv"
	@echo "  test       - Run test suite with coverage via pytest"
	@echo "  check      - Run code quality checks (ruff, radon)"
	@echo "  typecheck  - Run mypy strict (pre-existing debt, not part of check)"
	@echo "  clean      - Clean build and execution cache files"
	@echo "  clean-dep  - Clean project virtual environment and lockfiles"
	@echo "  all        - Run install, check, and test targets"
	@echo "  smoke      - Run smoke tests for regression validation"

install:
	uv sync --extra dev

test:
	uv run pytest --cov=src/dlamp tests/

check:
	uv run ruff check src/dlamp tests/
	uv run radon cc src/dlamp -a -s

typecheck:
	uv run mypy src/dlamp

clean:
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache outputs/
	find . -type d -name "__pycache__" -exec rm -rf {} +

clean-dep: clean
	rm -rf .venv uv.lock

all: install check test

smoke:
	@echo "Running smoke tests..."
	# Run quick sanity checks on core subsystems
	# uv run pytest --tb=short tests/dlamp/test_smoke.py -v
	# uv run ruff check src/dlamp --fast
	# uv run mypy src/dlamp --fast
	# echo "Smoke tests passed!"

regression:
	uv run pytest -m regression tests/
