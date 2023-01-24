all:
	@echo -e "Nope, try:\n  make test"

test:
	python -m pytest
	mypy qoai.py
	@echo Done

.PHONY: all test
