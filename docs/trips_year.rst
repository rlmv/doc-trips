
The ever-present ``trips_year`` variable
========================================

One of the main design goals of the database rewrite was to make the database self sustaining and eliminate the need to deploy a new codebase every year. To this end, there is one :class:`~fyt.db.models.TripsYear` object for each year of Trips. Every other model in the database (except for ``User`` and a few configuration singletons) has a :attr:`~fyt.db.models.DatabaseModel.trips_year` ForeignKey inherited from :class:`~fyt.db.models.DatabaseModel`.

Since every object has this field, we end up passing around ``trips_year`` values a lot. 

The CBV :class:`~fyt.db.views.TripsYearMixin` handles ``trips_year`` in views. All views which have a ``trips_year`` url kwarg should inherit from it. It pulls the ``trips_year`` from url kwargs, filters querysets, automatically restricts related objects choices in forms to those of the same ``trips_year``, and adds the ``trips_year`` of the view to the template context.

Objects for any ``trips_year`` may only relate (via ForeignKey, etc.) to objects of the same ``trips_year``. Custom forms needs to filter ``field.queryset``. ``TripsYearMixin`` takes care of this by default (see :class:`TripsYearMixin.get_form_class<fyt.db.views.TripsYearMixin.get_form_class>` and :func:`~fyt.db.forms.tripsyear_modelform_factory`), but you need to be careful when using explicit `form_class` values in CBVs.


.. toctree::
   core/models
   core/views
   core/forms
