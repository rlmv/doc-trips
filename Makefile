

VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
FAB=$(VENV)/bin/fab
COVERAGE=$(VENV)/bin/coverage


.PHONY: install migrations migrate test coverage clean

all:
	$(PYTHON) manage.py runserver

install:
	pyvenv $(VENV)
	$(PIP) install -r requirements.txt

migrations:
	$(PYTHON) manage.py makemigrations

migrate:
	$(PYTHON) manage.py migrate

test: 
	$(PYTHON) manage.py test

coverage:
	$(COVERAGE) run --omit "$(VENV)/*" manage.py test
	$(COVERAGE) report -m
	$(COVERAGE) html -d coverage

clean:
	rm -rf *.pyc
	rm -rf *~
