.ONESHELL:

venv:
	python -m venv .venv

install:
	. .venv/bin/activate || . .venv/Scripts/activate; pip install -r requirements.txt; pip install pytest

run:
	. .venv/bin/activate || . .venv/Scripts/activate; python -m src.cli all

test:
	. .venv/bin/activate || . .venv/Scripts/activate; pytest -q
