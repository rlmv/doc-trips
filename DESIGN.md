
Packages
========
mezzanine
mezzanine_blocks
something like https://github.com/schneck/django-foreignkeysearch may be useful


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

* leader 
    - application
    - trip information

main Database:

* checklists : large and complex. A full collection of checklists for every day of trips. 

* globals (/admin) : 
    - trips cost, application dates, assignments, etc.
    - sections. number of sections, dates for arrival, transfer/international/NAD etc.

* safety log  (PRIO LOW)
    - incident matrix of all reports. Show all trip templates (or scheduled trips?), and all incidents for those trips. Unscheduled trips should show a '-'.
    - summary of all incidents. 
    - 'new call' link 
    - incident updates should be implemented by extending django's built-in comments.

* trippees
    - table of all trippees, unassigned trippees are propogated to the top
    - each trippee page is editable by admin, and provides buttons for assignment to a trip. 
    - trippee registrations are matched with trippees (college provided information). this should be easily done via DIDs
    - blitzlists - generates email lists of sections, etc. (PRIO LOW)
    - find. search for trippees given many criteria. perhaps using a package like https://github.com/esistgut/django-simple-search

* leaders
    - table of all leader applications, accepted/waitlisted, assignments, grade, and links to change all these. able to sort by grade, gender. should bubble unassigned leaders and leaders with no status.
    - links to view leaders sorted by trip
    - blitzlists. many.
    - graders. list of graders. need a way to grant grading permissions to graders. use dnd interface.
    - grades. feeds leader applications to users with grader permissions. same grader should not get same app twice. should filter out 'deprecated' apps.

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

DB design
=========

years - use PARTITION?

basically all data should be versioned? For example, should be able to go back and look at trip types for all previous years. 

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

* should trainings have templates?

