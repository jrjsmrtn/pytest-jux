# Makefile for pytest-jux development

.PHONY: help install install-dev clean test test-security lint format type-check security-scan security-full

# Default target
help:
	@echo "pytest-jux development commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make install         Install package"
	@echo "  make install-dev     Install with dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run all tests"
	@echo "  make test-security   Run security tests only"
	@echo "  make test-cov        Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            Run ruff linter"
	@echo "  make format          Format code with ruff"
	@echo "  make type-check      Run mypy type checking"
	@echo "  make quality         Run all quality checks"
	@echo ""
	@echo "Security:"
	@echo "  make security-scan   Run security scanners"
	@echo "  make security-test   Run security test suite"
	@echo "  make security-full   Run complete security validation"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           Remove build artifacts"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,security]"
	pre-commit install

# Testing
test:
	pytest

test-security:
	pytest tests/security/ -v --tb=short

test-cov:
	pytest --cov=pytest_jux --cov-report=term-missing --cov-report=html

# Code Quality
lint:
	ruff check .

format:
	ruff format .

type-check:
	mypy pytest_jux

quality: lint type-check
	@echo "✓ All quality checks passed"

# Security
security-scan:
	@echo "Running security scanners..."
	@echo "\n=== pip-audit ==="
	pip-audit || true
	@echo "\n=== Bandit ==="
	bandit -r pytest_jux/ -f screen -ll || true
	@echo "\n=== Safety ==="
	safety check --short-report || true

security-test:
	@echo "Running security test suite..."
	pytest tests/security/ -v --tb=short --cov=pytest_jux --cov-report=term-missing

security-full: security-scan security-test
	@echo "\n✓ Full security validation complete"

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Development workflow
dev: install-dev format lint type-check test
	@echo "✓ Development environment ready"
