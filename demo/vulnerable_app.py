"""Demo: an AI-generated app with typical slop. DO NOT USE IN PROD (that's the point)."""
import hashlib
import pickle
import subprocess
import eval_helper  # noqa
import requests

AWS_ACCESS_KEY_ID = "AKIAEXAMPLEEXAMPLE12"
OPENAI_API_KEY = "sk-proj-abc123def456ghi789jkl012mno345pqr678"
password = "SuperSecretPassword123"


def run_command(user_input):
    # Vibe coded in 30 seconds, never tested
    subprocess.run("ls " + user_input, shell=True)


def get_user(db, username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return db.execute(query)


def load_state(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)


def hash_password(pw):
    return hashlib.md5(pw.encode()).hexdigest()


def fetch_remote(url):
    return requests.get(url, verify=False)


def process(data):
    try:
        result = eval(data)
        return result
    except Exception:
        pass


def big_function(a, b, c):
    # TODO: refactor this monster
    x = a + b + c
    x = x * 2
    x = x - 1
    print("debug", x)
    return x
