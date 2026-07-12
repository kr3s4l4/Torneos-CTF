#!/usr/bin/env python3
# auto_pwn.py - Recolecta y ataca en paralelo
import requests
import json
import base64
import hashlib
import threading
import subprocess
import sys
import time
import os

if len(sys.argv) < 2:
    print(f"Uso: python3 {sys.argv[0]} <URL>")
    sys.exit(1)

BASE_URL = sys.argv[1].rstrip('/')
ORDER_BYTES = 64
TARGET = 150
N_HILOS = 25

print(f"[*] Objetivo: {BASE_URL}")
print(f"[*] Target: {TARGET} firmas, {N_HILOS} hilos")

# ===== RECOLECTOR =====
firmas = []
lock = threading.Lock()
stop = False

def b64u_decode(value):
    padding = '=' * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode('ascii'))

def message_hash(account, message):
    payload = json.dumps(
        {"account": account, "message": message},
        ensure_ascii=False, sort_keys=True, separators=(',', ':')
    )
    return int.from_bytes(hashlib.sha512(payload.encode('utf-8')).digest(), 'big')

def worker(wid):
    global stop
    s = requests.Session()
    i = wid
    while not stop:
        email = f"atk{wid:03d}x{i:06d}@x.co"
        password = "p"
        try:
            s.post(f"{BASE_URL}/register", data={"email": email, "password": password}, timeout=5)
            r = s.post(f"{BASE_URL}/login", data={"email": email, "password": password}, timeout=5)
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
                    with lock:
                        firmas.append((rs, ss, z, email))
                        n = len(firmas)
                        sys.stdout.write(f"\r[+] Firmas: {n}/{TARGET}  ")
                        sys.stdout.flush()
                        if n >= TARGET:
                            stop = True
                            return
        except:
            pass
        i += N_HILOS

# ===== Lanzar recolección en background =====
start = time.time()
threads = []
for t in range(N_HILOS):
    th = threading.Thread(target=worker, args=(t,))
    threads.append(th)
    th.start()

# ===== Esperar a tener suficientes firmas para empezar Sage =====
MIN_PARA_SAGE = 80
print(f"\n[*] Esperando {MIN_PARA_SAGE} firmas para lanzar Sage...")
while len(firmas) < MIN_PARA_SAGE:
    time.sleep(0.5)

# ===== Guardar firmas parciales y lanzar Sage en paralelo =====
with open('firmas.txt', 'w') as f:
    for r, s, z, acc in firmas:
        f.write(f"{hex(r)},{hex(s)},{hex(z)},{acc}\n")

print(f"\n[*] Lanzando Sage con {len(firmas)} firmas iniciales...")

