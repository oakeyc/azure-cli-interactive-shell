import os

import azure.clishell._dump_commands
from azure.clishell.app import create_shell
from azure.clishell.az_completer import AzCompleter
from azure.clishell.az_lexer import AzLexer
from azure.clishell.configuration import Configuration

def main():
    """ the main function """

    config = Configuration()
    if config.get_lexer() == 'AzLexer':
        lexer = AzLexer
    else:
        lexer = None
    completer = AzCompleter()
    shell_app = create_shell(completer, lexer)
    shell_app.run()

if __name__ == '__main__':
    main()
