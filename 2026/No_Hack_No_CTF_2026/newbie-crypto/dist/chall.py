from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import json


KEY = get_random_bytes(16)
NONCE = b"ticket42"
FLAG = "NHNC{REDACTED}"

ATTENDEES = [
    ("hsuan0223x", "H-0223"),
    ("NHNC", "T-0704"),
    (
        "this_chal_not_need_read_read_read_read_read_read_read_read_read_read_read",
        "N-0705",
    ),
    ("AI_WILL_SLOP", "C-114514"),
]


def encode_ticket(ticket):
    return json.dumps(ticket, separators=(",", ":")).encode()


def make_guest_ticket(name, seat):
    return encode_ticket(
        {
            "event": "modern-crypto-101",
            "role": "guest",
            "name": name,
            "seat": seat,
            "note": "enjoy the workshop",
        }
    )


def make_admin_ticket():
    return encode_ticket(
        {
            "event": "modern-crypto-101",
            "role": "admin",
            "name": "organizer",
            "seat": "ROOT",
            "note": "priority access granted",
            "flag": FLAG,
        }
    )


def encrypt(ticket):
    cipher = AES.new(KEY, AES.MODE_CTR, nonce=NONCE)
    return cipher.encrypt(ticket).hex()


def main():
    for index, (name, seat) in enumerate(ATTENDEES):
        print(f"guest_cipher_{index} = {encrypt(make_guest_ticket(name, seat))}")
    print(f"admin_cipher = {encrypt(make_admin_ticket())}")


if __name__ == "__main__":
    main()
