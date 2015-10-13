Things TODO
===========

Immediate
---------
* Fix the assignment text about Section J placement exams. Make arrival time an editable text box?
* Update dietary/medical info fields for leaders

  #. Food allergens and reactions
  #. Other dietary restrictions?
  #. Other medical conditions, including other non-food allergies
  #. Do you carry an epipen?
  #. Do you have any other needs?

* Delete all medical info when migrating to next ``trips_year``
* Add hinman box to IncomingStudent + a way to upload a spreadsheet of #s
* Remove directions from ExternalBus (don't work for cities). Just list coordinates.
* Link to ExternalBus packets from external bus page
* Filter Qualifications by TripsYear in ``CrooGradeForm``
* Move driver certs from croo .docx to ``CrooSupplement``? (check with Peety)
* PDF uploads of maps and documents for trip templates
* Add a ``water_source`` (text) and ``bear_bag`` (boolean) field to ``Campsite``. Show them in leader packets.
* Add a ``type`` field ("tarp", "shelter", "cabin") to ``Campsite``
* Change ``non_swimmers`` to ``swimtest_required`` on ``TripTemplate``. If required, show "You will take  the swimtest on the first day of your trip" on the trippee's assignment page.
* Show leader itinerary on leader assignment page.
* Refactor and optimize ``Campsite`` matrix
* Refactor internal transport matrix and numbers
* Migrate ``YesNo`` field to use ``BooleanField`` backend.
* Validate that ``TripTemplates`` cannot use external stops (perhaps with Internal and ExternalStop proxy models?)
* Restrict ``Trip`` route overrides to ``EXTERNAL`` routes.
* Expose raid blog instructions edit field
* Export foodboxes by section? (the spread sheet does have a section column, yes? so perhaps not necessary?)
* Global page of all spreadsheets.
* Use global constants for transport attributes (eg. over_capacity) which are added to the ``Stops`` in GMaps directions for Internal and External stops.
* Put bagel info constants onto a model.
* Automatically select_related in the ``ApplicationManager``
* Urlencode dynamic querystrings
* Rename ``GeneralApplication.assigned_trip`` to ``trip_assignment``. Share assignment form with ``IncomingStudent``?
* Add ``/CPR`` to leader med certs? (and migrate existing)
* Generalize high-level admin permssions: ``db:write``
* Use Coalesce (Django 1.8) to fix ordering of Volunteer table.
* Explicitly pass ``trips_year`` to ``LeaderSupplementForm``, or make a custom ``ModelForm`` which requires a ``trips_year`` argument.
* Redo url generation to not depend on ``get_model_name`` or whatever it is.


Cosmetic
--------
* Rename/shorten bus assignment fields
* Rename application models
* Rename ``incoming.Settings`` to something nicer
* Remove ``DartmoutUser.did``?
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


.. todolist::

