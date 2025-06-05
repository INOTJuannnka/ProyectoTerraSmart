import requests
import time
from .firebase_config import db
from django.contrib.auth.models import User
from django.utils import timezone




    # Ejemplo de guardar datos asociados al usuario
    # DatosSensor.objects.create(usuario=user, PH=..., etc.)

API_KEY = "BX8EEVZ092MP4LXX"
CHANNEL_ID = "2967381"
URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={API_KEY}&results=1"

ultimo_entry_id = None

def run_monitor(user_id):
    try:
        user = user_id  
    except User.DoesNotExist:
        print("Usuario no encontrado")
        return

    # Aquí usas `user` normalmente:
    print(f"Iniciando monitor para: {user}")
    global ultimo_entry_id
    while True:
        try:
            response = requests.get(URL)
            if response.status_code == 200:
                data = response.json()
                feeds = data['feeds']
                if feeds:
                    nuevo_dato = feeds[0]
                    nuevo_entry_id = int(nuevo_dato['entry_id'])
                    if ultimo_entry_id is None or nuevo_entry_id > ultimo_entry_id:
                        print("Nuevo dato bruto:", nuevo_dato)
                        ultimo_entry_id = nuevo_entry_id

                        # Campos simples
                        ph_val = float(nuevo_dato.get('field1') or 0)
                        materiaOrganica_val = float(nuevo_dato.get('field2') or 0)
                        fosforo_val = float(nuevo_dato.get('field3') or 0)
                        azufre_val = float(nuevo_dato.get('field4') or 0)

                        # Función para extraer dos valores separados por coma
                        def extraer_dos_valores(campo):
                            valores = (nuevo_dato.get(campo) or "0,0").split(",")
                            return tuple(float(v) for v in valores) if len(valores) == 2 else (float(valores[0]), 0.0)

                        # Campos dobles
                        calcio_val, hierro_val = extraer_dos_valores('field5')
                        magnesio_val, cobre_val = extraer_dos_valores('field6')
                        potasio_val, manganeso_val = extraer_dos_valores('field7')
                        sodio_val, zinc_val = extraer_dos_valores('field8')
                        fecha = timezone.now()
                        datos_organizados = {
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
                        }
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
                            "fecha": fecha.isoformat()
                        })

                        print("Datos organizados:", datos_organizados)
                        
            time.sleep(15)
        except Exception as e:
            print("Error en monitor:", e)
            time.sleep(30)
