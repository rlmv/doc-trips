
all:
	python manage.py runserver

install:
	pip install django_cas_sso

clean:
	rm -rf *.pyc
	rm -rf *~
