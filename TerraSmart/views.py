from django.shortcuts import render ,redirect
from django.http import HttpResponse, JsonResponse
from TerraSmart.models import Medicion, postMediciones
from django.utils import timezone
from django.contrib import messages
from .firebase_config import db
from django.contrib.auth import login, logout
import pandas as pd
import numpy as np
import joblib
import requests
import time
from threading import Thread
from django.contrib.auth.decorators import login_required
from .thingspeak_monitor import run_monitor
from types import SimpleNamespace



@login_required
def iniciar_monitor(request):
    
    return JsonResponse({'mensaje': 'Monitor iniciado para el usuario actual'})

def recomendaciones(request):
    return render(request, 'recomendaciones.html')

def configuracion(request):
    return render(request, 'configuracion.html')

def historial(request):
    return render(request, 'historial.html')

def vista_inicio(request):
    user_id = request.session.get('usuario')
    ultimo_registro = obtener_n_registros_firestore(user_id, 1)
    ultimo_registro = ultimo_registro[0] if ultimo_registro else None

    print(f"Último registro obtenido: {ultimo_registro}")
    Thread(target=run_monitor, args=(user_id,), daemon=True).start()
    return render(request, 'inicio.html', {'ultimo_registro': ultimo_registro})

def vista_historial(request):
    user = request.session.get('usuario')
    print(f"Obteniendo historial para el usuario: {user}")
    registros = obtener_mediciones_firestore(user)
    return render(request, 'historial.html', {'registros': registros})

def vista_mediciones(request):
    user = request.session.get('usuario')
    if request.method == 'POST':
            accion = request.POST.get('accion', 'subir_manual')
            
            # Si es subida manual de datos
            if accion == 'subir_manual':
                # Obtener datos del formulario
                user = user
                ph = request.POST.get('ph')
                materiaOrganica = request.POST.get('materiaOrganica')
                fosforo = request.POST.get('fosforo')
                azufre = request.POST.get('azufre')
                calcio = request.POST.get('calcio')
                magnesio = request.POST.get('magnesio')
                potasio = request.POST.get('potasio')
                sodio = request.POST.get('sodio')
                hierro = request.POST.get('hierro')
                cobre = request.POST.get('cobre')
                manganeso = request.POST.get('manganeso')
                zinc = request.POST.get('zinc')
                fecha = timezone.now()
                
                
                try:
                    # Guardar en Firestore
                    db.collection("medicion").add({
                        "user": user,
                        "PH": ph,
                        "MateriaOrganica": materiaOrganica,
                        "Fosforo": fosforo,
                        "Azufre": azufre,
                        "Calcio": calcio,
                        "Magnesio": magnesio,
                        "Potasio": potasio,
                        "Sodio": sodio,
                        "Hierro": hierro,
                        "Cobre": cobre,
                        "Manganeso": manganeso,
                        "Zinc": zinc,
                        "fecha": fecha.isoformat()
                    })

                    messages.success(request, 'Registro guardado exitosamente.')
                    return render(request, 'mediciones.html')

                    #return render(request, 'recomendaciones.html')
                except Exception as e:
                    messages.error(request, f'Error al guardar el registro: {e}')
            
            # Si es subida de archivo
            elif accion == 'subir_archivo':
                archivo = request.FILES.get('archivo_mediciones')

                # Verificar si se ha subido un archivo
                if 'archivo_mediciones' in request.FILES:
                    archivo = request.FILES['archivo_mediciones']
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
                        columnas_requeridas = ['ph', 'materiaorganica', 'fosforo', 'azufre', 'calcio', 'magnesio', 'potasio', 'sodio', 'hierro', 'cobre', 'manganeso', 'zinc','fecha']
                        
                        # Verificar si todas las columnas requeridas están presentes
                        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                        if columnas_faltantes:
                            messages.error(request, f"El archivo no contiene todas las columnas requeridas. Faltantes: {', '.join(columnas_faltantes)}")
                        
                        # Procesar cada fila y guardar en la base de datos
                        registros_guardados = 0
                        errores = 0
                        
                        for index, fila in df.iterrows():
                            try:
                                ph_val = float(fila['ph']) if pd.notna(fila['ph']) else None
                                materiaOrganica_val = float(fila['materiaorganica']) if pd.notna(fila['materiaorganica']) else None
                                fosforo_val = float(fila['fosforo']) if pd.notna(fila['fosforo']) else None
                                azufre_val = float(fila['azufre']) if pd.notna(fila['azufre']) else None
                                calcio_val = float(fila['calcio']) if pd.notna(fila['calcio']) else None
                                magnesio_val = float(fila['magnesio']) if pd.notna(fila['magnesio']) else None
                                potasio_val = float(fila['potasio']) if pd.notna(fila['potasio']) else None
                                sodio_val = float(fila['sodio']) if pd.notna(fila['sodio']) else None
                                hierro_val = float(fila['hierro']) if pd.notna(fila['hierro']) else None
                                cobre_val = float(fila['cobre']) if pd.notna(fila['cobre']) else None
                                manganeso_val = float(fila['manganeso']) if pd.notna(fila['manganeso']) else None
                                zinc_val = float(fila['zinc']) if pd.notna(fila['zinc']) else None
                                fecha_str = fila['fecha'] if pd.notna(fila['fecha']) else None
                                               
                                # Crear y guardar nuevo registro
                                db.collection("medicion").add({
                                    "user": user,
                                    "PH": ph_val,
                                    "MateriaOrganica": materiaOrganica_val,
                                    "Fosforo": fosforo_val,
                                    "Azufre": azufre_val,
                                    "Calcio": calcio_val,
                                    "Magnesio": magnesio_val,
                                    "Potasio": potasio_val,
                                    "Sodio": sodio_val,
                                    "Hierro": hierro_val,
                                    "Cobre": cobre_val,
                                    "Manganeso": manganeso_val,
                                    "Zinc": zinc_val,
                                    "fecha": fecha_str
                                })
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
#Función para obtener mediciones desde Firestore
def obtener_mediciones_firestore(user):
    mediciones = []
    print(f"Obteniendo mediciones para el usuario: {user}")
