""" main function """
from __future__ import print_function
import os
from prompt_toolkit.history import FileHistory

import azclishell.configuration
from azclishell._dump_commands import dump_command_table
dump_command_table() # because need to write to files before read them
from azclishell.gather_commands import GatherCommands
from azclishell.app import Shell
from azclishell.az_completer import AzCompleter
from azclishell.az_lexer import AzLexer

import azure.cli.core.azlogging as azlogging
import azure.cli.core.telemetry as telemetry
from azure.cli.core.application import APPLICATION, Configuration
from azure.cli.core._session import ACCOUNT, CONFIG, SESSION
from azure.cli.core._util import (show_version_info_exit, handle_exception)
from azure.cli.core._environment import get_config_dir as cli_config_dir
from azure.cli.core.application import APPLICATION

AZCOMPLETER = AzCompleter(GatherCommands())
CONFIGURATION = azclishell.configuration.CONFIGURATION

def main():
    """ the main function """

    azure_folder = cli_config_dir()
    if not os.path.exists(azure_folder):
        os.makedirs(azure_folder)

    ACCOUNT.load(os.path.join(azure_folder, 'azureProfile.json'))
    CONFIG.load(os.path.join(azure_folder, 'az.json'))
    SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)

    config = CONFIGURATION

    if config.BOOLEAN_STATES[config.config.get('DEFAULT', 'firsttime')]:
        # APPLICATION.execute(["configure"])
        print("When in doubt, ask for 'help'")
        config.firsttime()

    shell_app = Shell(
        completer=AZCOMPLETER,
        lexer=AzLexer,
        history=FileHistory(os.path.join(CONFIGURATION.get_config_dir(), config.get_history())),
        app=APPLICATION,
        # cli_config=os.path.join(azure_folder, 'config')
    )
    shell_app.run()

if __name__ == '__main__':
    main()
