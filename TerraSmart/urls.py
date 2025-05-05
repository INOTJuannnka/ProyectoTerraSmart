from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('mediciones/', views.mediciones, name='mediciones'),
    path('recomendaciones/', views.recomendaciones, name='recomendaciones'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('historial/', views.historial, name='historial'),
]
