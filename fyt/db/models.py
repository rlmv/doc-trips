from django.db import models

from fyt.db.managers import TripsYearManager


class TripsYear(models.Model):
    """
    Global config object. Each year of trips has one such object.

    All other db objects point to their years' TripsYear.

    TODO: validate that there is only one object with is_current=True
    """
    year = models.PositiveIntegerField(unique=True, primary_key=True)
    # only one current TripsYear at any time
    is_current = models.BooleanField(default=False)

    objects = TripsYearManager()

    def make_next_year(self):
        """
        Instantiate the next ``trips_year``.

        Only works if this the current trips year.
        """
        assert self.is_current

        self.is_current = False
        self.save()

        return TripsYear.objects.create(
            year=self.year + 1, is_current=True
        )

    def __str__(self):
        return str(self.year)


class DatabaseModel(models.Model):
    """
    Abstract base class which manages the ``trips_year``
    property for all models in the trips database.

    TODO: rename this to TripsModel?
    """
    trips_year = models.ForeignKey(
        TripsYear, editable=False, on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def get_absolute_url(self):
        from fyt.db.urlhelpers import reverse_detail_url
        return reverse_detail_url(self)

    @classmethod
    def get_model_name_lower(cls):
        """ Lowercased name of the model. """
        return cls.__name__.lower()

    @classmethod
    def get_app_name(cls):
        """ Return the app name of cls. """
        return cls._meta.app_label

    def obj_kwargs(self):
        return {'trips_year': self.trips_year_id, 'pk': self.pk}
