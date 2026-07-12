#!/usr/bin/env sage
# attack_sage.py
import json
import hashlib
import sys
sys.path.insert(0, '/work')
from ecdsa.curves import BRAINPOOLP512r1
from ecdsa.numbertheory import inverse_mod

# Cargar firmas
firmas = []
with open('/work/firmas.txt', 'r') as f:
    for line in f:
        r, s, z, acc = line.strip().split(',')
        firmas.append((int(r, 16), int(s, 16), int(z, 16), acc))

print(f"[+] Firmas cargadas: {len(firmas)}")

CURVE = BRAINPOOLP512r1
ORDER = CURVE.generator.order()
B = 2**128  # 128 bits de entropía

N = 40  # Número de firmas a usar
print(f"[*] Usando {N} firmas")

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

# Construir lattice
M = matrix(ZZ, N + 2, N + 2)

for i in range(N):
    M[i, i] = ORDER

for i in range(N):
    M[N, i] = t_values[i]
    M[N+1, i] = (-u_values[i]) % ORDER

M[N, N] = B
M[N+1, N+1] = ORDER  # Escalar diferente

print("[*] Ejecutando LLL...")
L = M.LLL()

print("[*] Buscando solución...")
for idx, row in enumerate(L):
    k_vals = [abs(row[j]) for j in range(N)]
    
    if all(k < B * 10 for k in k_vals) and any(k != 0 for k in k_vals):
        print(f"\n[+] Posible solución en fila {idx}")
        print(f"    k_vals (primeros 3): {k_vals[:3]}")
        
        # Recuperar d
        d_candidate = abs(row[N+1])
        if d_candidate == 0:
            continue
            
        print(f"    d candidate: {hex(d_candidate)[:60]}...")
        
        G = CURVE.generator
        
        for sign in [1, -1]:
            d_test = (d_candidate * sign) % ORDER
            Q = d_test * G
            
            valid = True
            for i in range(min(5, N)):
                r_test, s_test, z_test, _ = firmas[i]
                w = inverse_mod(s_test, ORDER)
                u1 = (z_test * w) % ORDER
                u2 = (r_test * w) % ORDER
                P = u1 * G + u2 * Q
                
                if P.x() is None or Integer(P.x()) % ORDER != r_test:
                    valid = False
                    break
            
            if valid:
                print(f"\n[+] ¡CLAVE PRIVADA ENCONTRADA!")
                print(f"[+] d = {hex(d_test)}")
                with open('/work/private_key.txt', 'w') as f:
                    f.write(hex(d_test))
                break
        if valid:
            break
