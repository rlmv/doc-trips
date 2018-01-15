from django.db import models

from fyt.core.models import DatabaseModel


class Croo(DatabaseModel):
    """
    Represents a croo organization.

    Migrates each year.
    """

    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # TODO: croo head?

    def safety_leads(self):
        return self.croo_members.filter(safety_lead=True)

    def non_safety_leads(self):
        return self.croo_members.filter(safety_lead=False)

    def __str__(self):
        return self.name
