

from .models import TripsYear

class TripsYearAccessor:
    
    @property
    def current(self):
        return TripsYear.objects.filter(is_current=True)[0]
    
trips_year = TripsYearAccessor()
    
