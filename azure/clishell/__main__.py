import os
import sys
import subprocess

from app import create_shell
from az_completer import AzCompleter

def main(db):
    """ the main function """
    root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '../'))
  
    subprocess.Popen("python " + root_dir + "/_dump_commands.py", shell=True).communicate()

    completer = AzCompleter()
    shell_app = create_shell(completer)
    shell_app.run(db)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        db = ':memory:'
    else:
        db = sys.argv[1]
    main(db)
