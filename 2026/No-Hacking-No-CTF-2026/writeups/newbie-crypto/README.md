Writeup: No Hack No CTF 2026 - Newbie Crypto Challenge
📋 Información del Reto

    Nombre del reto: Newbie Crypto

    Categoría: Criptografía

    Dificultad: Fácil

    Vulnerabilidad: Nonce Reuse en AES-CTR

    Archivos proporcionados: chall.py, output.txt, public.txt

🔍 Análisis Inicial
Archivo chall.py

El código implementa un sistema de tickets cifrados con AES en modo CTR:
python

KEY = get_random_bytes(16)
NONCE = b"ticket42"

Punto crítico: La clave y el nonce son fijos para todas las operaciones de cifrado. En AES-CTR, la seguridad depende de que el par (clave, nonce) sea único para cada cifrado.
Archivo public.txt

Contiene los nombres y asientos de 4 asistentes:
text

name,seat
hsuan0223x,H-0223
NHNC,T-0704
this_chal_not_need_read_read_read_read_read_read_read_read_read_read_read,N-0705
AI_WILL_SLOP,C-114514

Archivo output.txt

Contiene 4 tickets de invitado cifrados y 1 ticket de administrador cifrado (que contiene la flag).
🧠 Entendiendo la Vulnerabilidad
¿Cómo funciona AES-CTR?

En modo CTR (Counter), el cifrado funciona así:

    Se genera un keystream usando el cifrador AES con la clave y un contador:
    text

    keystream = AES_encrypt(key, nonce || counter)

    El texto cifrado se obtiene haciendo XOR del texto plano con el keystream:
    text

    ciphertext = plaintext XOR keystream

El Problema del Nonce Reuse

Cuando se reutiliza el mismo par (key, nonce):

    El mismo keystream se genera para todos los mensajes

    Si conocemos un par (plaintext, ciphertext), podemos recuperar el keystream:
    text

    keystream = plaintext XOR ciphertext

    Con el keystream recuperado, podemos descifrar cualquier otro mensaje:
    text

    new_plaintext = new_ciphertext XOR keystream

Analogía: Es como usar la misma contraseña de un solo uso (OTP) dos veces - pierde toda su seguridad.
💻 Explotación
Paso 1: Identificar el mensaje más largo

El guest_2 tiene el nombre más largo (this_chal_not_need_read_...), lo que nos dará más keystream para descifrar completamente el ticket de admin.
Paso 2: Reconstruir el texto plano conocido

Creamos el mismo ticket que se generó para el guest_2:
python

def make_guest_ticket(name, seat):
    return json.dumps({
        "event": "modern-crypto-101",
        "role": "guest",
        "name": name,
        "seat": seat,
        "note": "enjoy the workshop"
    }, separators=(",", ":")).encode()

plaintext = make_guest_ticket(
    "this_chal_not_need_read_read_read_read_read_read_read_read_read_read_read", 
    "N-0705"
)

Paso 3: Recuperar el keystream
python

ciphertext = bytes.fromhex(guest_ciphers[2])
keystream = xor(plaintext, ciphertext[:len(plaintext)])

Paso 4: Descifrar el ticket de admin
python

admin_bytes = bytes.fromhex(admin_cipher)
admin_plain = xor(admin_bytes[:len(keystream)], keystream)

🚀 Solución Completa
python

from pwn import xor
import json

# Datos conocidos de public.txt
ATTENDEES = [
    ("hsuan0223x", "H-0223"),
    ("NHNC", "T-0704"),
    ("this_chal_not_need_read_read_read_read_read_read_read_read_read_read_read", "N-0705"),
    ("AI_WILL_SLOP", "C-114514"),
]

# Cifrados de output.txt
guest_ciphers = [
    "c3c8593c1adc1add7df8c32c549f785f67d6d3a86d486c4fa22322fe0c9848cfa7e66ae8bf2c0890bc6bf92f2a5dd1b971c73dd03b6593f0142f053b6bb64ac86d7a1d511690f30d81ca56ff87c98c701f3c0129f9bce7912924609baf0d0baae3989b7530f77542e69116cc",
    "c3c8593c1adc1add7df8c32c549f785f67d6d3a86d486c4fa22322fe0c9848cfa7e66ae8bf2c0890bc6bf92f2a5dd1b971c73dd01d5ea8d25833157a3daf1cc6752b2c1d5285f91bebcb44a3da8ecb7e07700b33f6f1a49338226fd4a1420da9f5d0836a60e1",
    "c3c8593c1adc1add7df8c32c549f785f67d6d3a86d486c4fa22322fe0c9848cfa7e66ae8bf2c0890bc6bf92f2a5dd1b971c73dd0277e8fe2257c5f683491068b3b56165507d6965dac860292c79fcf3862200b3cf8c1afd62d2e5586b34c1b9df4dd8d7e1dee634bedbe46d4ce749d41ce8f61118d060becd997309da64e9e5799b1625d333bd783837104cf82f6b1da7a7d613364771111a4688f1d6002b454315f2041d6a77749f11b19",
    "c3c8593c1adc1add7df8c32c549f785f67d6d3a86d486c4fa22322fe0c9848cfa7e66ae8bf2c0890bc6bf92f2a5dd1b971c73dd0125fb9c633537b560b8227b46d255a4307d3bd0df3c525e084cb9a690c664c71bef0b2c7296830d6b34315adff98987227bc7145fb8a47d9c060e04e",
]

