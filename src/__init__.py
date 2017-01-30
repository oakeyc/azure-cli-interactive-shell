
import sys
import subprocess

from app import create_shell
from az_completer import Az_Completer

def main(db):
    completer = Az_Completer()
    shell_app = create_shell(completer)
    # shell_app.run()
    shell_app.run(db)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        db = ':memory:'
    else:
        db = sys.argv[1]
    main(db)