# TerraSmart - Manual Técnico

## Requisitos Previos

- **Python 3.8+**  
  Verifica la versión con:  
  ```sh
  python --version
  ```

- **pip** (gestor de paquetes de Python)  
  Instala pip si no lo tienes:  
  ```sh
  python -m ensurepip --upgrade
  ```

- **Git** (opcional, para clonar el repositorio)

## Instalación del Proyecto

1. **Clona el repositorio**  
   ```sh
   git clone <URL_DEL_REPOSITORIO>
   cd ProyectoTerraSmart
   ```

2. **Crea y activa un entorno virtual**  
   ```sh
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instala las dependencias**  
   Asegúrate de tener un archivo `requirements.txt` con todas las librerías necesarias. Si no existe, crea uno con las siguientes dependencias mínimas:
   ```
    Django==4.2.4
    pandas
    numpy
    matplotlib
    firebase-admin
    joblib
    requests
    django-allauth
    mysqlclient
   
   ```
   Instala con:
   ```sh
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno y archivos sensibles**
   - Coloca tu archivo de credenciales de Firebase en `TerraSmart/terrasmart-c9c6d-firebase-adminsdk-fbsvc-c4df462741.json`.
   - Configura los parámetros de conexión en `TerraSmart/firebase_config.py` si es necesario.
   - Revisa y ajusta los valores en `project_core/settings.py` (por ejemplo, `SECRET_KEY`, `ALLOWED_HOSTS`, configuración de base de datos si usas una distinta a SQLite, etc).

5. **Migraciones de la base de datos**
   > Nota: El modelo principal usa Firestore, pero si usas modelos Django para otras apps:
   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Compila los archivos de traducción (opcional, para i18n)**
   ```sh
   python manage.py compilemessages
   ```

## Ejecución del Proyecto

1. **Inicia el servidor de desarrollo**
   ```sh
   python manage.py runserver
   ```
   Accede a [http://127.0.0.1:8000/](http://127.0.0.1:8000/) en tu navegador.

2. **Carga del modelo de Machine Learning**
   - El modelo se carga automáticamente desde `modelo/my_random_forest.joblib` al iniciar el servidor.
   - Si necesitas regenerar el modelo, reemplaza el archivo `.joblib` en la ruta indicada.

## Estructura de Carpetas

- `TerraSmart/`  
  App principal, contiene vistas, modelos, utilidades, configuración de Firebase, etc.
- `project_core/`  
  Configuración global de Django.
- `locale/`  
  Archivos de traducción para internacionalización.
- `products/`  
  (Si aplica) App adicional para gestión de productos.
- `migrations/`  
  Migraciones de Django.

## Dependencias Principales

- **Django**: Framework principal.
- **pandas, numpy**: Procesamiento de datos.
- **matplotlib**: Generación de gráficos.
- **firebase-admin**: Conexión con Firestore.
- **joblib**: Carga de modelos ML.
- **django-allauth**: Autenticación social.

## Notas Técnicas

- El sistema utiliza Firestore como base de datos principal para mediciones.
- El soporte multilenguaje está habilitado mediante Django i18n y archivos `.po` en la carpeta `locale/`.
- Para agregar nuevos idiomas, crea un subdirectorio en `locale/` y ejecuta `makemessages` y `compilemessages`.
- El monitoreo de datos externos (ThingSpeak) se realiza en segundo plano mediante hilos (`threading.Thread`).

## Comandos Útiles

- Crear superusuario Django:
  ```sh
  python manage.py createsuperuser
  ```
- Actualizar dependencias:
  ```sh
  pip freeze > requirements.txt
  ```

## Problemas Comunes

- **Problemas de migración**: Asegúrate de que las apps estén correctamente listadas en `INSTALLED_APPS`.
- **Traducciones no aparecen**: Ejecuta `python manage.py compilemessages` y revisa la configuración de idioma en `settings.py`.

---

Para dudas técnicas, consulta la documentación oficial de Django y Firebase, o revisa los archivos fuente en este repositorio.