#docs = db.collection("medicion").order_by("fecha", direction="DESCENDING").stream()
    docs = db.collection("medicion").order_by("fecha", direction="DESCENDING").where("user", "==", user).stream()
    for doc in docs:
        data = doc.to_dict()
        mediciones.append(data)
    return mediciones

def obtener_n_registros_firestore(user, n):
    print(f"Obteniendo los últimos {n} registros para el usuario: {user}")
    docs = db.collection("medicion").order_by("fecha", direction="DESCENDING").where("user", "==", user).limit(n).stream()
    registros = []
    for doc in docs:
        data = doc.to_dict()
        registros.append(data)
    return registros

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        users_ref = db.collection("user")
        query = users_ref.where("username", "==", username).where("password", "==", password).get()
        if query:
            # Aquí podrías crear una sesión personalizada si no usas el sistema de auth de Django
            request.session["usuario"] = username
            messages.success(request, "Inicio de sesión exitoso.")
            return redirect("inicio")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, "login.html")

    return render(request, "login.html")

def registro_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "registro.html")

        # Verifica si el usuario ya existe en Firestore
        users_ref = db.collection("user")
        existing = users_ref.where("email", "==", email).get()
        if existing:
            messages.error(request, "El correo ya está registrado.")
            return render(request, "registro.html")

        # Agrega el usuario a Firestore
        users_ref.add({
            "username": username,
            "email": email,
            "password": password1  # En producción, nunca guardes contraseñas en texto plano
        })
        messages.success(request, "Usuario registrado con éxito.")
        return redirect("login")

    return render(request, "registro.html")

def logout_view(request):
    request.session.flush()
    return redirect('login')

model = joblib.load('..\modelo\my_random_forest.joblib')


