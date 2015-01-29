
from sqlalchemy import create_engine
from django.conf import settings
from django.db import connections

from trips.models import Campsite
from transport.models import Vehicle, Route
from db.models import TripsYear

"""
    'legacy': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'ft2013',
        'HOST': '127.0.0.1',
        'USER': 'django',
    }
"""

"""
install 
------
sqlalchemy
mysql-connector-python
"""


def setup_connection():
    
    engine = create_engine('mysql+mysqlconnector://django@localhost/ft2013')
    return engine.connect()

def trips_year():
    
    trips_year, created = TripsYear.objects.get_or_create(year=2015, is_current=True)
    return trips_year
    
def migrate_campsites():

    connection = setup_connection()
    sql = 'SELECT * FROM ft2013_tripcampsite;'
    for row in connection.execute(sql):
        
        capacity = row['capacity']

        directions = row['directions_to']
        if directions is None:
            directions = ''

        bugout = row['bugout']
        if bugout is None:
            bugout = ''

        secret = row['secret']
        if secret is None:
            secret = ''
            
        campsite = Campsite(id=row['id'], 
                            name=row['name'],
                            capacity=capacity,
                            directions=directions,
                            bugout=bugout,
                            secret=secret, 
                            trips_year=trips_year())
        campsite.save()
        print('Added campsite ' + str(campsite))
        

def migrate_vehicles():
    
    connection = setup_connection()
    sql = 'SELECT * FROM ft2013_transportationtype;'

    for row in connection.execute(sql):
        
        vehicle = Vehicle(
            id=row['id'], 
            name=row['name'],
            capacity=row['passengers'], 
            trips_year=trips_year())
        
        vehicle.save()
        print('Added vehicle ' + str(vehicle))


def migrate_routes():

    connection = setup_connection()
    sql = 'SELECT * FROM ft2013_transportationroute;'

    for row in connection.execute(sql):

        category = row['category'].upper()
        
        route = Route(
            id=row['id'],
            name=row['name'],
            vehicle_id=row['transportationtype_id'],
            category=category, 
            trips_year=trips_year())

        route.save()
        print('Added route ' + str(route))

def migrate():

    #migrate_campsites()

    migrate_vehicles()
    migrate_routes()
