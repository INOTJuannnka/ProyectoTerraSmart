from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from .firebase_config import db

@receiver(user_logged_in)
def save_social_user_to_firebase(sender, request, user, **kwargs):
    print("Datos del usuario:", vars(user))
    print("Señal de login social recibida para:", user.email)
    
    users_ref = db.collection("user")
    existing = users_ref.where("email", "==", user.email).get()
    if not existing:
        users_ref.add({
            "username": user.username,
            "email": user.email,
            "password": "",  # Social login, sin password
        })
        print("Usuario guardado en Firebase:", user.email)
    else:
        print("Usuario ya existe en Firebase:", user.email)
    request.session["usuario"] = user.username