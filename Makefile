
all:
	python manage.py runserver

install:
	pip install django_cas_sso

# should later use migrate
sync:
	python manage.py syncdb

clean:
	rm -rf *.pyc
	rm -rf *~
