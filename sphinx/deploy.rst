Deployment
===========

The site is deployed on `Heroku`_ and uses `AWS S3`_ for file storage. Trips Directors and :ref:`bo` have the passwords for the current Heroku and AWS accounts.

#. Install `git`_, `heroku toolbelt`_.
#. Setting up Heroku:

   #. TODO

#. Setting up AWS S3:

  #. Create AWS account 
  #. Create an AWS bucket, e.g. 'doc-trips'. Set the environment variable AWS_STORAGE_BUCKET_NAME to be the bucket name.
  #. Create a new user in the AWS IAM manager. Give the user the AmazonS3FullAccess permission. Save the user's security credentials, setting the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables. (Don't use the master user's login credentials!)

#. I highly recommend setting up a `Heroku dev/staging instance <https://devcenter.heroku.com/articles/multiple-environments>`_ with a separate AWS bucket for testing, especially if you are going to make deep changes to the codebase.
#. Sentry ?
   #. TODO
#. Google Maps keys. What permissions do you need to set?

.. note::  Most of the time the database runs fine on two Heroku dynos. During high-load periods (when Leader and Croo applications are due, and possibly when Trippee Registrations are due) the site will crash unless you increase the number of dynos. **Be sure to reset the site back to two dynos afterwards, or Trips will have some hefty server bills!**


.. _heroku: http://heroku.com/
.. _heroku toolbelt: https://devcenter.heroku.com/articles/heroku-command
.. _aws s3: http://aws.amazon.com/s3/
.. _git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

