#!/usr/bin/env sage
# attack_lattice.sage
from sage.all import *
import json
import hashlib
import base64

# Cargar firmas
firmas = []
with open('/work/firmas_real.txt', 'r') as f:
    for line in f:
        r, s, z, acc = line.strip().split(',')
        firmas.append((int(r, 16), int(s, 16), int(z, 16), acc))

print(f"[+] Firmas cargadas: {len(firmas)}")

# Parámetros de BrainpoolP512r1
p = 0xAADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA703308717D4D9B009BC66842AECDA12AE6A380E62881FF2F2D82C68528AA6056583A48F3
A = 0x7830A3318B603B89E2327145AC234CC594CBDD8D3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CA
B_val = 0x3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CADC083E67984050B75EBAE5DD2809BD638016F723
xG = 0x81AEE4BDD82ED9645A21322E9C4C6A9385ED9F70B5D916C1B43B62EEF4D0098EFF3B1F78E2D0D48D50D1687B93B97D5F7C6D5047406A5E688B352209BCB9F822
yG = 0x7DDE385D566332ECC0EABFA9CF7822FDF209F70024A57B1AA000C55B881F8111B2DCDE494A5F485E5BCA4BD88A2763AED1CA2B2FA8F0540678CD1E0F3AD80892
ORDER = 0x8948962207650232551656602815159153422162609644098354511344597187200057010413418528378981730643524959857451398370029280583094215613882043973354392115544169

F = GF(p)
E = EllipticCurve(F, [A, B_val])
G = E(xG, yG)

print(f"[+] Curva cargada")

B = 2**128  # Cota para la parte aleatoria del nonce
N = min(100, len(firmas))  # Usar 100 firmas

print(f"[*] Usando {N} firmas")
print(f"[*] Nonce entropy: 128 bits")

# Calcular t_i y u_i
t_values = []
u_values = []

for i in range(N):
    r, s, z, _ = firmas[i]
    s_inv = inverse_mod(s, ORDER)
    t = (s_inv * r) % ORDER
    u = (s_inv * z) % ORDER
    t_values.append(t)
    u_values.append(u)

# Construir lattice para HNP
# k_i = u_i + t_i * d mod ORDER
# donde k_i tiene solo 128 bits de entropía
# 
# Planteamos: k_i = u_i + t_i*d - m_i*ORDER
# con k_i pequeño (~128 bits)
#
# Matriz del lattice:
# [ORDER, 0, ..., 0, 0, 0]
# [0, ORDER, ..., 0, 0, 0]
# ...
# [t_1, t_2, ..., t_N, 1, 0]
# [u_1, u_2, ..., u_N, 0, B]

print("[*] Construyendo lattice...")
M = matrix(ZZ, N + 2, N + 2)

for i in range(N):
    M[i, i] = ORDER

for i in range(N):
    M[N, i] = t_values[i]
    M[N+1, i] = u_values[i]

M[N, N] = 1
M[N+1, N+1] = B

print("[*] Ejecutando LLL (esto puede tardar)...")
L = M.LLL()

print("[*] Buscando clave privada...")

for idx, row in enumerate(L):
    # Buscar fila con k_i pequeños
    k_vals = [abs(row[j]) for j in range(N)]
    
    if all(k < B * 10 for k in k_vals) and any(k != 0 for k in k_vals):
        print(f"\n[+] Candidato en fila {idx}")
        print(f"    k_vals (primeros 3): {k_vals[:3]}")
        
        # d está en row[N]
        d_candidate = abs(row[N])
        if d_candidate == 0 or d_candidate >= ORDER:
            continue
        
        print(f"    d candidate: {hex(d_candidate)[:60]}...")
        
        # Verificar con varias firmas
        for sign in [1, -1]:
            d_test = (d_candidate * sign) % ORDER
            if d_test == 0:
                continue
            
            Q = d_test * G
            
            valid = True
            for i in range(min(5, N)):
                r_test, s_test, z_test, _ = firmas[i]
                w = inverse_mod(s_test, ORDER)
                u1 = (z_test * w) % ORDER
                u2 = (r_test * w) % ORDER
                P = u1 * G + u2 * Q
                
                if P.is_zero():
                    valid = False
                    break
                
                if Integer(P.x()) % ORDER != r_test:
                    valid = False
                    break
            
            if valid:
                print(f"\n[+] ¡CLAVE PRIVADA ENCONTRADA!")
                print(f"[+] d = {hex(d_test)}")
                
                with open('/work/private_key_real.txt', 'w') as f:
                    f.write(hex(d_test))
                
                # Forjar token para admin
                ADMIN = "whale@whale-tw.com"
                TARGET = "SinGen Said: At sunrise, when it answers over my signal, I sit by the sun."
                
                def b64u(data):
                    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')
                
                def canonical_payload(account, message):
                    return json.dumps(
                        {"account": account, "message": message},
                        ensure_ascii=False, sort_keys=True, separators=(',', ':')
                    )
                
                def message_hash(account, message):
                    data = canonical_payload(account, message).encode('utf-8')
                    return int.from_bytes(hashlib.sha512(data).digest(), 'big')
                
                import os
                z_admin = message_hash(ADMIN, TARGET)
                
                while True:
                    k = int.from_bytes(os.urandom(64), 'big') % ORDER
                    if k == 0:
                        continue
                    point = k * G
                    r = Integer(point.x()) % ORDER
                    if r == 0:
                        continue
                    s = (inverse_mod(k, ORDER) * (z_admin + r * d_test)) % ORDER
                    if s == 0:
                        continue
                    break
                
                payload = canonical_payload(ADMIN, TARGET).encode('utf-8')
                sig = r.to_bytes(64, 'big') + s.to_bytes(64, 'big')
                token = f"singen.{b64u(payload)}.{b64u(sig)}"
                
                print(f"\n[+] TOKEN FORJADO:")
                print(token)
                
                with open('/work/admin_token_real.txt', 'w') as f:
                    f.write(token)
                
                exit()

print("[-] No se encontró la clave privada")
