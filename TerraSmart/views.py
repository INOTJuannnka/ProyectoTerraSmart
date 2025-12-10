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
from django.shortcuts import render, redirect
from django.http import HttpResponse
import time
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from .models import Medicion
from .firebase_config import db
from django.contrib.auth.decorators import login_required
import matplotlib.pyplot as plt
import numpy as np
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from .utils import generate_token
from django.shortcuts import redirect
from .utils import verify_token
import os
import logging

from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from allauth.account.forms import ResetPasswordKeyForm


def recomendaciones(request):
    return render(request, 'recomendaciones.html')

def configuracion(request):
    return render(request, 'configuracion.html')

def historial(request):
    return render(request, 'historial.html')

def vista_inicio(request):
    if "usuario" not in request.session:
        return redirect("login")
    else:
        user_id = request.session.get('usuario')
        mediciones = obtener_mediciones_firestore(user_id)
        Thread(target=run_monitor, args=(user_id,), daemon=True).start()
        if not mediciones:
            return render(request, 'inicio.html', {'img_data_dict': {}, 'mediciones': []})

        # Convertir a DataFrame para agrupar por semana
        df = pd.DataFrame(mediciones)
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce', infer_datetime_format=True)
        df = df.dropna(subset=['fecha'])

        # Lista de campos numéricos
        campos = [
            'HumedadSuelo', 'Luz', 'Temperatura', 'HumedadAire','Nitrogeno', 'Fosforo', 'Potasio', 'PH'
        ]

        # Convertir columnas numéricas a float (ignorar errores)
        for campo in campos:
            if campo in df.columns:
                df[campo] = pd.to_numeric(df[campo], errors='coerce')

        # Usaremos la serie completa (no solo resample semanal) para mostrar todos los puntos
        df.set_index('fecha', inplace=True)
        # Asegurarse de que el índice esté ordenado de manera ascendente
        df.sort_index(inplace=True)

        # Loguear información útil para depuración
        try:
            logging.getLogger(__name__).info(f"Mediciones totales: {len(df)}; rango: {df.index.min()} - {df.index.max()}")
        except Exception:
            logging.getLogger(__name__).exception("Error logging df range")

        img_data_dict = {}

        for campo in campos:
            # Verificar que el campo exista en el DataFrame
            if campo not in df.columns:
                continue
            # Tomar la serie completa del campo y eliminar NaN
            serie = df[campo].dropna()
            if serie.empty:
                continue
            valores = serie.tolist()
            fechas = serie.index.strftime('%Y-%m-%d %H:%M:%S').tolist()

            fig, ax = plt.subplots(figsize=(8, 4))
            # Usar objetos datetime como eje x para que matplotlib maneje fechas
            x = serie.index
            y = valores
            ax.plot(x, y, marker='o', linestyle='-', color='g', label=campo, markersize=4, linewidth=1)
            try:
                ax.set_ylim(min(y) - 1, max(y) + 1)
            except Exception:
                pass
            ax.set(xlabel='Fecha', ylabel=campo, title=f'Evolución de {campo}')
            ax.grid(True, axis='y')

            # Mostrar etiquetas de fecha muestreadas para evitar sobreposición
            num_points = len(x)
            max_labels = 6
            step = max(1, num_points // max_labels)
            ticks = x[::step]
            ticklabels = [d.strftime('%Y-%m-%d') for d in ticks]
            ax.set_xticks(ticks)
            ax.set_xticklabels(ticklabels, rotation=45, ha='right')

            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png')
            buf.seek(0)
            img_data_dict[campo] = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()
            plt.close(fig)

            # Obtener el último registro (más reciente)
        ultimo_registro =  obtener_n_registros_firestore(user_id, 1)
        ultimo_registro = ultimo_registro[0] if ultimo_registro else None
        if not ultimo_registro:
            ultimo_registro = {
                'HumedadSuelo': None, 'Luz': None, 'Temperatura': None, 'HumedadAire': None,
                'Nitrogeno': None, 'Fosforo': None, 'Potasio': None, 'PH': None,
                'fecha': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        return render(request,'inicio.html',{
                'img_data_dict': img_data_dict,
                'mediciones': mediciones,
                'ultimo_registro': ultimo_registro
            }
        )

def vista_historial(request):
    user = request.session.get('usuario')
    print(f"Obteniendo historial para el usuario: {user}")
    registros = obtener_mediciones_firestore(user)
    return render(request, 'historial.html', {'registros': registros})

def vista_mediciones(request):
    if "usuario" not in request.session:
        return redirect("login")

    user = request.session.get('usuario')

    if request.method == 'POST':
        accion = request.POST.get('accion', 'subir_manual')

        # Si es subida manual de datos
        if accion == 'subir_manual':
            # Obtener datos del formulario
            HumedadSuelo = float(request.POST.get('HumedadSuelo', 0))
            Luz = float(request.POST.get('Luz', 0))
            Temperatura = float(request.POST.get('Temperatura', 0))
            HumedadAire = float(request.POST.get('HumedadAire', 0))
            Nitrogeno = float(request.POST.get('Nitrogeno', 0))
            Fosforo = float(request.POST.get('Fosforo', 0))
            Potasio = float(request.POST.get('Potasio', 0))
            ph = float(request.POST.get('ph', 0))
            fecha = timezone.now()

            try:
                # Guardar en Firestore
                db.collection("medicion").add({
                    "user": user,
                    "HumedadSuelo": HumedadSuelo,
                    "Luz": Luz,
                    "Temperatura": Temperatura,
                    "HumedadAire": HumedadAire,
                    "Nitrogeno": Nitrogeno,
                    "Fosforo": Fosforo,
                    "Potasio": Potasio,
                    "PH": ph,
                    "fecha": fecha.isoformat()
                })

                messages.success(request, 'Registro guardado exitosamente.')
                return render(request, 'mediciones.html')

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
                    columnas_requeridas = ['humedadsuelo', 'luz', 'temperatura', 'humedadaire', 'nitrogeno', 'fosforo', 'potasio', 'ph','fecha']

                    # Verificar si todas las columnas requeridas están presentes
                    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
                    if columnas_faltantes:
                        messages.error(request, f"El archivo no contiene todas las columnas requeridas. Faltantes: {', '.join(columnas_faltantes)}")

                    # Procesar cada fila y guardar en la base de datos
                    registros_guardados = 0
                    errores = 0

                    for index, fila in df.iterrows():
                        try:
                            ph_val = float(fila['HumedadSuelo']) if pd.notna(fila['HumedadSuelo']) else None
                            materiaOrganica_val = float(fila['luz']) if pd.notna(fila['luz']) else None
                            fosforo_val = float(fila['temperatura']) if pd.notna(fila['temperatura']) else None
                            azufre_val = float(fila['humedadaire']) if pd.notna(fila['humedadaire']) else None
                            calcio_val = float(fila['nitrogeno']) if pd.notna(fila['nitrogeno']) else None
                            magnesio_val = float(fila['fosforo']) if pd.notna(fila['fosforo']) else None
                            potasio_val = float(fila['potasio']) if pd.notna(fila['potasio']) else None
                            ph = float(fila['ph']) if pd.notna(fila['ph']) else None
                            fecha_str = fila['fecha'] if pd.notna(fila['fecha']) else None

                            # Crear y guardar nuevo registro
                            db.collection("medicion").add({
                                "user": user,
                                "HumedadSuelo": ph_val,
                                "Luz": materiaOrganica_val,
                                "Temperatura": fosforo_val,
                                "HumedadAire": azufre_val,
                                "Nitrogeno": calcio_val,
                                "Fosforo": magnesio_val,
                                "Potasio": potasio_val,
                                "PH": ph,
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

    # Si la solicitud no es POST -> preparar datos para la plantilla
    # Obtener todas las mediciones del usuario
    mediciones_raw = obtener_mediciones_firestore(user)

    # Normalizar y transformar mediciones para la plantilla
    mediciones = []
    for m in mediciones_raw:
        # fecha puede ser datetime o string ISO
        fecha = m.get('fecha')
        try:
            fecha_dt = pd.to_datetime(fecha, errors='coerce')
        except Exception:
            fecha_dt = None

        # Normalizar nombres (intentar varias claves)
        temperatura = m.get('Temperatura') or m.get('temperatura') or m.get('temp')
        humedad = m.get('Humedad') or m.get('humedad') or m.get('HumedadAire') or m.get('humedadaire')
        humedad_suelo = m.get('HumedadSuelo') or m.get('humedad_suelo')

        # Convertir a float si es posible
        def to_float(v):
            try:
                return float(v)
            except Exception:
                return None

        temperatura = to_float(temperatura)
        humedad = to_float(humedad)
        humedad_suelo = to_float(humedad_suelo)

        # Determinar si la medición es "óptima" para café (reglas simples)
        es_optimo = False
        if temperatura is not None and humedad_suelo is not None:
            # Rangos de referencia para café arábica (aprox.)
            if 18.0 <= temperatura <= 24.0 and 40.0 <= humedad_suelo <= 70.0:
                es_optimo = True

        mediciones.append({
            'fecha': fecha_dt,
            'temperatura': temperatura,
            'humedad': humedad,
            'humedad_suelo': humedad_suelo,
            'es_optimo': es_optimo
        })

    # Calcular última actualización (la más reciente con fecha válida)
    fecha_vals = [m['fecha'] for m in mediciones if m['fecha'] is not None]
    if fecha_vals:
        ultima_fecha = max(fecha_vals)
        # diferencia respecto a ahora
        ahora = timezone.now()
        # convertir ultima_fecha a timezone-naive or aware comparable a ahora
        try:
            # pandas Timestamp may be tz-aware or naive
            if hasattr(ultima_fecha, 'tz_convert'):
                ultima_fecha_local = pd.to_datetime(ultima_fecha).to_pydatetime()
            else:
                ultima_fecha_local = ultima_fecha.to_pydatetime() if hasattr(ultima_fecha, 'to_pydatetime') else ultima_fecha
        except Exception:
            try:
                ultima_fecha_local = pd.to_datetime(ultima_fecha).to_pydatetime()
            except Exception:
                ultima_fecha_local = ultima_fecha

        # Compute human readable delta (Spanish)
        delta = ahora - ultima_fecha_local
        seconds = int(delta.total_seconds())
        if seconds < 60:
            ultima_actualizacion = f'Hace {seconds} seg'
        elif seconds < 3600:
            minutos = seconds // 60
            ultima_actualizacion = f'Hace {minutos} min'
        elif seconds < 86400:
            horas = seconds // 3600
            ultima_actualizacion = f'Hace {horas} h'
        else:
            dias = seconds // 86400
            ultima_actualizacion = f'Hace {dias} días'
    else:
        ultima_actualizacion = 'Sin registros'

    # Calcular promedio del día para generar recomendaciones enfocadas al cultivo de café
    recomendaciones = []
    try:
        if fecha_vals:
            df = pd.DataFrame(mediciones)
            df = df.dropna(subset=['fecha'])
            df['fecha'] = pd.to_datetime(df['fecha'])
            hoy = timezone.now().date()
            df_today = df[df['fecha'].dt.date == hoy]
            if not df_today.empty:
                avg_temp = df_today['temperatura'].dropna().astype(float).mean() if 'temperatura' in df_today else None
                avg_hum = df_today['humedad'].dropna().astype(float).mean() if 'humedad' in df_today else None
                avg_hum_suelo = df_today['humedad_suelo'].dropna().astype(float).mean() if 'humedad_suelo' in df_today else None

                # Reglas simples para recomendaciones para café
                if avg_temp is not None:
                    if avg_temp < 18:
                        recomendaciones.append(f'Temperatura media hoy {avg_temp:.1f}°C: Considera proteger plantas del frío o utilizar coberturas.')
                    elif avg_temp > 24:
                        recomendaciones.append(f'Temperatura media hoy {avg_temp:.1f}°C: Podría ser alta; revisar riego y sombra parcial para evitar estrés térmico.')
                    else:
                        recomendaciones.append(f'Temperatura media hoy {avg_temp:.1f}°C: Adecuada para café.')

                if avg_hum_suelo is not None:
                    if avg_hum_suelo < 40:
                        recomendaciones.append(f'Humedad del suelo media hoy {avg_hum_suelo:.1f}%: Suelo seco; aumentar riego y evaluar sistema de riego por goteo.')
                    elif avg_hum_suelo > 70:
                        recomendaciones.append(f'Humedad del suelo media hoy {avg_hum_suelo:.1f}%: Suelo muy húmedo; revisar drenaje para prevenir enfermedades radiculares.')
                    else:
                        recomendaciones.append(f'Humedad del suelo media hoy {avg_hum_suelo:.1f}%: Dentro del rango adecuado para café.')

                if avg_hum is not None:
                    if avg_hum < 50:
                        recomendaciones.append(f'Humedad relativa media hoy {avg_hum:.1f}%: Ambiente seco; considerar sombras o manejo de microclima.')
                    elif avg_hum > 85:
                        recomendaciones.append(f'Humedad relativa media hoy {avg_hum:.1f}%: Muy alta; vigilar enfermedades foliares.')
                    else:
                        recomendaciones.append(f'Humedad relativa media hoy {avg_hum:.1f}%: Adecuada para cultivo de café.')
            else:
                recomendaciones.append('No hay mediciones de hoy para calcular recomendaciones.')
        else:
            recomendaciones.append('No hay registros para generar recomendaciones.')
    except Exception:
        logging.getLogger(__name__).exception('Error calculando recomendaciones diarias')
        recomendaciones.append('Error al calcular recomendaciones.')

    return render(request, 'mediciones.html', {
        'mediciones': mediciones,
        'ultima_actualizacion': ultima_actualizacion,
        'recomendaciones': recomendaciones
    })
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
        query = users_ref.where("username", "==", username).get()
        if not query:
            messages.error(request, "Usuario no encontrado.")
            return render(request, "login.html")

        user_data = query[0].to_dict()
        hashed_password = user_data.get("password")

        if check_password(password, hashed_password):
            # Login exitoso
            request.session["usuario"] = username
            messages.success(request, "Inicio de sesión exitoso.", extra_tags="login_exitoso")
            # Redirige a la página principal o dashboard
            return redirect("inicio")
        else:
            messages.error(request, "Contraseña incorrecta.")
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
        users_ref = db.collection("user")
        existing = users_ref.where("email", "==", email).get()
        if existing:
            messages.error(request, "El correo ya está registrado.",extra_tags="registro_exitoso")
            return render(request, "registro.html")

        # Crear usuario sin verificar
        users_ref.add({
            "username": username,
            "email": email,
            "password": make_password(password1),
            "email_verified": False
        })

        token = generate_token(email)
        verify_url = request.build_absolute_uri(reverse("verificar_email") + f"?token={token}")

        send_mail(
            "Confirma tu correo electrónico",
            f"Hola {username}, haz clic en este enlace para confirmar tu correo:\n\n{verify_url}",
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )

        messages.success(request, "Registro exitoso. Verifica tu correo para activar tu cuenta.")
        return redirect("login")

    return render(request, "registro.html")

def verificar_email(request):
    token = request.GET.get("token")
    email = verify_token(token)

    if email:
        # Buscar y actualizar el campo email_verified en Firestore
        users_ref = db.collection("user")
        user_docs = users_ref.where("email", "==", email).get()
        for doc in user_docs:
            users_ref.document(doc.id).update({"email_verified": True})
        messages.success(request, "Correo verificado correctamente. Ya puedes iniciar sesión.")
        return redirect("login")
    else:
        messages.error(request, "El enlace de verificación es inválido o ha expirado.")
        return redirect("registro")

def logout_view(request):
    request.session.flush()
    return redirect('login')

_model = None

def get_model():
    """Lazily load the ML model. Returns None if the model or sklearn aren't available.

    This avoids importing sklearn at module import time (which breaks management commands
    and tests when scikit-learn isn't installed).
    """
    global _model
    if _model is not None:
        return _model

    try:
        # Build a path relative to this file: ../modelo/my_random_forest.joblib
        base_dir = os.path.dirname(__file__)
        model_path = os.path.normpath(os.path.join(base_dir, '..', 'modelo', 'my_random_forest.joblib'))
        if os.path.exists(model_path):
            _model = joblib.load(model_path)
            return _model
        else:
            logging.getLogger(__name__).warning("ML model not found at %s", model_path)
            return None
    except Exception:
        logging.getLogger(__name__).exception("Failed to load ML model")
        return None

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
    model_inst = get_model()
    if model_inst is None:
        logging.getLogger(__name__).warning("Model not available, returning None for predicted crop")
        cultivo_predicho = None
    else:
        try:
            cultivo_predicho = model_inst.predict(pd.DataFrame([valores_ordenados], columns=features))[0]
        except Exception:
            logging.getLogger(__name__).exception("Error while predicting with the ML model")
            cultivo_predicho = None

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
            valor = data.get(campo, 0.0)
            # Aseguramos que el valor sea un número (float)
            try:
                valor = float(valor)
            except ValueError:
                valor = 0.0  # Si no es convertible a float, usamos 0.0
            acumulados[campo] += valor
        contador += 1

    if contador == 0:
        return None  

    promedios = {campo: acumulados[campo] / contador for campo in campos}
    return SimpleNamespace(**promedios)


def recomendaciones(request):
    if "usuario" not in request.session:
        return redirect("login")
    if request.method == "POST":
        # Obtener la cantidad de registros seleccionados por el usuario
        cantidad_registros = int(request.POST.get('cantidad_registros', 10))  # Valor predeterminado de 10 si no se ingresa nada
        
        # Obtener los registros desde Firestore
        user = request.session.get('usuario')  # Suponiendo que el nombre de usuario está en la sesión
        mediciones = obtener_n_registros_firestore(user, cantidad_registros)
        
        # Promediar las variables de medición
        m = promediar_variables_medicion(mediciones)
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

        # Evaluar el estado del suelo y obtener las recomendaciones
        resultado = evaluar_suelo(fila)
        resultados.append({
            'fecha': mediciones[0]['fecha'] if mediciones else timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'medicion': m,
            'cultivo': resultado['cultivo'],
            'estado': resultado['estado'],
            'recomendaciones': resultado['recomendaciones']
        })

        # Pasar los resultados a la plantilla
        return render(request, 'recomendaciones.html', {'resultados': resultados})

    # Si el método no es POST, redirigir a la misma página o mostrar un mensaje de error
    return render(request, 'recomendaciones.html', {'resultados': []})

def vista_bienvenida(request):
    return render(request, 'bienvenida.html')

def vista_instrucciones(request):
    return render(request, 'instrucciones.html')

