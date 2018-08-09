from fyt.incoming.models import Registration, IncomingStudent

trips_year = 2018
netid = 'd34898x'

def run():
    IncomingStudent.objects.filter(trips_year_id=trips_year, netid=netid).delete()
    Registration.objects.filter(trips_year_id=trips_year, user__netid=netid).delete()
