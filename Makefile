all: lint type_check test

test:
	python -m pytest Debugger

lint:
	python -m flake8 Debugger --max-line-length=120

type_check:
	python -m mypy Debugger --ignore-missing-imports
