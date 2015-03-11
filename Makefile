
VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
COVERAGE=$(VENV)/bin/coverage
MANAGE=$(PYTHON) manage.py

.PHONY: install migrations migrate test coverage clean deploy

all:
	$(MANAGE) runserver

install:
	pyvenv $(VENV)
	$(PIP) install -r requirements.txt

deploy: 
	heroku maintenance:on
	git push heroku master
	heroku run migrate
	heroku maintenance:off

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

superuser:
	$(MANAGE) setsuperuser d34898x

test: 
	$(MANAGE) test --nomigrations doc

coverage:
	$(COVERAGE) run --omit "$(VENV)/*" $(MANAGE) test
	$(COVERAGE) report -m
	$(COVERAGE) html -d coverage

clean: 
	rm -rf *.pyc
	rm -rf *~
