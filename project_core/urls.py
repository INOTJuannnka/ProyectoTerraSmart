"""
URL configuration for project_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# mi_proyecto/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns  # Importar i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
]

# Usar i18n_patterns para las rutas que se desean manejar con internacionalización
urlpatterns += i18n_patterns(
    path('', include('TerraSmart.urls')),  # Incluye las rutas de TerraSmart dentro de i18n_patterns
)

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
]