import requests
import time

API_KEY = "BX8EEVZ092MP4LXX"
CHANNEL_ID = "2967381"
URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={API_KEY}&results=1"

ultimo_entry_id = None

def run_monitor():
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
                        print("Nuevo dato:", nuevo_dato)
                        ultimo_entry_id = nuevo_entry_id
                        
            time.sleep(15)
        except Exception as e:
            print("Error en monitor:", e)
            time.sleep(30)
