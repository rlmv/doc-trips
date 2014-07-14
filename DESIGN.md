

Packages
========
cms:
mezzanine
mezzanine_blocks
something like https://github.com/schneck/django-foreignkeysearch may be useful

admin site:
http://grappelliproject.com/
https://github.com/etianen/django-reversion

dynamic settings: 
https://github.com/comoga/django-constance


* CMS means page should be admin editable
* DYN - page has special dynamic actions 
CMS needs to support image uploads and documents


Public Pages
===========

* about the program (CMS)
* contact (CMS) 
* faq (CMS)
* incoming students (CMS). home page links to faqs.
    - information (CMS) about trips, how to register, links to documents
    - registration form (DYN). Dynamic information (sections for international students, etc.) in the form explanations. Can these be dynamically inserted, or should the page be (CMS)able?
    - calendar (DYN) lists dates of sections this year 
* parents (CMS)
* sustainability (CMS)
* quotes (CMS)
* about the trips (CMS). landing page, links to :
    - a typical trip (CMS)
    - trip types (DYN) generated from current trip types in the DB. links to packing lists.
* leaders home (CMS). links to:
    - leader login (@LOGIN)-> private trip information if the leader is assigned a trip (DYN)
    - application (@LOGIN) -> app page
    - trip information (@LOGIN) if the leader is approved. should not be revealed until OK with admin. date controled? publish button?
    - how to apply. (CMS) contains application dates (open/close) (DYN)
    - calendar (CMS). contains training dates, should link to or embed general trips calendar (DYN).
    - being on a crew (CMS)
    - extra info (CMS)

It would be nice to have a way to add CMS generated pages anywhere on the site.

Private (DYN) (@LOGIN)
=======

* leader login 
    - Application. Form view of the `LeaderApplication` model. (Without customizable questions for the first iteration--this can later be changed.) Must cache answers so that users can return to the page to finish their application--Save/Submit buttons? Available if  `leader_application_available` < date < `application_due`. Submits with `trips_year` specification.
    - Trip Information. If the date > `leader_assignments_posted` trip assignment is available. This shows dates of trip, trip description, trip type, (trippees?) (co-leader?)

main Database:
-------------

Every database url looks like /database/2013/ for some year. Each menu database page has a dropdown menu to view the same page for previous years. The year will be clearly indicated at the top of the page. Most models should have a pre-save hook which adds a trips-year value.

* checklists : large and complex. A full collection of checklists for every day of trips.  - can perhaps be a grappeli admin page with a bunch of tables?

* globals (/admin) : 
    - (use django-constance)
    - `trips_year`. 
    - `migration_date` - date on which `trips_year` will increment to the next year. All application dates, section dates, etc will be incremented by a year. has a hard minimum. Also, a 'migrate now' button.
    - `trips_cost`
    - `leader_application_available`, `leader_application_due`, `leader_recommendation_due`
    - `leader_assignments_posted`
    - `trippee_registrations_available`, `due`
    - `trippee_assignments_posted`
    - sections. Section model. number of sections, dates for arrival, transfer/international/NAD etc.

* trippees - `Trippee`, `TrippeeRegistration` models
    - table of all trippees, unassigned trippees are propogated to the top
    - each trippee page is editable by admin, and provides buttons for assignment to a trip. 
    - trippee registrations are matched with trippees (college provided information). this should be easily done via DIDs
    - blitzlists - generates email lists of sections, etc. (PRIO LOW)
    - find. search for trippees given many criteria. perhaps using a package like https://github.com/esistgut/django-simple-search

* leaders
    - Table of all leader applications, accepted/waitlisted, assignments, grade, and links to change all these. Able to sort by grade, gender. should bubble unassigned leaders and leaders with no status. Able to change status of application.
    - Table of leaders sorted by section/trip
    - blitzlists. many.
    - graders. list of graders, and a portal to grant Users grader permissions. Use dnd interface.
    - grades. feeds leader applications to users with grader permissions. same grader should not get same app twice. should filter out 'deprecated' applications.

* trips
    - landing page w/ table of all trip templates and existence on section. links to scheduled trips.
    - trip templates. "uninstantiated trips".
    - trip types. used in trip templates, and to display on leader and trippee applications.
    - campsites. used in trip templates. contains table of capacities/max outs. for any given day.
    - about numbering page.

* transportation
    - landing page w/ scheduled transportation, ability to add/delete
    - transportation routes. Grant Bus, Local Bus, etc. should show which stops each can service.
    - transportation stops. each stop is linked to a primary route. 
    - somewhere in here we should show pickup/dropoff numbers, 

* statistics
    - tshirts - from leaders and trippee applications.
    - others??


* safety log  (PRIO LOW)
    - incident matrix of all reports. Show all trip templates (or scheduled trips?), and all incidents for those trips. Unscheduled trips should show a '-'.
    - summary of all incidents. 
    - 'new call' link 
    - incident updates should be implemented by extending django's built-in comments.


Permissions:
============
`superuser`
`admin/director` - can view and edit all database. Cannot touch User objects.
`graders`
`leaders` - a User is a leader if she has submitted a `LeaderApplication`
`trippee` - incoming students



DB design
=========

when migrating, copy db tables from
* trip types 

Should the database be editable for past years?

Can we have a test year for experimentation?

Should information from previous years be available to everyone who is logged in? e.g. previous leader pages? Is there any way to restrict new students from logging in to the leader page? Hmmm...

Interface
=========
Don't rely on colors to indicate status - people are colorblind

Auth
====
webAuth
should external users be able to log in? - separate admin?

See crews VV - there needs to be a permission granting portal.

Can we hack the DND to find DIDs from names? Check out http://www.dartmouth.edu/comp/systems/netid.html and http://www.dartmouth.edu/comp/_permacode/current/scripts/netid_lookup.js

Big Questions
=========
* should crews be integrated into the site? this will add a fair amount of architecture, and probably not much utility since crews don't come into play with logistics. However, if WebAuth is being used exclusively for login there needs to be some way for crews to be given permissions for accessing the database, yes? This could be done by inputing a list of DIDs perhaps.

* add blog?

* how is the trippee information imported from the college?

* should trip leader trainings be implemented with templates?

* should long-lasting data (templates) be reversioned/recoverable?


http://www.rdegges.com/the-perfect-django-settings-file/
