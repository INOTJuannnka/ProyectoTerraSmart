
import firebase_admin
from firebase_admin import credentials,firestore

cred = credentials.Certificate("C:/Users/user/Documents/2025.1/Proyecto/ProyectoTerraSmart2.0/ProyectoTerraSmart/TerraSmart/terrasmart-c9c6d-firebase-adminsdk-fbsvc-c4df462741.json")
firebase_admin.initialize_app(cred)
db = firestore.client()