


from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


# TODO: move to globals and reuse for trippees
TSHIRT_SIZE_CHOICES = (
    ('S', 'Small'), 
    ('M', 'Medium'), 
    ('L', 'Large'), 
    ('XL', 'Extra large'),
)


class LeaderApplication(models.Model):

    """ Status choices. 

    See https://docs.djangoproject.com/en/dev/ref/models/fields/#choices
    """
    PENDING = 'PEND'
    ACCEPTED = 'ACC'
    WAITLISTED = 'WAIT'
    REJECTED = 'REJ'
    CROO = 'CROO'
    CANCELED = 'CANC'
    DEPRECATED = 'DEP'
    DISQUALIFIED = 'DISQ'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (WAITLISTED, 'Waitlisted'), 
        (REJECTED, 'Rejected'), 
        (CROO, 'Croo'),
        (CANCELED, 'Cancelled'),
        (DEPRECATED, 'Deprecated'),
        (DISQUALIFIED, 'Disqualified'),
    )

    user = models.ForeignKey(User)
    status = models.CharField(max_length=4, choices=STATUS_CHOICES, default=PENDING)
    class_year = models.PositiveIntegerField()
    tshirt_size = models.CharField(max_length=2, choices=TSHIRT_SIZE_CHOICES)
    gender = models.CharField(max_length=255)
    hinman_box = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    offcampus_address = models.CharField(max_length=255)     # TODO: do we need this?

    # TODO: write sections model
    # sections_prefer = models.ManyToManyField('Section')
    # sections_available = models.ManyToManyField('Section')

    # TODO: should application questiosn and answers be hardcoded or dynamic?

    notes = models.CharField(max_length=255, blank=True) # not required in form

    def get_absolute_url(self): 
        """ Get the URL for this object. 
        
        See https://docs.djangoproject.com/en/1.6/ref/models/instances/#django.db.models.Model.get_absolute_url
        """
        from django.core.urlresolvers import reverse
        return reverse('leader:leaderapplication', kwargs={'pk': self.pk}) 
        
    
    
