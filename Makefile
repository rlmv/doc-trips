
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
COVERAGE = $(VENV)/bin/coverage
MANAGE = $(PYTHON) manage.py
DB = fyt/db.sqlite3
DB_BACKUP = fyt/db.sqlite3.bak

.PHONY: docs

all:
	$(MANAGE) runserver

install:
	pyvenv $(VENV)
	$(PIP) install --upgrade -r requirements.txt

deploy:
	git push production master
	heroku run migrate

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

superuser:
	$(MANAGE) setsuperuser d34898x

test:
	$(MANAGE) test --nomigrations

tidy:
	$(VENV)/bin/importanize -v fyt

coverage:
	$(COVERAGE) run --omit "$(VENV)/*" manage.py test --nomigrations
	$(COVERAGE) report -m
	$(COVERAGE) html

clean:
	rm -rf *.pyc
	rm -rf *~

flush:
	$(MANAGE) sqlflush | $(MANAGE) dbshell

docs:
	cd docs && make html

db_from_remote:
	./scripts/load_remote_db.sh

db_fresh: migrate
	$(MANAGE) init_db 2015

backup:
	cp $(DB) $(DB_BACKUP)

restore:
	cp $(DB_BACKUP) $(DB)
