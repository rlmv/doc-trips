from model_mommy.recipe import Recipe, foreign_key
from fyt.db.models import TripsYear

trips_year = Recipe(
    TripsYear,
    year=2015,
    is_current=True
)
