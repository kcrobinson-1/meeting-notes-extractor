.PHONY: venv reset-venv install-dev sync-deps compile-deps run smoke lint typecheck test build check clean

PYTHON ?= python3
VENV_DIR := ./.venv
VENV_BIN := ./.venv/bin
SMOKE_URL ?= http://127.0.0.1:8000/extract
SMOKE_REQUEST ?= examples/extract-request.json

$(VENV_BIN)/python:
	$(PYTHON) -m venv $(VENV_DIR)

$(VENV_BIN)/pip-tools: $(VENV_BIN)/python
	$(VENV_BIN)/python -m pip install pip-tools

venv: sync-deps

reset-venv:
	rm -rf $(VENV_DIR)
	$(MAKE) venv

install-dev: sync-deps

sync-deps: $(VENV_BIN)/pip-tools requirements-dev.txt
	$(VENV_BIN)/pip-sync requirements-dev.txt

compile-deps: $(VENV_BIN)/pip-tools requirements-dev.in pyproject.toml
	$(VENV_BIN)/pip-compile --strip-extras --output-file requirements-dev.txt requirements-dev.in

run:
	$(VENV_BIN)/uvicorn app.main:app --reload

smoke: $(VENV_BIN)/python
	curl --silent --show-error --fail \
		-X POST "$(SMOKE_URL)" \
		-H "Content-Type: application/json" \
		--data @"$(SMOKE_REQUEST)" | $(VENV_BIN)/python -m json.tool

lint:
	$(VENV_BIN)/ruff check .
	$(VENV_BIN)/ruff format --check .

typecheck:
	$(VENV_BIN)/mypy app tests

test:
	$(VENV_BIN)/pytest

build:
	$(VENV_BIN)/python -m build

check: lint typecheck test build

clean:
	find . -path "./.venv" -prune -o -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -path "./.venv" -prune -o -type f -name "*.pyc" -exec rm -f {} +
	rm -rf .pytest_cache .ruff_cache build dist ./*.egg-info
