import requests
import time
from .firebase_config import db
from django.contrib.auth.models import User
from django.utils import timezone



API_KEY = "APIKEY"
CHANNEL_ID = "CHANELID"
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
                        HumedadSuelo_val = float(nuevo_dato.get('field1') or 0)
                        Luz_val = float(nuevo_dato.get('field2') or 0)
                        Temperatura_val = float(nuevo_dato.get('field3') or 0)
                        HumedadAire_val = float(nuevo_dato.get('field4') or 0)
                        Nitrogeno_val = float(nuevo_dato.get('field5') or 0)
                        Fosforo_val = float(nuevo_dato.get('field6') or 0)
                        Potasio_val = float(nuevo_dato.get('field7') or 0)
                        Ph_val = float(nuevo_dato.get('field8') or 0)
                        fecha = timezone.now()
                        datos_organizados = {
                            "HumedadSuelo": HumedadSuelo_val,
                            "Luz": Luz_val,
                            "Temperatura": Temperatura_val,
                            "HumedadAire": HumedadAire_val,
                            "Nitrogeno": Nitrogeno_val,
                            "Fosforo": Fosforo_val,
                            "Potasio": Potasio_val,
                            "PH": Ph_val,
                            "fecha": fecha.isoformat()
                        }
                        db.collection("medicion").add({
                            "user": user,
                            "HumedadSuelo": HumedadSuelo_val,
                            "Luz": Luz_val,
                            "Temperatura": Temperatura_val,
                            "HumedadAire": HumedadAire_val,
                            "Nitrogeno": Nitrogeno_val,
                            "Fosforo": Fosforo_val,
                            "Potasio": Potasio_val,
                            "PH": Ph_val,
                            "fecha": fecha.isoformat()
                        })

                        print("Datos organizados:", datos_organizados)
                        
            time.sleep(15)
        except Exception as e:
            print("Error en monitor:", e)
            time.sleep(30)