recomendaciones_tecnicas = {
    'pH agua:suelo 2,5:1,0': {
        'bajo': "Aplicar cal agrícola o dolomita para elevar el pH.",
        'alto': "Aplicar azufre elemental o fertilizantes acidificantes como sulfato de amonio."
    },
    'Materia orgánica (MO) %': {
        'bajo': "Incorporar compost, estiércol bien descompuesto o abonos verdes.",
        'alto': "Monitorear salinidad y evitar acumulación excesiva de nutrientes."
    },
    'Fósforo (P) Bray II mg/kg': {
        'bajo': "Aplicar fosfato monoamónico (MAP), superfosfato triple o rocas fosfóricas.",
        'alto': "Evitar aplicaciones adicionales de fósforo, monitorear fijación en el suelo."
    },
    'Azufre (S) Fosfato monocalcico mg/kg': {
        'bajo': "Aplicar sulfato de amonio, yeso agrícola o azufre elemental.",
        'alto': "Reducir fertilización con azufre; verificar fuentes orgánicas del suelo."
    },
    'Calcio (Ca) intercambiable cmol(+)/kg': {
        'bajo': "Aplicar cal dolomítica o yeso agrícola.",
        'alto': "Evitar aplicaciones de cal o yeso; controlar exceso para prevenir antagonismo con Mg y K."
    },
    'Magnesio (Mg) intercambiable cmol(+)/kg': {
        'bajo': "Aplicar dolomita o fertilizantes como sulfato de magnesio.",
        'alto': "Evitar fuentes ricas en Mg; controlar balance con Ca y K."
    },
    'Potasio (K) intercambiable cmol(+)/kg': {
        'bajo': "Aplicar cloruro de potasio (KCl) o sulfato de potasio (SOP).",
        'alto': "Evitar sobreaplicación; niveles altos pueden interferir con absorción de Mg y Ca."
    },
    'Sodio (Na) intercambiable cmol(+)/kg': {
        'bajo': "Normalmente no requiere corrección.",
        'alto': "Aplicar yeso agrícola y mejorar el drenaje para reducir salinidad."
    },
    'Hierro (Fe) disponible olsen mg/kg': {
        'bajo': "Aplicar quelatos de hierro (Fe-EDDHA) o sulfato ferroso.",
        'alto': "Evitar aplicaciones; exceso puede inhibir absorción de fósforo y manganeso."
    },
    'Cobre (Cu) disponible mg/kg': {
        'bajo': "Aplicar sulfato de cobre (CuSO₄·5H₂O) o quelatos de cobre.",
        'alto': "Evitar fertilizantes cúpricos; monitorear por toxicidad."
    },
    'Manganeso (Mn) disponible Olsen mg/kg': {
        'bajo': "Aplicar sulfato de manganeso o quelatos de Mn.",
        'alto': "Evitar aportes; puede volverse tóxico en suelos ácidos."
    },
    'Zinc (Zn) disponible Olsen mg/kg': {
        'bajo': "Aplicar sulfato de zinc o quelatos de Zn (EDTA-Zn).",
        'alto': "Evitar aplicaciones; niveles altos afectan el fósforo y el hierro."
    }
}
rangos_optimos = {
        'pH agua:suelo 2,5:1,0': (6.0, 7.5),
        'Materia orgánica (MO) %': (2.0, 5.0),
        'Fósforo (P) Bray II mg/kg': (15, 40),
        'Azufre (S) Fosfato monocalcico mg/kg': (10, 30),
        'Calcio (Ca) intercambiable cmol(+)/kg': (5, 10),
        'Magnesio (Mg) intercambiable cmol(+)/kg': (1, 4),
        'Potasio (K) intercambiable cmol(+)/kg': (0.3, 0.7),
        'Sodio (Na) intercambiable cmol(+)/kg': (0.1, 0.4),
        'Hierro (Fe) disponible olsen mg/kg': (5, 10),
        'Cobre (Cu) disponible mg/kg': (0.2, 2.0),
        'Manganeso (Mn) disponible Olsen mg/kg': (10, 50),
        'Zinc (Zn) disponible Olsen mg/kg': (1, 5)
    }

