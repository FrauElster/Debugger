all: test lint type_check

test:
	python -m pytest Debugger

lint:
	python -m flake8 Debugger --max-line-length=100

type_check:
	python -m mypy Debugger --ignore-missing-imports
