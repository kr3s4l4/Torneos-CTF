#!/usr/bin/env python3
# check_curve.py
from ecdsa.curves import BRAINPOOLP512r1

CURVE = BRAINPOOLP512r1
GENERATOR = CURVE.generator
ORDER = GENERATOR.order()
print(f"ORDER real: {ORDER}")
print(f"ORDER hex: {hex(ORDER)}")
print(f"ORDER bits: {ORDER.bit_length()}")
print(f"ORDER bytes: {(ORDER.bit_length() + 7) // 8}")
