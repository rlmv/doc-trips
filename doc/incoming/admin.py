from django.contrib import admin

from doc.incoming.models import IncomingStudent, Registration

admin.site.register(IncomingStudent)
admin.site.register(Registration)
