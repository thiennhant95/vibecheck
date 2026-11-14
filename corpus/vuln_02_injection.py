"""Planted flaws: injection. Expected: shell-true, sql-injection."""
import subprocess

def run_cmd(user_input):
    subprocess.run("ls " + user_input, shell=True)

def get_user(db, username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return db.execute(query)
