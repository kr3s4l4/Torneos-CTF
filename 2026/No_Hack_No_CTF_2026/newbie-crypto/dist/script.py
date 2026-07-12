from pwn import xor
import json

# Textos planos conocidos
ATTENDEES = [
    ("hsuan0223x", "H-0223"),
    ("NHNC", "T-0704"),
    ("this_chal_not_need_read_read_read_read_read_read_read_read_read_read_read", "N-0705"),
    ("AI_WILL_SLOP", "C-114514"),
]

guest_ciphers = [
    "c3c8593c1adc1add7df8c32c549f785f67d6d3a86d486c4fa22322fe0c9848cfa7e66ae8bf2c0890bc6bf92f2a5dd1b971c73dd03b6593f0142f053b6bb64ac86d7a1d511690f30d81ca56ff87c98c701f3c0129f9bce7912924609baf0d0baae3989b7530f77542e69116cc",
    "c3c8593c1adc1add7df8c32c549f785f67d6d3a86d486c4fa22322fe0c9848cfa7e66ae8bf2c0890bc6bf92f2a5dd1b971c73dd01d5ea8d25833157a3daf1cc6752b2c1d5285f91bebcb44a3da8ecb7e07700b33f6f1a49338226fd4a1420da9f5d0836a60e1",
    "c3c8593c1adc1add7df8c32c549f785f67d6d3a86d486c4fa22322fe0c9848cfa7e66ae8bf2c0890bc6bf92f2a5dd1b971c73dd0277e8fe2257c5f683491068b3b56165507d6965dac860292c79fcf3862200b3cf8c1afd62d2e5586b34c1b9df4dd8d7e1dee634bedbe46d4ce749d41ce8f61118d060becd997309da64e9e5799b1625d333bd783837104cf82f6b1da7a7d613364771111a4688f1d6002b454315f2041d6a77749f11b19",
    "c3c8593c1adc1add7df8c32c549f785f67d6d3a86d486c4fa22322fe0c9848cfa7e66ae8bf2c0890bc6bf92f2a5dd1b971c73dd0125fb9c633537b560b8227b46d255a4307d3bd0df3c525e084cb9a690c664c71bef0b2c7296830d6b34315adff98987227bc7145fb8a47d9c060e04e",
]

admin_cipher = "c3c8593c1adc1add7df8c32c549f785f67d6d3a86d486c4fa22322fe0c9848cfa7e66ae8bf2a1998a671f92f2a5dd1b971c73dd03c6481f014764d6c2aec44c63c6c19444088eb7d86a832ef99d8c03349374c67beeeafda23386380af0d1ea1e5dd9f6962fb744be79551d58d3ce055c78f626cc54124c0c8a62e9ff51eed1ed9ad361e6332c1a09b1e069787a1f19c4b7c2620753f6c06f93595162e0bfe4c"


def encode_ticket(ticket):
    return json.dumps(ticket, separators=(",", ":")).encode()


# Usamos el guest_2 que es el más largo
name, seat = ATTENDEES[2]
plaintext = encode_ticket({
    "event": "modern-crypto-101",
    "role": "guest",
    "name": name,
    "seat": seat,
    "note": "enjoy the workshop",
})

print(f"Plaintext: {plaintext.decode()}")
print(f"Longitud plaintext: {len(plaintext)}")

ciphertext = bytes.fromhex(guest_ciphers[2])
admin_bytes = bytes.fromhex(admin_cipher)

print(f"Longitud ciphertext guest_2: {len(ciphertext)}")
print(f"Longitud admin_cipher: {len(admin_bytes)}")

# XOR para obtener keystream
keystream = xor(plaintext, ciphertext[:len(plaintext)])

# Descifrar admin
admin_plain = xor(admin_bytes[:len(keystream)], keystream)

print(f"\nAdmin ticket (primeros {len(keystream)} bytes):")
print(admin_plain)
