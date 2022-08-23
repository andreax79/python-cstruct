SHELL=/bin/bash -e

help:
	@echo - make black ------ Format code
	@echo - make clean ------ Clean virtual environment
	@echo - make coverage --- Run tests coverage
	@echo - make docs ------- Make docs
	@echo - make lint ------- Run lint
	@echo - make test ------- Run test
	@echo - make typecheck -- Typecheck
	@echo - make venv ------- Create virtual environment

black:
	black -S cstruct tests examples setup.py

clean:
	-rm -rf build dist
	-rm -rf *.egg-info
	-rm -rf bin lib share pyvenv.cfg

coverage:
	python3 -m coverage run --source=cstruct setup.py test && python3 -m coverage report -m

.PHONY: docs
docs:
	cd docs; $(MAKE) html

lint:
	flake8 cstruct tests

test:
	pytest

typecheck:
	mypy --strict --no-warn-unused-ignores cstruct

venv:
	python3 -m virtualenv .
	. bin/activate; pip install -Ur requirements.txt
	. bin/activate; pip install -Ur requirements-dev.txt
