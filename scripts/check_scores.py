from fyt.applications.models import Volunteer
from django.db.models import Count


if __name__ == "__main__":
    qs = Volunteer.objects.leader_or_croo_applications(
        trips_year=2018
    ).annotate(
        Count('scores')
    )

    def print_values():
        print([v.scores__count for v in qs])

    assert qs.filter(scores__count__gt=3).count() == 0
