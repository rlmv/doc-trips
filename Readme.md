
This is the DOC First Year trips website.

### TODO:

Documentation:
* Installing heroku toolbelt, Postgres, setting up dev database
* How to deploy
* database url schemes - derived from 'get_reference_name' and 'get_app_name'


### User models:

We currently use the default django User model, setting the username field to be the Dartmouth NetId. Ideally we would implement a custom User model, but this will require revamping the CAS login workflow to use get_user_model and make fewer assumptions about accessing user objects.


Testing strategy:
http://www.celerity.com/blog/2013/04/29/how-write-speedy-unit-tests-django-part-1-basics/

Invoke is a fabric predecessor: http://www.pyinvoke.org/
