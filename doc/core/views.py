from vanilla import UpdateView
from django.core.urlresolvers import reverse_lazy

from doc.core.models import Settings
from doc.db.views import CrispyFormMixin
from doc.permissions.views import DatabaseEditPermissionRequired
from doc.utils.forms import crispify


class EditSettings(DatabaseEditPermissionRequired,
                   CrispyFormMixin, UpdateView):
    
    model = Settings
    template_name = 'core/settings.html'
    success_url = reverse_lazy('core:settings')
    
    def get_object(self):
        return self.model.objects.get_or_create()[0]

    def get_form(self, **kwargs):
        form = super(EditSettings, self).get_form(**kwargs)
        return crispify(form)
