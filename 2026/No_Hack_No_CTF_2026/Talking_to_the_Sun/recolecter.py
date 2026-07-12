#!/usr/bin/env python3
# recolectar.py
import requests
import json
import base64
import hashlib
from ecdsa.curves import BRAINPOOLP512r1
from ecdsa.numbertheory import inverse_mod

BASE_URL = "http://localhost:5000"
CURVE = BRAINPOOLP512r1
GENERATOR = CURVE.generator
ORDER = GENERATOR.order()
ORDER_BYTES = 64

def b64u_decode(value):
    padding = '=' * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode('ascii'))

def message_hash(account, message):
    payload = json.dumps(
        {"account": account, "message": message},
        ensure_ascii=False, sort_keys=True, separators=(',', ':')
    )
    return int.from_bytes(hashlib.sha512(payload.encode('utf-8')).digest(), 'big')

def registrar_y_login(session, email, password):
    # Registrar (ignorar si ya existe)
    session.post(f"{BASE_URL}/register", data={
        "email": email, "password": password
    }, allow_redirects=False)
    
    # Login
    r = session.post(f"{BASE_URL}/login", data={
        "email": email, "password": password
    }, allow_redirects=False)
    
    if r.status_code == 302 and r.headers.get('Location') == '/studio':
        # Seguir redirect para establecer sesión
        session.get(f"{BASE_URL}/studio")
        return True
    return False

# Recolectar firmas
print("[*] Recolectando firmas...")
firmas = []

for i in range(200):
    email = f"attacker{i:04d}@example.com"
    password = "password123"
    
    session = requests.Session()
    
    if not registrar_y_login(session, email, password):
        print(f"[-] Error login {email}")
        continue
    
    # Generar token via API
    r = session.post(f"{BASE_URL}/api/generate", json={
        "time": i % 50,
        "motion": (i*7) % 50,
        "place": (i*13) % 50,
        "seat": (i*17) % 50
    })
    
    if r.status_code == 200 and r.json().get('ok'):
        data = r.json()
        token = data['token']
        account = email
        message = data['message']
        
        # Parsear firma
        parts = token.split('.')
        sig = b64u_decode(parts[2])
        r_sig = int.from_bytes(sig[:ORDER_BYTES], 'big')
        s_sig = int.from_bytes(sig[ORDER_BYTES:], 'big')
        z = message_hash(account, message)
        
        firmas.append((r_sig, s_sig, z, account))
        print(f"[+] Firma {len(firmas)}: {account}")
    else:
        print(f"[-] Error: {r.json()}")

print(f"\n[+] Total firmas recolectadas: {len(firmas)}")

# Guardar firmas
with open('firmas.txt', 'w') as f:
    for r, s, z, acc in firmas:
        f.write(f"{hex(r)},{hex(s)},{hex(z)},{acc}\n")

print("[+] Firmas guardadas en firmas.txt")
