"""Planted flaws: TLS + weak hash. Expected: verify-false, weak-hash."""
import hashlib
import requests

def fetch(url):
    return requests.get(url, verify=False)

def hash_pw(pw):
    return hashlib.md5(pw.encode()).hexdigest()
