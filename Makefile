#!make
ifneq (,)
	$(error This Makefile requires GNU Make)
endif

# ─── Variables ────────────────────────────────────────────────────────────────
PROJECT_NAME ?= epub-sorter
PYTHON       ?= python3
PIP          ?= pip

.DEFAULT_GOAL := help

.PHONY: $(shell grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | cut -d":" -f1 | tr "\n" " ")

help: ## Display this help message
	@echo "==================================================================="
	@echo "  $(PROJECT_NAME)"
	@echo "==================================================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}}'
	@echo ""
	@echo "==================================================================="

# ─── Installation ────────────────────────────────────────────────────────────

install: ## Install dependencies
	$(PIP) install -r requirements.txt

install-dev: ## Install dev dependencies
	$(PIP) install -r requirements.txt ruff mypy

install-pre-commit: ## Install and configure git pre-commit hooks
	$(PIP) install --quiet pre-commit
	pre-commit install
	pre-commit autoupdate --bleeding-edge

# ─── Run ─────────────────────────────────────────────────────────────────────

run-gui: ## Run the GUI
	$(PYTHON) gui.py

run-cli: ## Run the CLI
	$(PYTHON) cli.py

# ─── Quality ─────────────────────────────────────────────────────────────────

lint: ## Run ruff linting
	ruff check .

format: ## Run ruff formatter
	ruff format .

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

# ─── Cleanup ─────────────────────────────────────────────────────────────────

clean: ## Clean build artifacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {{}} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache

# ── Quality Gates ──────────────────────────────────────────────────────────────

quality-gate-baseline: ## Record baseline metrics for regression detection
	@python3 scripts/quality_gate.py baseline

quality-gate-verify: ## Verify no regression since baseline
	@python3 scripts/quality_gate.py verify
