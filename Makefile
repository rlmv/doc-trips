

VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
FAB=$(VENV)/bin/fab

all:
	$(PYTHON) manage.py runserver

install:
	pyvenv $(VENV)
	$(PIP) install -r requirements.txt

# should later use migrate
sync:
	$(PYTHON) manage.py syncdb

migrations:
	$(PYTHON) manage.py makemigrations

migrate:
	$(PYTHON) manage.py migrate

test:
	$(PYTHON) manage.py test

clean:
	rm -rf *.pyc
	rm -rf *~
