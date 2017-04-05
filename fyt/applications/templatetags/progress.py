from django.template import Library


register = Library()


@register.inclusion_tag('applications/_progress.html')
def scoring_progress(progress):
    return {
        'progress': progress
    }
