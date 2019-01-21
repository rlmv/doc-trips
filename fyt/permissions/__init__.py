from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class PermissionsConfig(AppConfig):
    name = 'fyt.permissions'

    def ready(self):
        from .permissions import groups

        # Initialize groups and permissions after every migration
        @receiver(post_migrate)
        def sync_auth(**kwargs):
            groups.bootstrap()


default_app_config = 'fyt.permissions.PermissionsConfig'