# Crear script Sage inline
sage_script = f'''
import json, hashlib, base64, os

firmas = []
with open('/work/firmas.txt') as f:
    for line in f:
        r, s, z, acc = line.strip().split(',')
        firmas.append((int(r,16), int(s,16), int(z,16), acc))

print(f"[Sage] {{len(firmas)}} firmas")

p = 0xAADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA703308717D4D9B009BC66842AECDA12AE6A380E62881FF2F2D82C68528AA6056583A48F3
A = 0x7830A3318B603B89E2327145AC234CC594CBDD8D3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CA
Bv = 0x3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CADC083E67984050B75EBAE5DD2809BD638016F723
xG = 0x81AEE4BDD82ED9645A21322E9C4C6A9385ED9F70B5D916C1B43B62EEF4D0098EFF3B1F78E2D0D48D50D1687B93B97D5F7C6D5047406A5E688B352209BCB9F822
yG = 0x7DDE385D566332ECC0EABFA9CF7822FDF209F70024A57B1AA000C55B881F8111B2DCDE494A5F485E5BCA4BD88A2763AED1CA2B2FA8F0540678CD1E0F3AD80892
ORDER = 0x8948962207650232551656602815159153422162609644098354511344597187200057010413418528378981730643524959857451398370029280583094215613882043973354392115544169

F = GF(p)
E = EllipticCurve(F, [A, Bv])
G = E(xG, yG)

N = min(80, len(firmas))
B = 2**128

t_vals = []; u_vals = []
for i in range(N):
    r, s, z, _ = firmas[i]
    si = inverse_mod(Integer(s), ORDER)
    t_vals.append((si * r) % ORDER)
    u_vals.append((si * z) % ORDER)

M = matrix(ZZ, N+2, N+2)
for i in range(N):
    M[i,i] = ORDER
    M[N,i] = t_vals[i]
    M[N+1,i] = u_vals[i]
M[N,N] = 1
M[N+1,N+1] = B

print("[Sage] LLL...")
L = M.LLL()

for idx, row in enumerate(L):
    k_vals = [abs(row[j]) for j in range(N)]
    if all(k < B*100 for k in k_vals) and any(k != 0 for k in k_vals):
        for sign in [1, -1]:
            d = (abs(row[N]) * sign) % ORDER
            if d == 0: continue
            Q = d * G
            ok = True
            for i in range(min(5, N)):
                r,s,z,_ = firmas[i]
                w = inverse_mod(Integer(s), ORDER)
                P = ((z*w)%ORDER)*G + ((r*w)%ORDER)*Q
                if P.is_zero() or Integer(P.x())%ORDER != r:
                    ok = False; break
            if ok:
                print(f"[Sage] CLAVE: {{hex(d)}}")
                with open('/work/privkey.txt','w') as fk: fk.write(hex(d))
                
                ADMIN = "whale@whale-tw.com"
clear                TARGET = "SinGen Said: At sunrise, when it answers over my signal, I sit by the sun."
                
                def b64u(x): return base64.urlsafe_b64encode(x).rstrip(b'=').decode()
                def mh(a,m):
                    p = json.dumps({{"account":a,"message":m}}, ensure_ascii=False, sort_keys=True, separators=(',',':'))
                    return int.from_bytes(hashlib.sha512(p.encode()).digest(), 'big')
                
                z_adm = mh(ADMIN, TARGET)
                while True:
                    k = int.from_bytes(os.urandom(64), 'big') % ORDER
                    if k==0: continue
                    pt = k*G; r_adm = Integer(pt.x())%ORDER
                    if r_adm==0: continue
                    s_adm = (inverse_mod(Integer(k), ORDER)*(z_adm + r_adm*d))%ORDER
                    if s_adm==0: continue
                    break
                
                payload = json.dumps({{"account":ADMIN,"message":TARGET}}, ensure_ascii=False, sort_keys=True, separators=(',',':')).encode()
                sig = r_adm.to_bytes(64,'big') + s_adm.to_bytes(64,'big')
                token = f"singen.{{b64u(payload)}}.{{b64u(sig)}}"
                print(f"[Sage] TOKEN: {{token}}")
                with open('/work/token.txt','w') as ft: ft.write(token)
                exit()
print("[Sage] NO ENCONTRADA")
'''

with open('auto_attack.sage', 'w') as f:
    f.write(sage_script)

# Lanzar Sage en background
sage_proc = subprocess.Popen([
    'docker', 'run', '--rm', '-v', f'{os.getcwd()}:/work:rw',
    'sagemath/sagemath', 'sage', '/work/auto_attack.sage'
], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# ===== Seguir recolectando mientras Sage trabaja =====
print("[*] Recolectando más firmas mientras Sage ataca...")
for th in threads:
    th.join()

elapsed = time.time() - start
print(f"\n[+] Recolección: {len(firmas)} firmas en {elapsed:.1f}s")

# Guardar todas las firmas finales
with open('firmas.txt', 'w') as f:
    for r, s, z, acc in firmas:
        f.write(f"{hex(r)},{hex(s)},{hex(z)},{acc}\n")

# ===== Esperar a Sage =====
print("[*] Esperando a Sage...")
sage_output, _ = sage_proc.communicate(timeout=180)
print(sage_output)

# ===== Verificar =====
if os.path.exists('token.txt'):
    with open('token.txt') as f:
        token = f.read().strip()
    print(f"\n[*] Verificando token...")
    r = requests.post(f"{BASE_URL}/verify", data={"token": token})
    try:
        result = r.json()
        print(f"[+] FLAG: {result.get('flag', 'NO ENCONTRADA')}")
    except:
        print(r.text[:500])
else:
    print("[-] No se generó token")
