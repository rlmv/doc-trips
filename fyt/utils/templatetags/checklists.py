from django import template

from fyt.incoming.models import sort_by_lastname

register = template.Library()


def split(a, n):
    """
    http://stackoverflow.com/a/2135920/3818777
    """
    import math
    k, m = math.floor(len(a) / n), len(a) % n
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


@register.inclusion_tag('utils/checklists/people.html')
def person_checklist(people):
    """
    Three-column checklist of people. Can handle any
    database model with a 'name' field or property.
    """
    people = sort_by_lastname(people)
    col1, col2, col3 = split(people, 3)
    return {
        'col1': col1,
        'col2': col2,
        'col3': col3,
    }
