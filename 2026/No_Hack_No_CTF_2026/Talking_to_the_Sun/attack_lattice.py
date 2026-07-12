#!/usr/bin/env python3
# attack_lattice.py
import json
import hashlib
from ecdsa.curves import BRAINPOOLP512r1
from ecdsa.numbertheory import inverse_mod
from fpylll import IntegerMatrix, LLL

# Cargar firmas
firmas = []
with open('firmas.txt', 'r') as f:
    for line in f:
        r, s, z, acc = line.strip().split(',')
        firmas.append((int(r, 16), int(s, 16), int(z, 16), acc))

print(f"[+] Firmas cargadas: {len(firmas)}")

CURVE = BRAINPOOLP512r1
ORDER = CURVE.generator.order()
ORDER_BITS = ORDER.bit_length()
B = 2**128  # Cota para la parte aleatoria del nonce

# Usamos varias firmas
N = 40  # Número de firmas

print(f"[*] ORDER bits: {ORDER_BITS}")
print(f"[*] Nonce entropy: 128 bits")
print(f"[*] Usando {N} firmas")

# Calcular t_i = s^(-1)*r mod ORDER, u_i = s^(-1)*z mod ORDER
t_values = []
u_values = []

for i in range(N):
    r, s, z, _ = firmas[i]
    s_inv = inverse_mod(s, ORDER)
    t = (s_inv * r) % ORDER
    u = (s_inv * z) % ORDER
    t_values.append(t)
    u_values.append(u)

# Construir matriz para lattice
# Queremos encontrar k_i pequeños tales que:
# k_i ≡ u_i + t_i * d (mod ORDER)
# => k_i = u_i + t_i * d - m_i * ORDER
# => t_i * d - k_i - m_i * ORDER = -u_i
#
# Planteamos el lattice:
# | ORDER   0     0   ... 0     0       0     |
# | 0       ORDER 0   ... 0     0       0     |
# | ...                                      |
# | t_1     t_2   t_3 ... t_N   B/ORDER 0     |
# | -u_1   -u_2  -u_3 ... -u_N  0       B     |

dim = N + 2
M = IntegerMatrix(dim, dim)

# Llenar la matriz
for i in range(N):
    M[i, i] = ORDER

scale = B // ORDER + 1
for i in range(N):
    M[N, i] = t_values[i]
    M[N+1, i] = (-u_values[i]) % ORDER

M[N, N] = scale
M[N+1, N+1] = B

print("[*] Ejecutando LLL...")
L_reduced = LLL.reduction(M)

print("[*] Buscando solución...")

# Convertir a lista para iterar más fácil
rows = [[L_reduced[i, j] for j in range(dim)] for i in range(dim)]

for idx, row in enumerate(rows):
    # Los primeros N elementos deberían ser pequeños (los k_i)
    k_vals = [abs(row[j]) for j in range(N)]
    
    # Verificar si todos son menores que B*2 (margen)
    if all(k < B * 100 for k in k_vals) and any(k != 0 for k in k_vals):
        print(f"\n[+] Posible solución en fila {idx}")
        print(f"    k_vals (primeros 3): {k_vals[:3]}")
        
        # Recuperar d
        # De la construcción: row[N] debería ser d * scale
        d_candidate = abs(row[N]) // scale
        if d_candidate == 0:
            continue
            
        print(f"    d candidate: {hex(d_candidate)[:60]}...")
        
        # Verificar
        G = CURVE.generator
        
        for sign in [1, -1]:
            d_test = (d_candidate * sign) % ORDER
            Q = d_test * G
            
            # Verificar con varias firmas
            valid = True
            for i in range(min(5, N)):
                r_test, s_test, z_test, _ = firmas[i]
                w = inverse_mod(s_test, ORDER)
                u1 = (z_test * w) % ORDER
                u2 = (r_test * w) % ORDER
                P = u1 * G + u2 * Q
                
                if P.x() is None or P.x() % ORDER != r_test:
                    valid = False
                    break
            
            if valid:
                print(f"\n[+] ¡CLAVE PRIVADA ENCONTRADA!")
                print(f"[+] d = {hex(d_test)}")
                
                # Guardar clave
                with open('private_key.txt', 'w') as f:
                    f.write(hex(d_test))
                
                # Ahora forjar firma para admin
                forge_admin(d_test)
                exit()
        
        print("[-] Verificación falló con esta fila")

print("[-] No se encontró la clave privada")
