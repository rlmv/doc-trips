

VENV=fyt-venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

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
