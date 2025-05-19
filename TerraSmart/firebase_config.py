
import firebase_admin
from firebase_admin import credentials,firestore

cred = credentials.Certificate("C:\\Users\\jvuan\\Documents\\ProyectoTerraSmart\\TerraSmart\\terrasmart-c9c6d-firebase-adminsdk-fbsvc-c4df462741.json")
firebase_admin.initialize_app(cred)
db = firestore.client()