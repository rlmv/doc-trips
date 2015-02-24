
This is the DOC First Year trips website.


Deployment
=========
* Install git, heroku toolbelt.
* Trips Directors and Bo have the passwords for the current Heroku and AWS accounts.
* Heroku:
* AWS S3 (for file uploads): 
  1) Create AWS account 
  2) Create an AWS bucket, e.g. 'doc-trips'. Set the environment variable AWS_STORAGE_BUCKET_NAME to be the bucket name.
  3) Create a new user in the AWS IAM manager. Give the user the AmazonS3FullAccess permission. Save the user's security credentials, setting the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables. (Don't use the master user's login credentials!)
* I *highly recommend* setting up a [Heroku dev/staging instance](https://devcenter.heroku.com/articles/multiple-environments), with a development AWS bucket.
* Sentry ?


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
