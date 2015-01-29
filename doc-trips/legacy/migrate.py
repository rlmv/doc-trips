

from django.conf import settings
from django.db import connections

from trips.models import Campsite

"""
    'legacy': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'ft2013',
        'HOST': '127.0.0.1',
        'USER': 'django',
    }
"""

def setup_cursor():
    return connections['legacy'].cursor()

def import_campsites():

    cursor = setup_cursor()
    sql = 'SELECT id, name, capacity, directions_to, bugout, secret FROM ft2013_tripcampsite;'
    cursor.execute(sql)
    for row in cursor.fetchall():

        campsite = Campsite(id=row[0], 
                            name=row[1],
                            capacity=row[2],
                            directions=row[3],
                            bugout=row[4],
                            secret=row[5])
        campsite.save()
        
    
def migrate():

    import_campsites()
