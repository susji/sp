#!/usr/bin/env python3

from Crypto.Cipher import AES
from urllib.parse import urlparse
from base64 import urlsafe_b64decode as bd
import argparse
import json
import requests


def b64_urldecode_raw(enc):
    return bd(enc + '=' * (4 - len(enc) % 4))


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
    dec = b64_urldecode_raw(res["k"])
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


def submit():
    u = urlparse(input("Give backend address: "))
    endpoint = f"{u.scheme}://{u.netloc}"
    print(endpoint)


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
