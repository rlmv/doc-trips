
This is the DOC First Year trips website.

### TODO:

Documentation:
* Installing heroku toolbelt, Postgres, setting up dev database
* How to deploy
* database url schemes - derived from 'get_reference_name' and 'get_app_name'


### User models:

We currently use the default django User model, setting the username field to be the Dartmouth NetId. Ideally we would implement a custom User model, but this will require revamping the CAS login workflow to use get_user_model and make fewer assumptions about accessing user objects.


### Database forms

Objects for any trip_year may only relate (via ForeignKey, etc.) to objects of the same trips_year. This means we need to be careful to explicitly provide a form class for all objects which have ForeignKeys to other objects, and the form needs to filter field.queryset to only include trips_year. This has been implemented in the get_form_class method of DatabaseMixin, and should just work. Be carefule when setting explicit form_class-es or overriding get_form_class.



Testing strategy:
http://www.celerity.com/blog/2013/04/29/how-write-speedy-unit-tests-django-part-1-basics/

Invoke is a fabric predecessor: http://www.pyinvoke.org/
