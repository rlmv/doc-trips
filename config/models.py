

from django.db import models

class Config(models.Model):

    """ TODO: implement and replace constance with this. """
    
    # set the current trip year for the entire site
    trips_year = models.PostiveIntegerField()
    migration_date = models.DateTimeField()

    
class Global(models.Model):

    # this trips year versions the global. the current trip year is
    # set by Config
    trips_year = models.PositiveIntegerField()

    cost = models.PositiveIntegerField()
    leader_application_available = models.DateTimeField()
    leader_application_due = models.DateTimeField()
    # TODO: ??? are we going to have leader recs?
    # leader_recommendation_due = models.DateTimeField()
    leader_assignment_posted = models.DateTimeField()
    trippee_registration_available = models.DateTimeField()
    trippee_assignment_posted = models.DateTimeField()
    

class Section(models.Model):
    pass

