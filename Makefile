INTERPRETER = python3.6
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
COVERAGE = $(VENV)/bin/coverage
MANAGE = $(PYTHON) manage.py

POSTGRES = fyt
POSTGRES_USER = fytuser
POSTGRES_DUMP = latest.dump

SCRIPTS = scripts/runtests

all:
	$(MANAGE) runserver

install: venv config.yml scripts
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements/dev.txt

venv:
	$(INTERPRETER) -m venv $(VENV)

config.yml:
	cp -nv config.yml.example config.yml

.PHONY: scripts

scripts:
	chmod +x $(SCRIPTS)
	ln -sfv $(SCRIPTS) .

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

reset_db:
	$(MANAGE) reset_db

bootstrap:
	$(MANAGE) bootstrap

dump_remote:
	heroku pg:backups:capture
	heroku pg:backups:download --output $(POSTGRES_DUMP)

load_dump:
	pg_restore -v --no-acl --no-owner -n public -1 \
		-h localhost -U $(POSTGRES_USER) -d $(POSTGRES) $(POSTGRES_DUMP)

postgres_from_remote: dump_remote reset_db load_dump
