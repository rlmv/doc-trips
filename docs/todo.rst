Things TODO
===========

External
--------
* Fix django-braces to allow `is_authenticated` be a property.

Upgrades
--------
* Upgrade packages
* Split dependencies into dev/production files
* Use subqueries for get_graders (Django 1.11).

Immediate
---------
* Test filters
* Rewrite display_view logic
* Allow application extensions for specific users.
* Add more filter options
* Fix application filters / Django bug
* Move trip assignment text from model to HTML.
* Prefix ``cache_as`` attribute name with something
* Add a croo waitlist. Needs to support people simultaneously being on the croo
  waitlist and trip leaders, or croo waitlist and leader waitlist, etc
* Add a global page of all spreadsheets.
* Add trainings signup app
* Add checkboxes/formset for batch updating FA/CPR trainings.
* Add spreadsheets for various registration sub-categories
* Remove Section-specific info from `availability` field
* Remove `19s reference from `croo_willing` text
* Fix the assignment text about Section J placement exams. Make arrival time an editable text box?
* Remove directions from ExternalBus (don't work for cities). Just list coordinates.
* Show leader itinerary on leader assignment page.
* Refactor internal transport matrix and numbers
* Validate that ``TripTemplates`` cannot use external stops (perhaps with Internal and ExternalStop proxy models?)
* Restrict ``Trip`` route overrides to ``EXTERNAL`` routes.
* Export foodboxes by section? (the spread sheet does have a section column, yes? so perhaps not necessary?)
* Use global constants for transport attributes (eg. over_capacity) which are added to the ``Stops`` in GMaps directions for Internal and External stops.
* Put bagel info constants onto a model.
* Add ``/CPR`` to leader med certs? (and migrate existing)

Questions
---------
* Should ``campsite.shelter`` be shown to trippees? Were we going to add more itenerary info to the trippee's trip assignment?
* Should trippee registrations also have a 15-minute grace period?

Cosmetic
--------
* Rename/shorten bus assignment fields
* Rename application models
* Rename ``incoming.Settings`` to something nicer
* Rename ``Volunteer.assigned_trip`` to ``trip_assignment``. Share assignment form with ``IncomingStudent``?
* Generalize Create/New button
* Show overbooked campsites in matrix
* Warn when a trip is overbooked on the leader/trippee assignment
* Show warning if transport for a ``ScheduledTrip`` is not scheduled
* Make a utility singleton model mixin
* Use ``timedelta`` constants for all date intervals.
* Use tables2 for transport matrix?
* Add a note about not being able to delete ``PROTECTED`` objects.
* Show each user's permissions.

Long term
---------
* Expose raid blog instructions edit field
* Add PDF uploads of maps and documents for trip templates
* Validate ``trips_year`` consistancy between related objects
* Add a preview link to leader and trippee assignment pages
* Tidy up the webauth app: remove unused config options
* Use ``model_mommy`` recipes for tests
* Always show the database menu to folks with view permissions.
* Add dropdown search to Incident reports so that the ``caller`` and ``subject`` fields are linked to ``User`` objects
* Add ``croo_head`` field to Croos
* Pass ``trips_year`` to forms instead of using ``TripsYear.objects.current()``. This especially shows up in ``fyt.applications.forms``.


.. todolist::
