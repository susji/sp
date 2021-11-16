#!/usr/bin/env python3

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from urllib.parse import urlparse
from base64 import (urlsafe_b64decode, urlsafe_b64encode, standard_b64encode as
                    be, standard_b64decode as bd)
import argparse
import sys
import json
import requests


def b64_urlraw_decode(enc):
    return urlsafe_b64decode(enc + '=' * (4 - len(enc) % 4))


def b64_urlraw_encode(dec):
    return urlsafe_b64encode(dec).replace(b"=", b"")


def ppoint(content):
    print(f"  * {content}")


def pheader(name):
    print()
    print(name)
    print("-" * len(name))


def api_extract_blob(endpoint):
    pheader("Fetch")
    ppoint(f"endpoint={endpoint}")
    r = requests.get(endpoint)
    if r.status_code != 200:
        raise RuntimeError(f"failed fetching blob, got {r}")
    ppoint(f"=> got blob of {len(r.text)} bytes")
    nonce, ciphertext = r.text.split("|")
    return nonce, ciphertext


def decrypt(nonce, ciphertext, key):
    pheader("Decrypt")
    ppoint(f"nonce={len(nonce)}")
    ppoint(f"ciphertext={len(ciphertext)}")
    ppoint(f"key={len(key)}")
    cipher = AES.new(key, AES.MODE_GCM, nonce)
    return cipher.decrypt_and_verify(ciphertext[:-16], ciphertext[-16:])


def extract_jwk(key):
    pheader("Key extraction")
    res = json.loads(key)
    assert res["alg"] == "A128GCM"
    dec = b64_urlraw_decode(res["k"])
    ppoint(f"=> got key of {len(dec)} bytes")
    return dec


def fetch():
    u = urlparse(input("Give fetch URL: "))
    ident, key = u.fragment.split(",")
    endpoint = f"{u.scheme}://{u.netloc}/{ident}"
    nonce, ciphertext = api_extract_blob(endpoint)
    plaintext = decrypt(bd(nonce), bd(ciphertext), extract_jwk(bd(key)))
    print("--")
    print(plaintext.decode())


def encrypt(plaintext):
    pheader("Encrypt")
    key = get_random_bytes(16)
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
    ciphertext = ciphertext + tag
    ppoint(f"key_len={len(key)}")
    ppoint(f"nonce_len={len(nonce)}")
    ppoint(f"cipher={cipher}")
    ppoint(f"ciphertext+tag={be(ciphertext)}")
    return key, nonce, ciphertext


def post(endpoint, ciphertext):
    r = requests.post(endpoint, data=ciphertext)
    if r.status_code != 200:
        raise RuntimeError(f"post failed: {r.status_code}")
    ppoint(f"paste ID={r.text}")
    return r.text


def generate_jwk(rawkey):
    return json.dumps({
        "alg": "A128GCM",
        "ext": True,
        "k": b64_urlraw_encode(rawkey).decode("utf-8"),
        "key_ops": ["decrypt", "encrypt"],
        "kty": "oct"
    })


def submit():
    u = urlparse(input("Give backend address: "))
    endpoint = f"{u.scheme}://{u.netloc}{u.path}"
    print(endpoint)

    plaintext = ""
    print("Give your paste and end with Ctrl-D:")
    for line in sys.stdin:
        plaintext += line

    key, nonce, ciphertext = encrypt(plaintext)
    pid = post(endpoint, be(nonce).decode() + "|" + be(ciphertext).decode())
    jwk = generate_jwk(key)
    ppoint(f"Your decryption anchor: #{pid},{be(jwk.encode()).decode()}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Submit and fetch encrypted `sp` pastes.")
    p.add_argument("mode", type=str, help="Either 'submit' or 'fetch'")
    args = p.parse_args()

    if args.mode == "fetch":
        fetch()
    elif args.mode == "submit":
        submit()
    else:
        print(f"Unrecognized mode: {args.mode}")
