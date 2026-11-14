"""Planted flaws that ONLY the AST layer catches (regex misses all of these).
Expected: eval-exec, except-pass.
"""
from builtins import eval as safe_eval  # aliased call


def calculate(expr):
    return safe_eval(  # multi-line call, alias
        expr
    )


def do_thing():
    try:
        risky()
    except ValueError:
        # silently swallowed, with a comment in between
        pass
