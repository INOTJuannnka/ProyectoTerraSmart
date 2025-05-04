from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
#index

def vista_inicio(request):
    return render(request, 'inicio.html')
