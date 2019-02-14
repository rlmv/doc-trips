.PHONY: scripts postgres3

INTERPRETER = python3.6

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
COVERAGE = $(VENV)/bin/coverage
MANAGE = $(PYTHON) manage.py

POSTGRES_DB = fyt
POSTGRES_USER = fytuser
POSTGRES_PASSWORD = password
POSTGRES_DUMP = latest.dump

SCRIPTS = scripts/runtests

all: postgres
	$(MANAGE) runserver

install: venv config.yml scripts
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements/dev.txt

venv:
	$(INTERPRETER) -m venv $(VENV)

config.yml:
	cp -nv config.yml.example config.yml

scripts:
	chmod +x $(SCRIPTS)
	ln -sfv $(SCRIPTS) .

deploy:
	git push production master
	heroku run manage migrate

migrations: postgres
	$(MANAGE) makemigrations

migrate: postgres
	$(MANAGE) migrate

superuser: postgres
	$(MANAGE) setsuperuser d34898x

test: postgres
	$(MANAGE) test --nomigrations --noinput --parallel 4

tidy:
	$(VENV)/bin/importanize -v fyt
	$(VENV)/bin/black -S --exclude migrations/ fyt

format:
	black -S --exclude migrations/ fyt

coverage: postgres
	$(COVERAGE) run --omit "$(VENV)/*" manage.py test --nomigrations
	$(COVERAGE) report -m
	$(COVERAGE) html

clean:
	rm -rf *.pyc
	rm -rf *~
	rm $(POSTGRES_DUMP)

postgres:
	brew services start postgresql@9.6
	#docker-compose up -d postgres

reset_db: postgres
	$(MANAGE) reset_db

bootstrap: postgres
	$(MANAGE) bootstrap

dump_remote:
	heroku pg:backups:capture
	heroku pg:backups:download --output $(POSTGRES_DUMP)

load_dump: postgres
	pg_restore -v --no-acl --no-owner -n public -1 \
		-h localhost -U $(POSTGRES_USER) -d $(POSTGRES_DB) $(POSTGRES_DUMP)

postgres_from_remote: dump_remote reset_db load_dump
