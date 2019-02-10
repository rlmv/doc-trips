from fyt.applications.models import Volunteer

def run():
    v = Volunteer.objects.get(applicant__netid='d34898x', trips_year__is_current=True)
    v.leader_supplement.delete()
    v.croo_supplement.delete()
    v.attendee.delete()
    v.first_aid_certifications.all().delete()
    v.delete()
