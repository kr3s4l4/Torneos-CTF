#!/usr/bin/env python3
# recolecter_fast.py
import requests
import json
import base64
import hashlib
import threading
import sys
import time

BASE_URL = "http://nhnc2.whale-tw.com:10002/"
ORDER_BYTES = 64
TARGET = 150  # Firmas objetivo
N_HILOS = 20  # Hilos simultáneos

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

def worker(wid):
    global stop
    s = requests.Session()
    i = wid
    while not stop:
        email = f"atk{wid:03d}x{i:06d}@x.co"
        password = "p"
        try:
            # Registrar
            s.post(f"{BASE_URL}/register", 
                   data={"email": email, "password": password}, timeout=5)
            
            # Login
            r = s.post(f"{BASE_URL}/login", 
                       data={"email": email, "password": password}, timeout=5)
            
            # Si login ok -> /studio
            if '/studio' in r.url:
                # Generar
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

# Main
print(f"[*] Objetivo: {BASE_URL}")
print(f"[*] Recolectando {TARGET} firmas con {N_HILOS} hilos...")
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

# Guardar
with open('firmas.txt', 'w') as f:
    for r, s, z, acc in firmas:
        f.write(f"{hex(r)},{hex(s)},{hex(z)},{acc}\n")

print(f"[+] Guardadas en firmas.txt")
print(f"[*] Velocidad: {len(firmas)/elapsed:.1f} firmas/segundo")
