from django.shortcuts import render

def inicio(request):
    return render(request, 'inicio.html')

def mediciones(request):
    return render(request, 'mediciones.html')

def recomendaciones(request):
    return render(request, 'recomendaciones.html')

def configuracion(request):
    return render(request, 'configuracion.html')

def historial(request):
    return render(request, 'historial.html')
