from django.shortcuts import render 
from django.http import HttpResponse
from TerraSmart.models import Medicion, postMediciones
from django.utils import timezone
from django.contrib import messages
import pandas as pd

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
            accion = request.POST.get('accion', 'subir_manual')
            
            # Si es subida manual de datos
            if accion == 'subir_manual':
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
                        fecha=timezone.now()
                    )
                    nuevo_registro.save()
                    messages.success(request, 'Registro guardado exitosamente.')
                    return render(request, 'recomendaciones.html')
                except Exception as e:
                    messages.error(request, f'Error al guardar el registro: {e}')
            
            # Si es subida de archivo
            elif accion == 'subir_archivo':
                print("Entra en subir archivo")
                archivo = request.FILES.get('archivo_mediciones')

                # Verificar si se ha subido un archivo
                if 'archivo_mediciones' in request.FILES:
                    archivo = request.FILES['archivo_mediciones']
                    #Imprimir el archivo subido
                    print("Hola")
                    print(f"Archivo subido: {archivo.name}")
                    try:
                        # Determinar el tipo de archivo y procesarlo
                        if archivo.name.endswith('.csv'):
                            # Procesar CSV
                            df = pd.read_csv(archivo)
                        elif archivo.name.endswith(('.xlsx', '.xls')):
                            # Procesar Excel
                            df = pd.read_excel(archivo)
                        else:
                            messages.error(request, "Formato de archivo no soportado. Use CSV o Excel.")
                        
                        # Normalizar nombres de columnas (convertir a minúsculas para comparación)
                        df.columns = [col.lower().strip() for col in df.columns]
                        
                        # Verificar columnas necesarias
                        columnas_requeridas = ['nitrogeno', 'humedad', 'ph', 'potasio', 'fosforo']
                        
                        # Verificar si todas las columnas requeridas están presentes
                        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                        if columnas_faltantes:
                            messages.error(request, f"El archivo no contiene todas las columnas requeridas. Faltantes: {', '.join(columnas_faltantes)}")
                        
                        # Procesar cada fila y guardar en la base de datos
                        registros_guardados = 0
                        errores = 0
                        
                        for index, fila in df.iterrows():
                            try:
                                # Convertir valores a float y manejar valores nulos
                                nitrogeno_val = float(fila['nitrogeno']) if pd.notna(fila['nitrogeno']) else None
                                humedad_val = float(fila['humedad']) if pd.notna(fila['humedad']) else None
                                ph_val = float(fila['ph']) if pd.notna(fila['ph']) else None
                                potasio_val = float(fila['potasio']) if pd.notna(fila['potasio']) else None
                                fosforo_val = float(fila['fosforo']) if pd.notna(fila['fosforo']) else None
                                
                                # Crear y guardar nuevo registro
                                nuevo_registro = postMediciones(
                                    nitrogeno=nitrogeno_val,
                                    fosforo=fosforo_val,
                                    potasio=potasio_val,
                                    ph=ph_val,
                                    humedad=humedad_val,
                                    fecha=timezone.now()
                                )
                                nuevo_registro.save()
                                registros_guardados += 1
                                
                            except Exception as e:
                                errores += 1
                                print(f"Error en fila {index+1}: {e}")
                        
                        if registros_guardados > 0:
                            mensaje = f"Archivo procesado. {registros_guardados} registros guardados correctamente."
                            if errores > 0:
                                mensaje += f" Se encontraron {errores} errores."
                            messages.success(request, mensaje)
                            return render(request, 'recomendaciones.html')
                        else:
                            messages.error(request, "No se pudo guardar ningún registro del archivo.")
                            
                    except Exception as e:
                        messages.error(request, f"Error al procesar el archivo: {str(e)}")
                else:
                    messages.error(request, "Por favor seleccione un archivo para subir.")
        
        # Si la solicitud no es POST
    return render(request, 'mediciones.html')

def login_view(request):
    return render(request, 'login.html')

def registro_view(request):
    return render(request, 'registro.html')