from fyt.applications.models import Volunteer, LeaderSupplement, CrooSupplement
from fyt.users.models import DartmouthUser


def run():
    trips_year = 2018
    v = Volunteer.objects.create(
        applicant=DartmouthUser.objects.get(netid='d34898x'),
        trips_year_id=trips_year,
        class_year='2014',
        gender='male',
        croo_willing=True,
        leader_willing=True,
        status='PENDING',
        hinman_box='2884',
        tshirt_size='S',
        hometown='Chapel Hill',
        trippee_confidentiality=True,
        in_goodstanding_with_college=True,
        trainings=True)

    LeaderSupplement.objects.create(
        application=v,
        trips_year_id=trips_year)

    CrooSupplement.objects.create(
        application=v,
        trips_year_id=trips_year)
