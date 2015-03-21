 

from django.db import models


class Settings(models.Model):
    """ 
    Contains global configuration values that appear across the site
    trips_cost = models.PositiveIntegerField()

    Singleton object - not tied to a trips year.
    """
    
    trips_cost = models.PositiveSmallIntegerField()
    doc_membership_cost = models.PositiveSmallIntegerField()
    contact_url = models.URLField(help_text='url of trips_directorate contact info')

    SETTINGS_ID = 1

    def save(self, *args, **kwargs):
        self.pk = self.SETTINGS_ID
        super(Settings, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass
        
