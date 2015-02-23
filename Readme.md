
This is the DOC First Year trips website.


Deployment
=========
* Install git, heroku toolbelt.
* Trips Directors and Bo have the passwords for Heroku and AWS.
* ...


Timeline
========

#### Immediate:
[x] leader applications, (leader application recommendations), 
[x] custom user model 
[x] basic login, user permissions
[x] permission granting portal
[x] grading leader applications
[x] application styling 
[x] basic trip information - trip types, section configuration

#### Midrange:
[ ] all logistical capabilities: trip, campsite, transport scheduling
[ ] leader portal: trip assignments
[ ] front facing public pages
[ ] trippee registration
[ ] trippee login, view of trip assignments
[ ] food, tshirt checklists
[ ]

#### Pre-trips:
[ ] logistics checklists
[ ] trippee checkin
[ ] safety log
[ ] raid blog

#### 2 year:
[ ] archive view of information from previous years
[ ] longterm stability and year-to-year migration 
[ ]


### User models:

Custom DartmouthUser in doc-trips/users.

### Database forms

Objects for any trip_year may only relate (via ForeignKey, etc.) to objects of the same trips_year. This means we need to be careful to explicitly provide a form class for all objects which have ForeignKeys to other objects, and the form needs to filter field.queryset to only include trips_year. This has been implemented in the get_form_class method of DatabaseMixin, and should just work. Be carefule when setting explicit form_class-es or overriding get_form_class.

### Views

* Do we actually need a ScheduledTrip UpdateView? There are only two fields on the model, and all have to validate unique. It would make sense not to have one.


Testing strategy:
http://www.celerity.com/blog/2013/04/29/how-write-speedy-unit-tests-django-part-1-basics/
