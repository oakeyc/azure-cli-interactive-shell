import os
from azure.clishell.configuration import Configuration, get_config_dir
from azure.clishell._dump_commands import dump_command_table
dump_command_table() # order of imports
from prompt_toolkit.history import FileHistory

from azure.clishell.app import Shell
from azure.clishell.az_completer import AzCompleter
from azure.clishell.az_lexer import AzLexer

from azure.cli.core.application import Application

def main():
    """ the main function """
    app = Application()

    config = Configuration()
    if config.get_lexer() == 'AzLexer':
        lexer = AzLexer
    else:
        lexer = None
    if config.config.get('DEFAULT', 'firsttime') is 'yes':
        app.execute(["login"])
        app.execute(["configure"])
        config.firsttime()

    completer = AzCompleter()
    shell_app = Shell(
        completer=completer,
        lexer=lexer,
        history=FileHistory(os.path.join(get_config_dir(), config.get_history())),
        app=app
    )

    # app.execute(["vm", "list"])
    shell_app.run()

if __name__ == '__main__':
    main()
