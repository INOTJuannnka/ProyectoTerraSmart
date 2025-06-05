from django.apps import AppConfig
import threading
import time
import requests


class TerrasmartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TerraSmart'

    def ready(self):
        from . import thingspeak_monitor
        #thread = threading.Thread(target=thingspeak_monitor.run_monitor, daemon=True)
        #thread.start()
        import TerraSmart.signals

