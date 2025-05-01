from django.urls import path
from .views.views import HolaMundo

urlpatterns = [
    path('', HolaMundo),
]