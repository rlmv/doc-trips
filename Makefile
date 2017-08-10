INTERPRETER = python3.6
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
COVERAGE = $(VENV)/bin/coverage
MANAGE = $(PYTHON) manage.py

SQLITE = fyt/db.sqlite3
SQLITE_BACKUP = fyt/db.sqlite3.bak

POSTGRES = fyt
POSTGRES_USER = fytuser
POSTGRES_DUMP = latest.dump

.PHONY: docs venv

all:
	$(MANAGE) runserver

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements/dev.txt

venv:
	$(INTERPRETER) -m venv $(VENV)

deploy:
	git push production master
	heroku run manage migrate

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

superuser:
	$(MANAGE) setsuperuser d34898x

test:
	$(MANAGE) test --nomigrations --noinput --parallel 2

tidy:
	$(VENV)/bin/importanize -v fyt

coverage:
	$(COVERAGE) run --omit "$(VENV)/*" manage.py test --nomigrations
	$(COVERAGE) report -m
	$(COVERAGE) html

clean:
	rm -rf *.pyc
	rm -rf *~
	rm $(POSTGRES_DUMP)

flush:
	$(MANAGE) sqlflush | $(MANAGE) dbshell

docs:
	cd docs && make html

sqlite_from_remote:
	./scripts/load_remote_db.sh

sqlite_fresh: migrate
	$(MANAGE) init_db 2015

sqlite_backup:
	cp $(SQLITE) $(SQLITE_BACKUP)

sqlite_restore:
	cp $(SQLITE_BACKUP) $(SQLITE)

postgres_from_remote:
	heroku pg:backups:capture
	heroku pg:backups:download --output $(POSTGRES_DUMP)
	pg_restore -v --clean --no-acl --no-owner -n public -1 -h localhost \
		-U $(POSTGRES_USER) -d $(POSTGRES) $(POSTGRES_DUMP)
