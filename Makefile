
help:
	@echo - make coverage
	@echo - make tests

coverage:
	python3 -m coverage run --source=cstruct setup.py test && python3 -m coverage report -m

tests:
	python3 setup.py test
