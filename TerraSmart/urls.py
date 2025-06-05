from django.urls import path,include
from TerraSmart import views

urlpatterns = [
    path('', views.vista_bienvenida, name='bienvenida'),
    path("verificar-email/", views.verificar_email, name="verificar_email"),
    path('instrucciones/', views.vista_instrucciones, name='instrucciones'),
    path('inicio/', views.vista_inicio, name='inicio'),
    path('mediciones/', views.vista_mediciones, name='mediciones'),
    path('recomendaciones/', views.recomendaciones, name='recomendaciones'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('historial/', views.vista_historial, name='historial'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
]
