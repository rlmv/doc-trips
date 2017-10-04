INTERPRETER = python3.6
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
COVERAGE = $(VENV)/bin/coverage
MANAGE = $(PYTHON) manage.py

POSTGRES = fyt
POSTGRES_USER = fytuser
POSTGRES_DUMP = latest.dump

all:
	$(MANAGE) runserver

install: venv config.yaml
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements/dev.txt

venv:
	$(INTERPRETER) -m venv $(VENV)

config.yaml:
	cp -nv config.yaml.sample config.yaml

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

bootstrap:
	$(MANAGE) bootstrap

postgres_from_remote:
	heroku pg:backups:capture
	heroku pg:backups:download --output $(POSTGRES_DUMP)
	pg_restore -v --clean --no-acl --no-owner -n public -1 -h localhost \
		-U $(POSTGRES_USER) -d $(POSTGRES) $(POSTGRES_DUMP)
