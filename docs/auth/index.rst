Users and Authentication
========================

All logins to the database are done via `Dartmouth WebAuth`_ which uses the CAS protocol. None of the existing CAS clients for Django worked for me (either no Python 3 support or missing features) so a stripped down and modified version of one (I believe `kstateome/django-cas`_) lives in the :mod:`fyt.webauth` app. It now uses `requests`_ for CAS ticket verification. The code works fine but supports some configuration options which are not needed for our auth and can be tidied up, or moved entirely to a third-party dependency.

A custom user model, :class:`~fyt.users.models.DartmouthUser`, stores information parsed from the CAS responses. 

Since the CAS response does not contain the user's email, :func:`~fyt.dartdm.lookup.lookup_email` tries to pull this from dndprofiles.dartmouth.edu. There does not seem to be a canonical way to lookup an email. Dartmouth IT suggests scraping results from http://lookupdnd.dartmouth.edu/lite if the current system ever fails.

Unfortunately the DND does not contain alumni information and we cannot programmtically find their emails. Therefore when alums log in (e.g. to acces the Raid Blog) :class:`~fyt.users.middleware.UserEmailRequiredMiddleware` prompts them to update their email.


Contents
--------

.. toctree::
   webauth
   users
   dartdm

.. _dartmouth webauth: http://tech.dartmouth.edu/its/services-support/help-yourself/knowledge-base/web-auth-frequently-asked-questions
.. _kstateome/django-cas: https://github.com/kstateome/django-cas
.. _requests: http://python-requests.org

