Installation and Deployment
===========================

Local installation
------------------

To run a local development server (assuming a Linux/Unix/OSX environment):

#. Install `Python 3.4`_ and `git`_
#. ``git clone`` the repository and ``cd`` into it
#. Run ``make install``. This sets up a virtual environment and installs all dependencies. 
#. Set up the necessary environment variables. See :ref:`environment_variables`.
#. Run ``./manage.py init_db <this_year>`` to bootstrap the minimal initial data needed for the site to work.
#. Run ``make`` (or just ``./manage.py runserver``) to start the development server. Visit ``localhost:8000/db``. You should be redirected to login via WebAuth.
#. Once you are logged in (and your User info is in the database) run ``./manage.py setsuperuser <your_netid>`` to give yourself superuser privileges and access to the whole database.

Once you have set up authentication with the current Heroku deployment (see :ref:`deploy_to_heroku`, you can run ``make db_from_remote`` to copy all data from the remote database to your local machine.


.. _environment_variables:

Keys and Config
---------------
TODO: keys for Heroku

You only need the AWS keys if you are going to be messing with Leader and Croo applications. Likewise, Google Maps is only used by the transportation app.::
  
    DEBUG="True"
    SECRET_KEY="some secret key"

    AWS_ACCESS_KEY_ID="your key id"
    AWS_SECRET_ACCESS_KEY="your secret key"
    AWS_STORAGE_BUCKET_NAME="a bucket name"

    GOOGLE_MAPS_KEY="your google maps key"
    GOOGLE_MAPS_BROWSER_KEY="your google maps browser key"

When working locally, I put the environment variables in a local ``config.sh`` file that looks like::
    
    export DEBUG="True"
    ...

and run ``source venv/bin/activate && source config.sh`` when I start work.


.. _deploy_to_heroku:

Deploying to Heroku
-------------------

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
.. _python 3.4: https://www.python.org/downloads/

