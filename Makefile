

VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
FAB=$(VENV)/bin/fab
COVERAGE=$(VENV)/bin/coverage

MANAGE=$(PYTHON) doc-trips/manage.py


.PHONY: install migrations migrate test coverage clean

all:
	$(MANAGE) runserver

install:
	pyvenv $(VENV)
	$(PIP) install -r requirements.txt

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

test: 
	$(MANAGE) test doc-trips

coverage:
	$(COVERAGE) run --omit "$(VENV)/*" $(MANAGE) test
	$(COVERAGE) report -m
	$(COVERAGE) html -d coverage

clean:
	rm -rf *.pyc
	rm -rf *~
