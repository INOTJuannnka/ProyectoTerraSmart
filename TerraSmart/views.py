from django.shortcuts import render
from django.http import HttpResponse
from TerraSmart.models import Medicion, postMediciones
from django.utils import timezone
from django.contrib import messages

def recomendaciones(request):
    return render(request, 'recomendaciones.html')

def configuracion(request):
    return render(request, 'configuracion.html')

def historial(request):
    return render(request, 'historial.html')

def vista_inicio(request):
    ultimo_registro = Medicion.objects.last()
    return render(request, 'inicio.html', {'ultimo_registro': ultimo_registro})

def vista_historial(request):
    registros = Medicion.objects.all()
    return render(request, 'historial.html', {'registros': registros})

def vista_mediciones(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        nitrogeno = request.POST.get('nitrogeno')
        humedad = request.POST.get('humedad')
        ph = request.POST.get('ph')
        potasio = request.POST.get('potasio')
        fosforo = request.POST.get('fosforo')

    
    try:
        nuevo_registro = postMediciones(
            nitrogeno=nitrogeno,
            fosforo=fosforo,
            potasio=potasio,
            ph=ph,
            humedad=humedad,
            fecha= timezone.now() 
        )
        nuevo_registro.save()
        messages.success(request, 'Registro guardado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al guardar el registro: {e}')
        return render(request, 'mediciones.html')
    return render(request, 'recomendaciones.html')
