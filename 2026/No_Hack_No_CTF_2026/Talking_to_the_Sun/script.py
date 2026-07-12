#!/usr/bin/env python3
# debug2.py
import requests

BASE_URL = "http://localhost:5000"

session = requests.Session()
email = "testdebug@example.com"
password = "password123"

print("[*] Registrando...")
r = session.post(f"{BASE_URL}/register", data={
    "email": email, "password": password
}, allow_redirects=False)
print(f"Registro: {r.status_code}")
print(f"Cookies: {session.cookies.get_dict()}")

# Si ya existe, intentamos login directo
print("\n[*] Login...")
r = session.post(f"{BASE_URL}/login", data={
    "email": email, "password": password
}, allow_redirects=False)
print(f"Login: {r.status_code}")
print(f"Location: {r.headers.get('Location')}")
print(f"Cookies: {session.cookies.get_dict()}")

# Seguir redirect para establecer cookie de sesión
if r.status_code == 302:
    redirect_url = r.headers.get('Location')
    r = session.get(f"{BASE_URL}{redirect_url}")
    print(f"Redirect: {r.status_code}")
    print(f"Cookies: {session.cookies.get_dict()}")

print("\n[*] Generando token via API...")
r = session.post(f"{BASE_URL}/api/generate", json={
    "time": 0, "motion": 1, "place": 2, "seat": 3
})
print(f"API: {r.status_code}")
print(f"Respuesta: {r.json()}")
