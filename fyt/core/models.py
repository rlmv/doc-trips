from django.db import models
from django.urls import reverse

from fyt.core.managers import TripsYearManager


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

        return TripsYear.objects.create(year=self.year + 1, is_current=True)

    def __str__(self):
        return str(self.year)


class DatabaseModel(models.Model):
    """
    Abstract base class which manages the ``trips_year``
    property for all models in the trips database.

    TODO: rename this to TripsModel?
    """

    trips_year = models.ForeignKey(TripsYear, editable=False, on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def get_absolute_url(self):
        return self.detail_url()

    def detail_url(self):
        return reverse(
            'core:{}:detail'.format(self.model_name_lower()), kwargs=self.obj_kwargs()
        )

    def update_url(self):
        return reverse(
            'core:{}:update'.format(self.model_name_lower()), kwargs=self.obj_kwargs()
        )

    def delete_url(self):
        return reverse(
            'core:{}:delete'.format(self.model_name_lower()), kwargs=self.obj_kwargs()
        )

    def index_url(self):
        return reverse(
            'core:{}:index'.format(self.model_name_lower()),
            kwargs={'trips_year': self.trips_year_id},
        )

    @classmethod
    def create_url(cls, trips_year):
        return reverse(
            'core:{}:create'.format(cls.model_name_lower()),
            kwargs={'trips_year': trips_year.pk},
        )

    @classmethod
    def model_name_lower(cls):
        """ Lowercased name of the model. """
        return cls._meta.concrete_model._meta.model_name

    def obj_kwargs(self):
        return {'trips_year': self.trips_year_id, 'pk': self.pk}
