
from django.conf import settings
from django.db import connections
from sqlalchemy import create_engine

from fyt.db.models import TripsYear
from fyt.transport.models import Route, Stop, Vehicle
from fyt.trips.models import Campsite, TripTemplate, TripType


"""
To build the new database from the old.

Install: sqlalchemy, mysql-connector-python

Login to mysql: 
mysql -uroot

Load the database dump file into a new mysql database, called 'doc':
CREATE DATABASE doc;
USE doc;

Setup a user for django:
CREATE USER django;
GRANT ALL ON fyt.* TO 'django'@'localhost';

Migrate data to local dev database:
manage.py runscript migrate_legacy

Dump data to json:
manage.py dumpdata > doc-trips/db/legacy/db.json

Push to site, load data to production:
manage.py migrate
manage.py loaddata doc-trips/db/legacy/db.json

Boom! Everything should be set.

"""

def setup_connection():

    engine = create_engine('mysql+mysqlconnector://django@localhost/doc')
    return engine.connect()

def trips_year():

    trips_year, created = TripsYear.objects.get_or_create(year=2015, is_current=True)
    return trips_year

def walk_to_lodge_transport_stop():

    stop, created = Stop.objects.get_or_create(trips_year=trips_year(),
                                               name='Walk To Lodge',
                                               address='walk to lodge',
                                               category='INTERNAL')
    return stop

def migrate_campsites():

    connection = setup_connection()
    sql = 'SELECT * FROM ft2014_tripcampsite;'
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
    sql = 'SELECT * FROM ft2014_transportationtype;'

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
    sql = 'SELECT * FROM ft2014_transportationroute;'

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


def migrate_stops():

    connection = setup_connection()
    sql = 'SELECT * FROM ft2014_transportationstop;'

    for row in connection.execute(sql):

        if row['category'] is not None:
            category = row['category'].upper()
        else:
            category = 'BOTH'

        directions = row['directions']
        if directions is None:
            directions = ''

        pickup_time = row['timepickup']
        if pickup_time is not None:
            pickup_time = str(pickup_time)

        dropoff_time = row['timedropoff']
        if dropoff_time is not None:
            dropoff_time = str(dropoff_time)

        stop = Stop(
            id=row['id'],
            name=row['name'],
            address=row['name'],
            directions=directions,
            distance=row['distance'],
            cost=row['cost'],
            pickup_time=pickup_time,
            dropoff_time=dropoff_time,
            route_id=row['primary_transportationroute_id'],
            category=category,
            trips_year=trips_year())

        stop.save()
        print('Added stop ' + str(stop))


def migrate_triptypes():

    connection = setup_connection()
    sql = 'SELECT * FROM ft2014_triptype;'

    for row in connection.execute(sql):

        triptype = TripType(
            id=row['id'],
            name=row['name'],
            leader_description=row['desc_leader'],
            trippee_description=row['desc_trippee'],
            packing_list=row['packing_list'],
            trips_year=trips_year())

        triptype.save()
        print('Added triptype ' + str(triptype))


def migrate_triptemplates():

    connection = setup_connection()
    sql = 'SELECT * FROM ft2014_triptemplate;'

    for row in connection.execute(sql):

        pickup_id = row['pickup_transportationstop_id']
        if pickup_id is None:
            pickup_id = walk_to_lodge_transport_stop().id

        introduction = row['desc_introduction']
        if introduction is None:
            introduction = ''

        day1 = row['desc_day1']
        if day1 is None:
            day1 = ''

        day2 = row['desc_day2']
        if day2 is None:
            day2 = ''

        day3 = row['desc_day3']
        if day3 is None:
            day3 = ''

        conclusion = row['desc_conclusion']
        if conclusion is None:
            conclusion = ''

        revision_notes = row['desc_revision']
        if revision_notes is None:
            revision_notes = ''

        campsite1_id = row['night1_tripcampsite_id']
        campsite2_id = row['night2_tripcampsite_id']

        # template is missing campsite
        if campsite1_id is None and campsite2_id is None and row['name'] == '939':
            campsite = Campsite.objects.get(name='Beaver Brook Shelter')
            print(campsite)
            campsite1_id = campsite.id
            campsite2_id = campsite.id

        triptemplate = TripTemplate(
            id=row['id'],
            name=row['name'],
            triptype_id=row['triptype_id'],
            max_trippees=row['maximum_trippees'],
            non_swimmers_allowed=row['non_swimmers_allowed'],
            dropoff_id=row['dropoff_transportationstop_id'],
            pickup_id=pickup_id,
            return_route_id=row['return_transportationroute_id'],
            campsite1_id=campsite1_id,
            campsite2_id=campsite2_id,
            description_summary=row['desc_summary'],
            description_introduction=introduction,
            description_day1=day1,
            description_day2=day2,
            description_day3=day3,
            description_conclusion=conclusion,
            revision_notes=revision_notes,
            trips_year=trips_year())

        triptemplate.save()
        print('Added triptemplate ' + str(triptemplate))


def migrate():

    migrate_vehicles()
    migrate_routes()
    migrate_stops()

    migrate_campsites()
    migrate_triptypes()
    migrate_triptemplates()
