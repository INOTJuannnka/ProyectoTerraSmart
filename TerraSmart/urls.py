from django.urls import path
from TerraSmart.views.views import vista_inicio, vista_historial


urlpatterns = [
    path('', vista_inicio, name='inicio'),
    path('historial/', vista_historial, name='historial'),
]