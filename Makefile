all:
	@echo -e "Nope, try:\n  make test"

test:
	mypy copyaid
	python -m pytest
	@echo Done

.PHONY: all test
