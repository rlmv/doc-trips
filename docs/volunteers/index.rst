Volunteers
==========

Leader and Croo applications live in :mod:`fyt.applications`

The applications is split into three models related by one-to-one relationships:

:class:`~fyt.applications.models.GeneralApplication` holds shared information (contact info, medical certifications, trip assignments, etc.)

:class:`~fyt.applications.models.LeaderSupplement` holds leader-specific information: availability, trip preferences, and a free-form questionaire.

:class:`~fyt.applications.models.CrooSupplement` holds croo-specific information: Safety Lead and Kitchen Witch availability and a free-form questionaire.


.. todo::
   
   I think it would be semantically better to have *four* models: The three we currently have plus a general ``Volunteer`` model to which we move things like application status and assignments from ``GeneralApplication``. This will require reworking most of the ``applications`` app, but if anyone has the time...


Questionaire Documents
----------------------
TODO: AWS, docx to html conversion


Grading
=======
TODO: 


Reference
---------

.. toctree::
   models
   views
