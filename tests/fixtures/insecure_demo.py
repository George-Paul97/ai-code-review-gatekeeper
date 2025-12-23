# This file intentionally contains insecure patterns for CI gate demo.
# It should be removed or fixed before merge.

def insecure():
    return eval("2 + 2")  # intentionally unsafe for demo
