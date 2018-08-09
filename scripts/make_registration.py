from fyt.incoming.models import Registration, IncomingStudent
from fyt.users.models import DartmouthUser

trips_year = 2018
netid = 'd34898x'


def run():
    registration = Registration.objects.create(
        trips_year_id=trips_year,
        user=DartmouthUser.objects.get(netid=netid),
        name='Robert Marchman',
        gender='male',
        email='me@hotmail.com',
        phone='123-345-1345'
    )

    incoming_student = IncomingStudent.objects.create(
        trips_year_id=trips_year,
        netid=netid,
        name='Robert Marchman',
    )
