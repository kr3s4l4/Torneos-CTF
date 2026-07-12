#!/usr/bin/env python3
# forge_token.py
import json
import hashlib
import base64
import os
from ecdsa.curves import BRAINPOOLP512r1
from ecdsa.numbertheory import inverse_mod

# Cargar secretos
STATE = json.loads(open('data/state.json').read())

SIGNING_SCALAR = int(STATE["signing_scalar"], 16)
ADMIN_PASSWORD = STATE["admin_password"]

print(f"[+] Clave privada: {hex(SIGNING_SCALAR)[:50]}...")
print(f"[+] Admin password (b64u): {ADMIN_PASSWORD}")

CURVE = BRAINPOOLP512r1
GENERATOR = CURVE.generator
ORDER = GENERATOR.order()
ORDER_BYTES = (ORDER.bit_length() + 7) // 8

def b64u(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def b64u_decode(value):
    padding = '=' * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode('ascii'))

def canonical_payload(account, message):
    return json.dumps(
        {"account": account, "message": message},
        ensure_ascii=False, sort_keys=True, separators=(',', ':')
    )

def message_hash(account, message):
    data = canonical_payload(account, message).encode('utf-8')
    return int.from_bytes(hashlib.sha512(data).digest(), 'big')

def sign_message(account, message, d):
    z = message_hash(account, message)
    while True:
        k = int.from_bytes(os.urandom(ORDER_BYTES + 16), 'big') % ORDER
        if k == 0:
            continue
        point = k * GENERATOR
        r = point.x() % ORDER
        if r == 0:
            continue
        s = (inverse_mod(k, ORDER) * (z + r * d)) % ORDER
        if s == 0:
            continue
        break
    
    payload = canonical_payload(account, message).encode('utf-8')
    signature = r.to_bytes(ORDER_BYTES, 'big') + s.to_bytes(ORDER_BYTES, 'big')
    token = f"singen.{b64u(payload)}.{b64u(signature)}"
    return token

# Forjar token para admin
ADMIN = "whale@whale-tw.com"
TARGET = "SinGen Said: At sunrise, when it answers over my signal, I sit by the sun."

token = sign_message(ADMIN, TARGET, SIGNING_SCALAR)
print(f"\n[+] Token forjado:")
print(token)

# Verificar con el servidor
import requests
r = requests.post("http://localhost:5000/verify", data={"token": token})
print(f"\n[+] Verificación: {r.status_code}")
# Buscar flag en la respuesta
import re
flag_match = re.search(r'NHNC\{[^}]+\}', r.text)
if flag_match:
    print(f"[+] FLAG: {flag_match.group()}")
else:
    print(r.text[:500])
