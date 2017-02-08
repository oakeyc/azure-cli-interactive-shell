
import sys
import subprocess

from app import create_shell
from az_completer import AzCompleter
import dump_commands

def main(db):
    """ the main function """
    completer = AzCompleter()
    shell_app = create_shell(completer)
    shell_app.run(db)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        db = ':memory:'
    else:
        db = sys.argv[1]
    main(db)
