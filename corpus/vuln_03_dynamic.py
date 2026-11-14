"""Planted flaws: unsafe deserialization/execution. Expected: pickle-load, yaml-unsafe-load, eval-exec."""
import pickle
import yaml

def load_state(f):
    return pickle.load(f)

def load_config(s):
    return yaml.load(s)

def compute(data):
    return eval(data)
