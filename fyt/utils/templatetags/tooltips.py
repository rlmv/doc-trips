from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def tooltip_wrap(target, tooltip):
    """
    Wrap a string with a Bootstrap tooltip
    """
    return mark_safe(
        '<span data-toggle="tooltip" data-placement="top" title="{}">'
        '{}'
        '</span>'.format(tooltip, target)
    )


@register.simple_tag
def activate_tooltips():
    return template.Template(
        """
        <script type="text/javascript">
        $(function () {
          $('[data-toggle="tooltip"]').tooltip()
        })
        </script>
        """
    ).render(template.Context({}))
