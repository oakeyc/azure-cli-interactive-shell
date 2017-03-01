import os
from prompt_toolkit.history import FileHistory


import azure.clishell.configuration
from azure.clishell._dump_commands import dump_command_table
dump_command_table() # order of imports

from azure.clishell.gather_commands import GatherCommands
from azure.clishell.app import Shell
from azure.clishell.az_completer import AzCompleter
from azure.clishell.az_lexer import AzLexer

import azure.cli.core.azlogging as azlogging
import azure.cli.core.telemetry as telemetry
import azure.cli.core.telemetry as telemetry
from azure.cli.core.application import APPLICATION, Configuration
from azure.cli.core._session import ACCOUNT, CONFIG, SESSION
from azure.cli.core._util import (show_version_info_exit, handle_exception)
from azure.cli.core._environment import get_config_dir
from azure.cli.core.application import APPLICATION

AZCOMPLETER = AzCompleter(GatherCommands())
CONFIGURATION = azure.clishell.configuration.CONFIGURATION

# logger = azlogging.get_az_logger(__name__)

def main():
    """ the main function """

    # azure_folder = CONFIGURATION.get_config_dir()
    # if not os.path.exists(azure_folder):
    #     os.makedirs(azure_folder)
    # ACCOUNT.load(os.path.join(azure_folder, 'azureProfile.json'))
    # CONFIG.load(os.path.join(azure_folder, 'az.json'))
    # SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)
    # 


    config = CONFIGURATION
    if config.get_lexer() == 'AzLexer':
        lexer = AzLexer
    else:
        lexer = None
    if config.config.get('DEFAULT', 'firsttime') is 'yes':
        APPLICATION.execute(["login"])
        APPLICATION.execute(["configure"])
        config.firsttime()

    shell_app = Shell(
        completer=AZCOMPLETER,
        lexer=lexer,
        history=FileHistory(os.path.join(get_config_dir(), config.get_history())),
        app=APPLICATION,
    )

    shell_app.run()

if __name__ == '__main__':
    main()
