from django.shortcuts import render
from django.http import HttpResponse
from TerraSmart.models import registroSuelo, Medicion
# Create your views here.
#index

def vista_inicio(request):
    ultimo_registro = Medicion.objects.last()
    return render(request, 'inicio.html', {'ultimo_registro': ultimo_registro})

def vista_historial(request):
    registros = Medicion.objects.all()
    return render(request, 'historial.html', {'registros': registros})
