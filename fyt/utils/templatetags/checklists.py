from django.template import Library, loader

from fyt.incoming.models import sort_by_lastname


register = Library()


def split(a, n):
    """
    http://stackoverflow.com/a/2135920/3818777
    """
    import math

    k, m = math.floor(len(a) / n), len(a) % n
    return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))


@register.simple_tag
def person_checklist(people, phone_numbers=False):
    """
    A checklist of people.

    Each person is a database model with a `name` field or property. If
    including phone numbers, each person must also have a `get_phone_number`
    method.
    """
    people = sort_by_lastname(people)

    if phone_numbers:
        n_cols = 2
        template_name = 'utils/checklists/people_and_phones.html'
    else:
        n_cols = 3
        template_name = 'utils/checklists/people.html'

    return loader.get_template(template_name).render({'columns': split(people, n_cols)})
