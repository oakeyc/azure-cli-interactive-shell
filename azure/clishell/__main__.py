import azure.clishell._dump_commands
from azure.clishell.app import create_shell
from azure.clishell.az_completer import AzCompleter

def main():
    """ the main function """

    completer = AzCompleter()
    shell_app = create_shell(completer)
    shell_app.run()

if __name__ == '__main__':
    main()