def evaluar_suelo(fila):
    estado = []
    recomendaciones = []

    for var, (min_val, max_val) in rangos_optimos.items():
        valor = fila[var]
        if valor < min_val:
            estado.append(f"{var} : BAJO")
            recomendaciones.append(recomendaciones_tecnicas[var]['bajo'])
        elif valor > max_val:
            estado.append(f"{var} : ALTO")
            recomendaciones.append(recomendaciones_tecnicas[var]['alto'])
        else:
            estado.append(f"{var} : ÓPTIMO")
            recomendaciones.append(recomendaciones_tecnicas[var].get('óptimo', 'Valor en rango adecuado, no se requiere atención o correción.'))

    valores_ordenados = [fila[f] for f in features]
    cultivo_predicho = model.predict(pd.DataFrame([valores_ordenados], columns=features))[0]

    return {
    "cultivo": cultivo_predicho,
    "estado": estado,
    "recomendaciones": recomendaciones
    }

features = [
    'pH agua:suelo 2,5:1,0', 'Materia orgánica (MO) %',
    'Fósforo (P) Bray II mg/kg', 'Azufre (S) Fosfato monocalcico mg/kg',
    'Calcio (Ca) intercambiable cmol(+)/kg', 'Magnesio (Mg) intercambiable cmol(+)/kg',
    'Potasio (K) intercambiable cmol(+)/kg', 'Sodio (Na) intercambiable cmol(+)/kg',
    'Hierro (Fe) disponible olsen mg/kg', 'Cobre (Cu) disponible mg/kg',
    'Manganeso (Mn) disponible Olsen mg/kg', 'Zinc (Zn) disponible Olsen mg/kg'
]

def promediar_variables_medicion(lista_de_dicts):
    campos = [
        'PH', 'MateriaOrganica', 'Fosforo', 'Azufre',
        'Calcio', 'Magnesio', 'Potasio', 'Sodio',
        'Hierro', 'Cobre', 'Manganeso', 'Zinc'
    ]

    acumulados = {campo: 0.0 for campo in campos}
    contador = 0

    for data in lista_de_dicts:
        for campo in campos:
            acumulados[campo] += data.get(campo, 0.0)
        contador += 1

    if contador == 0:
        return None  

    promedios = {campo: acumulados[campo] / contador for campo in campos}
    return SimpleNamespace(**promedios)

def recomendaciones(request):
    n = 10
    user = request.session.get('usuario')
    mediciones = obtener_n_registros_firestore(user, n)
    m = promediar_variables_medicion(mediciones)
    print(mediciones)
    resultados = []

    print(f"Promedio de mediciones: {m}")
    fila = {
        'pH agua:suelo 2,5:1,0': m.PH,
        'Materia orgánica (MO) %': m.MateriaOrganica,
        'Fósforo (P) Bray II mg/kg': m.Fosforo,
        'Azufre (S) Fosfato monocalcico mg/kg': m.Azufre,
        'Calcio (Ca) intercambiable cmol(+)/kg': m.Calcio,
        'Magnesio (Mg) intercambiable cmol(+)/kg': m.Magnesio,
        'Potasio (K) intercambiable cmol(+)/kg': m.Potasio,
        'Sodio (Na) intercambiable cmol(+)/kg': m.Sodio,
        'Hierro (Fe) disponible olsen mg/kg': m.Hierro,
        'Cobre (Cu) disponible mg/kg': m.Cobre,
        'Manganeso (Mn) disponible Olsen mg/kg': m.Manganeso,
        'Zinc (Zn) disponible Olsen mg/kg': m.Zinc
    }

    resultado = evaluar_suelo(fila)
    resultados.append({
        'medicion': m,
        'cultivo': resultado['cultivo'],
        'estado': resultado['estado'],
        'recomendaciones': resultado['recomendaciones']
    })

    return render(request, 'recomendaciones.html', {'resultados': resultados})

