from os import system

if system("mypy main.py --ignore-missing-imports --disallow-untyped-defs"):
    exit(1)
