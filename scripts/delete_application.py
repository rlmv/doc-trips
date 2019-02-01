from fyt.applications.models import Volunteer
v = Volunteer.objects.get(applicant__netid='d34898x')
v.leader_supplement.delete()
v.croo_supplement.delete()
v.attendee.delete()
v.first_aid_certifications.all().delete()
v.delete()
