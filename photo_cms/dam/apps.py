from django.apps import AppConfig


class DamConfig(AppConfig):
    name = 'dam'

    def ready(self):
        import dam.signals

