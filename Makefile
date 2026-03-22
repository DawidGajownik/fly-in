PYTHON = python3
PIP = pip
VENV = .venv
BIN = $(VENV)/bin
MAP =

.PHONY: install run debug clean lint lint-strict build

ALLOWED_TARGETS := install run debug clean lint lint-strict build

INVALID_TARGETS := $(filter-out $(ALLOWED_TARGETS),$(MAKECMDGOALS))

ifneq ($(INVALID_TARGETS),)
$(error Usage: python fly_in.py <filename> or: make run MAP=<filename>)
endif

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/$(PIP) install --upgrade pip
	$(BIN)/$(PIP) install flake8 mypy pygame

run:
	$(BIN)/$(PYTHON) fly_in.py $(MAP)

debug:
	$(BIN)/$(PYTHON) -m pdb fly_in.py $(MAP)

clean:
	rm -rf $(VENV)
	rm -rf .mypy_cache
	rm -rf build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	$(BIN)/flake8 . --exclude=$(VENV)
	$(BIN)/mypy . --exclude $(VENV) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
