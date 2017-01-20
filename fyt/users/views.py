from django.contrib import auth
from vanilla import UpdateView

from fyt.users.models import DartmouthUser
from fyt.utils.forms import crispify


class UpdateEmail(UpdateView):
    model = DartmouthUser
    fields = ['email']
    template_name = 'users/email_form.html'

    def get_object(self):
        return self.request.user

    def get_form(self, **kwargs):
        return crispify(super(UpdateEmail, self).get_form(**kwargs), 'Update')

    def get_success_url(self):
        return self.request.GET[auth.REDIRECT_FIELD_NAME]
