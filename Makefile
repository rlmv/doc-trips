

VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
FAB=$(VENV)/bin/fab
COVERAGE=$(VENV)/bin/coverage

MANAGE=$(PYTHON) doc-trips/manage.py

BEHAVE=$(VENV)/bin/behave
FEATURES=doc-trips/features/

.PHONY: install migrations migrate behave behave_dry rm_emacs_locks test coverage clean

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
	$(MANAGE) test db

rm_emacs_locks:
	@find $(FEATURES) -name ".#*" -delete # remove emacs lock files

behave: rm_emacs_locks
	$(BEHAVE) $(FEATURES)

behave_dry: rm_emacs_locks
	$(BEHAVE) -d $(FEATURES)

coverage:
	$(COVERAGE) run --omit "$(VENV)/*" $(MANAGE) test
	$(COVERAGE) report -m
	$(COVERAGE) html -d coverage

clean:
	rm -rf *.pyc
	rm -rf *~
