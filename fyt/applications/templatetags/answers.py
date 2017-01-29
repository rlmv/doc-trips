from django.template import Library

register = Library()


@register.inclusion_tag('applications/_display_answers.html')
def display_answers(application):
    """
    Display the answers to dynamic application questions.
    """
    return {
        'answers': application.answer_set.all(),
    }
