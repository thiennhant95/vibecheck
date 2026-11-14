"""Clean code with tricky bait. Expected: ZERO findings.

Contains strings that LOOK like violations but are docs/regex/test data.
"""
import hashlib
import os
import subprocess

import requests

# Rule-of-thumb doc: never call eval() on user input, avoid shell=True,
# and don't write verify=False. Doc mentions of banned calls are fine here.
DOC = "To use: eval(x) is banned. subprocess with shell=True is banned."
EXAMPLE = "password = 'not-a-real-secret-value'"  # just example data
PATTERN = r"\b(eval|exec)\s*\("


def get_user(db, username):
    query = "SELECT * FROM users WHERE name = %s"
    return db.execute(query, (username,))


def run_ls(args):
    return subprocess.run(["ls"] + args, check=True)


def fetch(url):
    api_key = os.getenv("API_KEY")
    return requests.get(url, headers={"Authorization": f"Bearer {api_key}"}).text


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()
