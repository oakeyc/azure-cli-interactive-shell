import os

from azure.clishell._dump_commands import dump_command_table
from azure.clishell.app import Shell
from azure.clishell.az_completer import AzCompleter
from azure.clishell.az_lexer import AzLexer
from azure.clishell.configuration import Configuration

def main():
    """ the main function """
    config = Configuration()
    dump_command_table()
    if config.get_lexer() == 'AzLexer':
        lexer = AzLexer
    else:
        lexer = None
    completer = AzCompleter()
    shell_app = Shell(completer=completer, lexer=lexer)
    shell_app.run()

if __name__ == '__main__':
    main()
