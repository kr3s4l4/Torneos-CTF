#!/usr/bin/env python3
# recolecter_stream.py
import requests
import json
import base64
import hashlib
import threading
import sys
import time

BASE_URL = "http://nhnc2.whale-tw.com:10007"  # Cambiar para instancia real
ORDER_BYTES = 64
TARGET = 150
N_HILOS = 20
OUTPUT_FILE = 'firmas.txt'

def b64u_decode(value):
    padding = '=' * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode('ascii'))

def message_hash(account, message):
    payload = json.dumps(
        {"account": account, "message": message},
        ensure_ascii=False, sort_keys=True, separators=(',', ':')
    )
    return int.from_bytes(hashlib.sha512(payload.encode('utf-8')).digest(), 'big')

firmas = []
lock = threading.Lock()
stop = False
file_lock = threading.Lock()

def guardar_firma(r, s, z, acc):
    """Guarda cada firma inmediatamente al archivo"""
    with file_lock:
        with open(OUTPUT_FILE, 'a') as f:
            f.write(f"{hex(r)},{hex(s)},{hex(z)},{acc}\n")

def worker(wid):
    global stop
    s = requests.Session()
    i = wid
    while not stop:
        email = f"atk{wid:03d}x{i:06d}@x.co"
        password = "p"
        try:
            s.post(f"{BASE_URL}/register", 
                   data={"email": email, "password": password}, timeout=5)
            r = s.post(f"{BASE_URL}/login", 
                       data={"email": email, "password": password}, timeout=5)
            if '/studio' in r.url:
                r = s.post(f"{BASE_URL}/api/generate", 
                           json={"time": i%50, "motion": (i*7)%50, 
                                 "place": (i*13)%50, "seat": (i*17)%50}, 
                           timeout=5)
                if r.status_code == 200 and r.json().get('ok'):
                    data = r.json()
                    token = data['token']
                    parts = token.split('.')
                    sig = b64u_decode(parts[2])
                    rs = int.from_bytes(sig[:ORDER_BYTES], 'big')
                    ss = int.from_bytes(sig[ORDER_BYTES:], 'big')
                    z = message_hash(email, data['message'])
                    
                    # Guardar inmediatamente
                    guardar_firma(rs, ss, z, email)
                    
                    with lock:
                        firmas.append((rs, ss, z, email))
                        n = len(firmas)
                        sys.stdout.write(f"\r[+] {n}/{TARGET} firmas")
                        sys.stdout.flush()
                        if n >= TARGET:
                            stop = True
                            return
        except:
            pass
        i += N_HILOS

# Limpiar archivo anterior
with open(OUTPUT_FILE, 'w') as f:
    f.write('')

print(f"[*] Objetivo: {BASE_URL}")
print(f"[*] Recolectando {TARGET} firmas con {N_HILOS} hilos...")
print(f"[*] Guardando en: {OUTPUT_FILE}")
sys.stdout.flush()

start = time.time()
threads = []
for t in range(N_HILOS):
    th = threading.Thread(target=worker, args=(t,))
    threads.append(th)
    th.start()

for th in threads:
    th.join()

elapsed = time.time() - start
print(f"\n[+] {len(firmas)} firmas en {elapsed:.1f}s")
print(f"[+] Archivo: {OUTPUT_FILE} ({len(firmas)} líneas)")
