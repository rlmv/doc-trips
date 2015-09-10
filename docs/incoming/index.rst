Incoming Students
=================

Each trippee is represented by two models: :class:`~fyt.incoming.models.IncomingStudent` and :class:`~fyt.incoming.models.Registration`.

``IncomingStudent`` is populated with data provided by the college each year. ``Registration`` is filled out by incoming students and contains trip preferences, availibilty, etc.

``Registrations`` and ``IncomingStudents`` are connected by post_save signals on each model.

.. toctree::
   models
   views




