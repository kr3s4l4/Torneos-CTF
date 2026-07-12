#!/usr/bin/env sage
from sage.all import *
import json, hashlib, base64, os

# Cargar firmas
firmas = []
with open('/work/firmas.txt') as f:
    for line in f:
        r, s, z, acc = line.strip().split(',')
        firmas.append((int(r,16), int(s,16), int(z,16), acc))

print(f"[+] {len(firmas)} firmas cargadas")

# BrainpoolP512r1
p = 0xAADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA703308717D4D9B009BC66842AECDA12AE6A380E62881FF2F2D82C68528AA6056583A48F3
A = 0x7830A3318B603B89E2327145AC234CC594CBDD8D3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CA
Bv = 0x3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CADC083E67984050B75EBAE5DD2809BD638016F723
xG = 0x81AEE4BDD82ED9645A21322E9C4C6A9385ED9F70B5D916C1B43B62EEF4D0098EFF3B1F78E2D0D48D50D1687B93B97D5F7C6D5047406A5E688B352209BCB9F822
yG = 0x7DDE385D566332ECC0EABFA9CF7822FDF209F70024A57B1AA000C55B881F8111B2DCDE494A5F485E5BCA4BD88A2763AED1CA2B2FA8F0540678CD1E0F3AD80892
ORDER = 0x8948962207650232551656602815159153422162609644098354511344597187200057010413418528378981730643524959857451398370029280583094215613882043973354392115544169

F = GF(p)
E = EllipticCurve(F, [A, Bv])
G = E(xG, yG)

N = min(100, len(firmas))
B = 2**128

print(f"[*] Usando {N} firmas, nonce entropy: 128 bits")

t_vals = []; u_vals = []
for i in range(N):
    r, s, z, _ = firmas[i]
    si = inverse_mod(s, ORDER)
    t_vals.append((si * r) % ORDER)
    u_vals.append((si * z) % ORDER)

print("[*] Construyendo lattice...")
M = matrix(ZZ, N+2, N+2)
for i in range(N):
    M[i,i] = ORDER
    M[N,i] = t_vals[i]
    M[N+1,i] = u_vals[i]
M[N,N] = 1
M[N+1,N+1] = B

print("[*] Ejecutando LLL (puede tardar 30-60s)...")
import sys
sys.stdout.flush()
L = M.LLL()

print("[*] Buscando clave privada...")
for idx, row in enumerate(L):
    k_vals = [abs(row[j]) for j in range(N)]
    if all(k < B*100 for k in k_vals) and any(k != 0 for k in k_vals):
        print(f"    Candidato en fila {idx}")
        for sign in [1, -1]:
            d = (abs(row[N]) * sign) % ORDER
            if d == 0: continue
            Q = d * G
            ok = True
            for i in range(min(5, N)):
                r,s,z,_ = firmas[i]
                w = inverse_mod(s, ORDER)
                P = ((z*w)%ORDER)*G + ((r*w)%ORDER)*Q
                if P.is_zero() or Integer(P.x())%ORDER != r:
                    ok = False; break
            if ok:
                print(f"\n[+] ¡CLAVE PRIVADA ENCONTRADA!")
                print(f"[+] d = {hex(d)}")
                with open('/work/privkey.txt','w') as fk: fk.write(hex(d))
                
                # Forjar token admin
                ADMIN = "whale@whale-tw.com"
                TARGET = "SinGen Said: At sunrise, when it answers over my signal, I sit by the sun."
                
                def b64u(x): 
                    return base64.urlsafe_b64encode(x).rstrip(b'=').decode()
                
                def mh(a,m):
                    p = json.dumps({"account":a,"message":m}, ensure_ascii=False, sort_keys=True, separators=(',',':'))
                    return int.from_bytes(hashlib.sha512(p.encode()).digest(), 'big')
                
                z_adm = mh(ADMIN, TARGET)
                
                # Firmar
                while True:
                    k = int.from_bytes(os.urandom(64), 'big') % ORDER
                    if k == 0: continue
                    pt = k*G
                    r_adm = Integer(pt.x()) % ORDER
                    if r_adm == 0: continue
                    s_adm = (inverse_mod(k, ORDER) * (z_adm + r_adm * d)) % ORDER
                    if s_adm == 0: continue
                    break
                
                payload = json.dumps(
                    {"account": ADMIN, "message": TARGET},
                    ensure_ascii=False, sort_keys=True, separators=(',',':')
                ).encode()
                sig = r_adm.to_bytes(64, 'big') + s_adm.to_bytes(64, 'big')
                token = f"singen.{b64u(payload)}.{b64u(sig)}"
                
                print(f"\n[+] TOKEN FORJADO:")
                print(token)
                
                with open('/work/token.txt', 'w') as ft: 
                    ft.write(token)
                
                print("\n[*] Verificar con:")
                print(f"    curl -X POST <URL>/verify -d 'token={token}'")
                exit()

print("[-] No se encontró la clave privada. Intenta con más firmas.")
