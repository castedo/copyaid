all:
	@echo -e "Nope, try:\n  make test"

test:
	python -m pytest

.PHONY: all test
