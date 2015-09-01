This is the DOC First Year trips website.

Dependencies
===========
*django-bootstrap3-datetimepicker Need version>2.2.3. need PR #14 which fixes an early jquery dependency:

### Database forms

Objects for any trip_year may only relate (via ForeignKey, etc.) to objects of the same trips_year. This means we need to be careful to explicitly provide a form class for all objects which have ForeignKeys to other objects, and the form needs to filter field.queryset to only include trips_year. This has been implemented in the get_form_class method of DatabaseMixin, and should just work. Be carefule when setting explicit form_class-es or overriding get_form_class.

