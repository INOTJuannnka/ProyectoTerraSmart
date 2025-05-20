from django.apps import AppConfig


class TerrasmartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TerraSmart'

    def ready(self):
        import TerraSmart.signals
