
import firebase_admin
from firebase_admin import credentials,firestore

# Ubicacion Juan PC
#cred = credentials.Certificate("C:/Users/user/Documents/2025.1/Proyecto/ProyectoTerraSmart2.0/ProyectoTerraSmart/TerraSmart/terrasmart-c9c6d-firebase-adminsdk-fbsvc-c4df462741.json")
#cred = credentials.Certificate("C:\\Users\\jvuan\\Documents\\TerraSmart\\ProyectoTerraSmart\\TerraSmart\\terrasmart-c9c6d-firebase-adminsdk-fbsvc-c4df462741.json")

# Ubicacion Miguel PC
#cred = credentials.Certificate("D:/Mis documentos/Downloads/TerraSmart/ProyectoTerraSmart/TerraSmart/terrasmart-c9c6d-firebase-adminsdk-fbsvc-c4df462741.json")

# Ubicacion PC Julian
cred = credentials.Certificate("C:/Users/user/Documents/2025.1/Proyecto/ProyectoTerraSmart2.0/ProyectoTerraSmart/TerraSmart/terrasmart-c9c6d-firebase-adminsdk-fbsvc-c4df462741.json")

firebase_admin.initialize_app(cred)
db = firestore.client()