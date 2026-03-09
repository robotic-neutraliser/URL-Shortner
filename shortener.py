"""
shortener.py — Generates a short code for a given URL

How it works:
  1. Take the long URL
  2. Hash it using MD5 (produces a fixed-length fingerprint)
  3. Take the first 6 characters of that hash as the short code

Example:
  "https://www.google.com" → MD5 → "aa747c..." → short code = "aa747c"
"""

import hashlib


def generate_short_code(long_url: str) -> str:
    # Step 1: Encode the URL to bytes (required for hashing)
    url_bytes = long_url.encode("utf-8")

    # Step 2: Hash it with MD5 — always produces a 32-character hex string
    hash_hex = hashlib.md5(url_bytes).hexdigest()

    # Step 3: Take the first 6 characters as the short code
    short_code = hash_hex[:6]

    return short_code
