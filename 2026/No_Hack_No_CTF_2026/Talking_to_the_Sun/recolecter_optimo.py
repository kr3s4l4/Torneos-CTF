#!/usr/bin/env python3
# recolecter_optimo.py
import requests
import json
import base64
import hashlib
import threading
import sys
import time

BASE_URL = "http://nhnc2.whale-tw.com:10004/"  # Cambiar
ORDER_BYTES = 64
TARGET = 150
N_HILOS = 4  # Pocos hilos para no saturar
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

count = 0
lock = threading.Lock()
stop = False

def guardar_firma(r, s, z, acc):
    with open(OUTPUT_FILE, 'a') as f:
        f.write(f"{hex(r)},{hex(s)},{hex(z)},{acc}\n")

def worker(wid):
    global count, stop
    i = wid
    while not stop:
        email = f"atk{wid:02d}x{i:06d}@x.co"
        password = "p"
        try:
            s = requests.Session()
            s.post(f"{BASE_URL}/register", data={"email": email, "password": password}, timeout=10)
            r = s.post(f"{BASE_URL}/login", data={"email": email, "password": password}, timeout=10)
            
            if '/studio' in r.url:
                r = s.post(f"{BASE_URL}/api/generate", 
                          json={"time": i%50, "motion": (i*7)%50, 
                                "place": (i*13)%50, "seat": (i*17)%50}, 
                          timeout=10)
                
                if r.status_code == 200 and r.json().get('ok'):
                    data = r.json()
                    token = data['token']
                    parts = token.split('.')
                    sig = b64u_decode(parts[2])
                    rs = int.from_bytes(sig[:ORDER_BYTES], 'big')
                    ss = int.from_bytes(sig[ORDER_BYTES:], 'big')
                    z = message_hash(email, data['message'])
                    
                    guardar_firma(rs, ss, z, email)
                    
                    with lock:
                        count += 1
                        sys.stdout.write(f"\r[+] {count}/{TARGET} firmas")
                        sys.stdout.flush()
                        if count >= TARGET:
                            stop = True
                            return
        except Exception as e:
            pass
        i += N_HILOS

# Limpiar archivo
with open(OUTPUT_FILE, 'w') as f:
    f.write('')

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
print(f"\n[+] {count} firmas en {elapsed:.1f}s")
