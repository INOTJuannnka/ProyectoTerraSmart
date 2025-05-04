from django.urls import path
from TerraSmart.views.views import vista_inicio


urlpatterns = [
    path('', vista_inicio, name='inicio'),
]