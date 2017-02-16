from azure.clishell.configuration import Configuration
from azure.clishell._dump_commands import dump_command_table
dump_command_table() # order of imports

from azure.clishell.app import Shell
from azure.clishell.az_completer import AzCompleter
from azure.clishell.az_lexer import AzLexer

def main():
    """ the main function """
    config = Configuration()
    if config.get_lexer() == 'AzLexer':
        lexer = AzLexer
    else:
        lexer = None
    completer = AzCompleter()
    shell_app = Shell(completer=completer, lexer=lexer)
    shell_app.run()

if __name__ == '__main__':
    main()
