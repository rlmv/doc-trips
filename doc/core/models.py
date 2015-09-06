from django.db import models

from doc.db.models import DatabaseModel


class Settings(DatabaseModel):
    """
    Contains global configuration values that appear across the site
    """
    trips_cost = models.PositiveSmallIntegerField()
    doc_membership_cost = models.PositiveSmallIntegerField()
    contact_url = models.URLField(help_text='url of trips directorate contact info')

    class Meta:
        unique_together = ['trips_year']
