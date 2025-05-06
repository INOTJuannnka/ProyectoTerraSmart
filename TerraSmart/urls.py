from django.urls import path
from TerraSmart import views

urlpatterns = [
    path('', views.vista_inicio, name='inicio'),
    path('mediciones/', views.vista_mediciones, name='mediciones'),
    path('recomendaciones/', views.recomendaciones, name='recomendaciones'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('historial/', views.vista_historial, name='historial'),
]
