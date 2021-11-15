#!/usr/bin/env python3

from Crypto.Cipher import AES
from urllib.parse import urlparse
from base64 import urlsafe_b64decode as bd
import json
import requests


def b64_urldecode_raw(enc):
    return bd(enc + '=' * (4 - len(enc) % 4))


def pheader(name):
    print()
    print(name)
    print("-" * len(name))


def api_extract_blob(endpoint):
    pheader("Fetch")
    print(f"  [] endpoint={endpoint}")
    r = requests.get(endpoint)
    if r.status_code != 200:
        raise RuntimeError(f"failed fetching blob, got {r}")
    print(f"    => got blob of {len(r.text)} bytes.")
    nonce, ciphertext = r.text.split("|")
    return nonce, ciphertext


def decrypt(nonce, ciphertext, key):
    pheader("Decrypt")
    print(f"  [] nonce={len(nonce)}")
    print(f"  [] ciphertext={len(ciphertext)}")
    print(f"  [] key={len(key)}")
    cipher = AES.new(key, AES.MODE_GCM, nonce)
    return cipher.decrypt_and_verify(ciphertext[:-16], ciphertext[-16:])

    
def extract_jwk(key):
    pheader("Key extraction")
    res = json.loads(key)
    assert res["alg"] == "A128GCM"
    dec = b64_urldecode_raw(res["k"])
    print(f"    => got key of {len(dec)} bytes")
    return dec


if __name__ == "__main__":
    u = urlparse(input("Give fetch URL: "))
    ident, key = u.fragment.split(",")
    endpoint = f"{u.scheme}://{u.netloc}/{ident}"
    nonce, ciphertext = api_extract_blob(endpoint)
    plaintext = decrypt(bd(nonce), bd(ciphertext), extract_jwk(bd(key)))
    print("--")
    print(plaintext.decode())
    
