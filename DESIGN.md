
Packages
========
mezzanine
mezzanine_blocks


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

Private (DYN) (@LOGIN)
=======

* leader 
    - application 



DB design
=========

years - use PARTITION?

basically all data should be versioned? For example, should be able to go back and look at trip types for all previous years.

when migrating, copy information from
* trip types 

Should information from previous years be available to everyone who is logged in? e.g. previous leader pages? Is there anyway to restrict new students from logging in to the leader page? Hmmm...

Auth
====
webAuth
should external users be able to log in? - separate admin?

See crews VV - there needs to be a permission granting portal.


Big Questions
=========
* should crews be integrated into the site? this will add a fair amount of architecture, and probably not much utility since crews don't come into play with logistics. However, if WebAuth is being used exclusively for login there needs to be some way for crews to be given permissions for accessing the database, yes? This could be done by inputing a list of DIDs perhaps.