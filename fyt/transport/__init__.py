from django.apps import AppConfig


class TransportConfig(AppConfig):
    name = 'fyt.transport'

    def ready(self):
        # Register signals
        from . import signals


default_app_config = 'fyt.transport.TransportConfig'
