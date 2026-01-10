SHELL=/bin/bash -e
VERSION := $(shell grep '__version__ = ' cstruct/__init__.py | sed 's/__version__ = "\(.*\)"/\1/')

help:
	@echo - make ruff ------- Format code and sort imports
	@echo - make clean ------ Clean virtual environment
	@echo - make coverage --- Run tests coverage
	@echo - make docs ------- Make docs
	@echo - make lint ------- Run lint
	@echo - make test ------- Run test
	@echo - make test-32bit - Run test on 32bit architecture
	@echo - make typecheck -- Typecheck
	@echo - make venv ------- Create virtual environment

.PHONY: codespell
codespell:
	uv run codespell -w cstruct tests examples

.PHONY: ruff
ruff:
	uv run ruff format cstruct tests examples

.PHONY: clean
clean:
	-rm -rf build dist pyvenv.cfg *.egg-info .venv

.PHONY: coverage
coverage:
	uv run pytest --cov --cov-report=term-missing

.PHONY: docs
docs:
	uv run mkdocs build
	uv run mkdocs gh-deploy

.PHONY: lint
lint:
	uv run ruff check cstruct tests

.PHONY: test
test:
	uv run pytest

.PHONY: test-32bit
test-32bit:
	make -C docker/i386 test

.PHONY: typecheck
typecheck:
	uv run mypy --strict --no-warn-unused-ignores cstruct

.PHONY: tag
tag:
	git tag v${VERSION}

.PHONY: venv
venv:
	uv venv
	uv pip install -e .
	uv pip install -e ".[dev]"
