#!/usr/bin/env python3
# check_order2.py
ORDER = 0x8948962207650232551656602815159153422162609644098354511344597187200057010413418528378981730643524959857451398370029280583094215613882043973354392115544169

print(f"ORDER = {ORDER}")
print(f"ORDER bits = {ORDER.bit_length()}")

# Verificar si es primo
from sympy import isprime
print(f"Es primo: {isprime(ORDER)}")

# Verificar las firmas
import json
from math import gcd

with open('firmas.txt', 'r') as f:
    for i, line in enumerate(f):
        r, s, z, acc = line.strip().split(',')
        s_int = int(s, 16)
        g = gcd(s_int, ORDER)
        if g != 1:
            print(f"Firma {i}: s no es coprimo con ORDER, gcd={g}")
            print(f"  s = {s_int}")
            print(f"  s % ORDER = {s_int % ORDER}")
        if i >= 20:
            break
