# Makefile for the Kinz Secure Commerce Hub.

PYTHON ?= python3
VENV   ?= .venv

.PHONY: help setup test lint ruff check clean

help:
	@echo "Kinz Secure Commerce Hub — Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make setup   — create venv and install API requirements"
	@echo "  make test    — run pytest suite"
	@echo "  make lint    — syntax-check all Python files"
	@echo "  make ruff    — run ruff linter"
	@echo "  make check   — run test + ruff (full local CI gate)"
	@echo "  make clean   — remove venv and caches"

setup: $(VENV)/bin/activate
	@echo "✅ Virtualenv ready at $(VENV)"

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r src/api/requirements.txt
	@echo "✅ Installed all dependencies"

test: setup
	$(VENV)/bin/pytest tests/ -v

lint:
	@find src -name "*.py" -print0 | xargs -0 -n1 $(PYTHON) -m py_compile
	@echo "✅ All files compile cleanly"

ruff: setup
	$(VENV)/bin/ruff check src/api/
	@echo "✅ Ruff clean"

check: test ruff
	@echo "✅ All checks passed"

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache
	@echo "✅ Cleaned"