admin_cipher = "c3c8593c1adc1add7df8c32c549f785f67d6d3a86d486c4fa22322fe0c9848cfa7e66ae8bf2a1998a671f92f2a5dd1b971c73dd03c6481f014764d6c2aec44c63c6c19444088eb7d86a832ef99d8c03349374c67beeeafda23386380af0d1ea1e5dd9f6962fb744be79551d58d3ce055c78f626cc54124c0c8a62e9ff51eed1ed9ad361e6332c1a09b1e069787a1f19c4b7c2620753f6c06f93595162e0bfe4c"


def make_guest_ticket(name, seat):
    """Reconstruye el ticket de invitado tal como se genera en chall.py"""
    return json.dumps({
        "event": "modern-crypto-101",
        "role": "guest",
        "name": name,
        "seat": seat,
        "note": "enjoy the workshop"
    }, separators=(",", ":")).encode()


# Usamos el guest_2 (índice 2) porque tiene el nombre más largo
name, seat = ATTENDEES[2]
plaintext = make_guest_ticket(name, seat)
ciphertext = bytes.fromhex(guest_ciphers[2])

print("[+] Plaintext conocido:")
print(f"    {plaintext.decode()}")
print(f"    Longitud: {len(plaintext)} bytes\n")

# Recuperamos el keystream: keystream = plaintext XOR ciphertext
keystream = xor(plaintext, ciphertext[:len(plaintext)])
print(f"[+] Keystream recuperado: {len(keystream)} bytes\n")

# Desciframos el ticket de admin: admin_plain = admin_cipher XOR keystream
admin_bytes = bytes.fromhex(admin_cipher)
admin_plain = xor(admin_bytes[:len(keystream)], keystream)

print("[+] Ticket de administrador descifrado:")
print(f"    {admin_plain.decode()}")

Instalación de dependencias
bash

pip install pwntools

O alternativamente sin dependencias:
python

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

keystream = xor_bytes(plaintext, ciphertext[:len(plaintext)])
admin_plain = xor_bytes(admin_bytes[:len(keystream)], keystream)

🎯 Resultado

Al ejecutar el script obtenemos:
json

{"event":"modern-crypto-101","role":"admin","name":"organizer","seat":"ROOT","note":"priority access granted","flag":"NHNC{...}"}

📚 Conceptos Aprendidos
1. AES-CTR (Counter Mode)

    Convierte un cifrador de bloque en un cifrador de flujo

    Genera un keystream independiente del plaintext

    La seguridad requiere que el nonce sea único por mensaje

2. Nonce Reuse Attack

    Es una vulnerabilidad crítica en cifradores de flujo

    Permite recuperar el keystream si se conoce un texto plano

    Compromete la confidencialidad de todos los mensajes

3. Known-Plaintext Attack (KPA)

    Ataque donde el adversario conoce parte del texto plano

    Muy efectivo contra cifradores de flujo con keystream reutilizado

    No requiere conocer la clave secreta

🛡️ ¿Cómo Prevenirlo?

    NUNCA reutilizar un nonce con la misma clave en AES-CTR

    Usar nonces aleatorios generados con Crypto.Random.get_random_bytes()

    Alternativamente, usar modos de operación que incluyan autenticación como AES-GCM

    Implementar un contador o usar secrets module para generar nonces únicos

Código seguro:
python

def encrypt(ticket):
    nonce = get_random_bytes(8)  # Nonce único por mensaje
    cipher = AES.new(KEY, AES.MODE_CTR, nonce=nonce)
    ciphertext = cipher.encrypt(ticket)
    return nonce + ciphertext  # Prependemos el nonce para descifrar

🏁 Conclusión

Este reto demuestra por qué la reutilización de nonces en AES-CTR es catastrófica para la seguridad. Un atacante con conocimiento parcial del texto plano puede recuperar completamente el keystream y descifrar todos los demás mensajes cifrados con el mismo par (clave, nonce), sin necesidad de conocer la clave secreta.

Flag: NHNC{*********************************}
