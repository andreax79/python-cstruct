SHELL=/bin/bash -e

help:
	@echo - make black ------ Format code
	@echo - make isort ------ Sort imports
	@echo - make clean ------ Clean virtual environment
	@echo - make coverage --- Run tests coverage
	@echo - make docs ------- Make docs
	@echo - make lint ------- Run lint
	@echo - make test ------- Run test
	@echo - make test-32bit - Run test on 32bit architecture
	@echo - make typecheck -- Typecheck
	@echo - make venv ------- Create virtual environment

.PHONY: isort
codespell:
	@codespell -w cstruct tests examples setup.py

.PHONY: isort
isort:
	@isort --profile black cstruct tests examples setup.py

.PHONY: black
black: isort
	@black -S cstruct tests examples setup.py

clean:
	-rm -rf build dist
	-rm -rf *.egg-info
	-rm -rf bin lib share pyvenv.cfg

coverage:
	@pytest --cov --cov-report=term-missing

.PHONY: docs
docs:
	@mkdocs build
	@mkdocs gh-deploy

lint:
	flake8 cstruct tests

test:
	pytest

test-32bit:
	@make -C docker/i386 test

typecheck:
	mypy --strict --no-warn-unused-ignores cstruct

venv:
	python3 -m venv . || python3 -m virtualenv .
	. bin/activate; pip install -Ur requirements.txt
	. bin/activate; pip install -Ur requirements-dev.txt
