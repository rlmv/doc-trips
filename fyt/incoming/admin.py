from django.contrib import admin

from fyt.incoming.models import IncomingStudent, Registration

admin.site.register(IncomingStudent)
admin.site.register(Registration)
