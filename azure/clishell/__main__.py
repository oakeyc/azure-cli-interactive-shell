import os
from azure.clishell.configuration import Configuration, get_config_dir
from azure.clishell._dump_commands import dump_command_table
dump_command_table() # order of imports
from prompt_toolkit.history import FileHistory

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
    # with open(os.path.join(get_config_dir(), config.get_history), 'a') as history_file:
    completer = AzCompleter()
    shell_app = Shell(
        completer=completer,
        lexer=lexer,
        history=FileHistory(os.path.join(get_config_dir(), config.get_history())))
    shell_app.run()

if __name__ == '__main__':
    main()
