
from django.test import TestCase

from model_mommy import mommy

from test.fixtures import init_trips_year


class CalendarTestCase(TestCase):

    def setUp(self):
        init_trips_year()
    
  
  def test_computes_dates_out_with_one_section(self):
        section = mommy.make('trip.Section')
        section.save()
        self.assertEqual(section.nights_on_trail, calendar.dates_with_trips_camping)
        
