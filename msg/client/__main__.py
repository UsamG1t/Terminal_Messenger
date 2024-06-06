"""Start client."""
from . import start_client
import sys


if len(sys.argv) == 1:
    print("You need to write username.")
    quit(1)

username = sys.argv[1]

start_client(username)
