
import os
import logging

import firebase_admin
from firebase_admin import credentials, firestore

# Determine credential path. Order of precedence:
# 1. FIREBASE_CREDENTIALS environment variable
# 2. Several common repo-relative locations (module-local, project-level)
# If the file isn't present or initialization fails, we set `db = None`.

DEFAULT_CRED_FILENAME = "serviceAccountKey.json"
env_path = os.environ.get("FIREBASE_CREDENTIALS")

# Candidate locations to check (in order)
base_dir = os.path.dirname(__file__)  # TerraSmart/
candidates = []
if env_path:
	candidates.append(env_path)
# TerraSmart/firebase/serviceAccountKey.json
candidates.append(os.path.join(base_dir, 'firebase', DEFAULT_CRED_FILENAME))
# project_root/firebase/serviceAccountKey.json (one level up)
candidates.append(os.path.normpath(os.path.join(base_dir, '..', 'firebase', DEFAULT_CRED_FILENAME)))
# project_root/TerraSmart/firebase/serviceAccountKey.json (redundant but safe)
candidates.append(os.path.normpath(os.path.join(base_dir, '..', 'ProyectoTerraSmart', 'firebase', DEFAULT_CRED_FILENAME)))
# repo-level firebase/serviceAccountKey.json
candidates.append(os.path.normpath(os.path.join(base_dir, '..', 'firebase', DEFAULT_CRED_FILENAME)))

cred_path = None
for p in candidates:
	if p and os.path.exists(p):
		cred_path = p
		break

db = None
if cred_path:
	# Print to console so it's visible when running manage.py/runserver
	print("Firebase credentials found at:", cred_path)
	try:
		cred = credentials.Certificate(cred_path)
		try:
			# avoid initializing more than once
			firebase_admin.get_app()
		except ValueError:
			firebase_admin.initialize_app(cred)
		db = firestore.client()
	except Exception as exc:
		logging.getLogger(__name__).warning(
			"Firebase initialization failed for '%s': %s", cred_path, exc
		)
		print("Firebase initialization failed:", exc)
else:
	# Print the candidates we checked to help debugging
	print("Firebase credentials not found. Checked paths:")
	for p in candidates:
		print(" -", p)
	logging.getLogger(__name__).info(
		"Firebase credentials not found. Continuing without Firestore (db=None)."
	)