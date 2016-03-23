Things TODO
===========

Immediate
---------
* Fix the assignment text about Section J placement exams. Make arrival time an editable text box?
* Remove directions from ExternalBus (don't work for cities). Just list coordinates.
* PDF uploads of maps and documents for trip templates
* Show leader itinerary on leader assignment page.
* Refactor internal transport matrix and numbers
* Validate that ``TripTemplates`` cannot use external stops (perhaps with Internal and ExternalStop proxy models?)
* Restrict ``Trip`` route overrides to ``EXTERNAL`` routes.
* Expose raid blog instructions edit field
* Export foodboxes by section? (the spread sheet does have a section column, yes? so perhaps not necessary?)
* Global page of all spreadsheets.
* Use global constants for transport attributes (eg. over_capacity) which are added to the ``Stops`` in GMaps directions for Internal and External stops.
* Put bagel info constants onto a model.
* Automatically select_related in the ``ApplicationManager``
* Urlencode dynamic querystrings
* Add ``/CPR`` to leader med certs? (and migrate existing)
* Generalize high-level admin permssions: ``db:write``
* Explicitly pass ``trips_year`` to ``LeaderSupplementForm``, or make a custom ``ModelForm`` which requires a ``trips_year`` argument.
* Redo url generation to not depend on ``get_model_name`` or whatever it is.

Questions
---------
* Should ``campsite.shelter`` be shown to trippees? Were we going to add more itenerary info to the trippee's trip assignment?

Cosmetic
--------
* Rename/shorten bus assignment fields
* Rename application models
* Rename ``incoming.Settings`` to something nicer
* Rename ``GeneralApplication.assigned_trip`` to ``trip_assignment``. Share assignment form with ``IncomingStudent``?
* Remove ``DartmoutUser.did``?
* Generalize Create/New button
* Shaw overbooked campsites in matrix
* Warn when a trip is over booked on the leader/trippee assignment
* Show warning if transport for a ``ScheduledTrip`` is not scheduled
* Utility singleton model mixin
* Use ``timedelta`` constants for all date intervals.
* Use tables2 for transport matrix?
* Add a note about not being able to delete ``PROTECTED`` objects.
* Show each user's permissions.

Long term
---------
* Validate ``trips_year`` consistancy between related objects
* Preview link to leader and trippee assignment pages.
* Tidy up the webauth app: remove unused config options
* Move Leader and Croo grading to a separate ``grade`` app
* Update all database urls that look like ``db:trip_update`` to ``db:trip:update``
* Use ``model_mommy`` recipes for tests
* Implement more robust .docx parsing for applications, or figure out a base format which always makes pretty HTML.
* Always show the database menu to folks with view permissions.
* Add dropdown search to Incident reports so that the ``caller`` and ``subject`` fields are linked to ``User`` objects
* Skip ``application`` tests if S3 times out.
* Add ``croo_head`` field to Croos
* Cache directions requests (this may be unecessary)
* Use javascript to make prefer/available fields exclusive in a row/implement a better preference field.
* Pass ``trips_year`` to forms instead of using ``TripsYear.objects.current()``. This especially shows up in ``fyt.applications.forms``.


.. todolist::
