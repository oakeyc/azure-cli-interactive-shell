import math
import os
# import argcomplete
import sys
import json
import os
import pkgutil
# import yaml
import os, sys, argparse, contextlib

from importlib import import_module
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion

from argcomplete import CompletionFinder, completers, my_shlex as shlex
from argcomplete.compat import USING_PYTHON2, str, sys_encoding, ensure_str, ensure_bytes
from argcomplete.completers import FilesCompleter
from argcomplete.my_argparse import IntrospectiveArgumentParser, action_is_satisfied, action_is_open, action_is_greedy

from azure.cli.core.parser import AzCliCommandParser

from azure.cli.core.application import APPLICATION, Application, Configuration
from azure.clishell.gather_commands import GatherCommands

from azure.clishell.completion_finder import CompletionFinder as MyCompleterFinder, FilesCompleter
from azure.cli.core.application import APPLICATION, Application, Configuration
from azure.cli.core.commands import CliArgumentType
from azure.cli.core.commands import load_params, _update_command_definitions
from azure.clishell.configuration import get_config_dir, Configuration
from azure.cli.core.help_files import helps
from azure.cli.core.application import APPLICATION
import os
from azure.clishell.configuration import Configuration as ShellConfig, get_config_dir
from azure.clishell._dump_commands import dump_command_table
dump_command_table() # order of imports
from prompt_toolkit.history import FileHistory

from azure.clishell.app import Shell
from azure.clishell.az_completer import AzCompleter
from azure.clishell.az_lexer import AzLexer
from azure.cli.core.application import APPLICATION, Configuration
import azure.cli.core.azlogging as azlogging
from azure.cli.core._session import ACCOUNT, CONFIG, SESSION
from azure.cli.core._util import (show_version_info_exit, handle_exception)
from azure.cli.core._environment import get_config_dir
import azure.cli.core.telemetry as telemetry

from azure.cli.core.application import APPLICATION
# import azure.cli.core._profile 

def main(args):

    azure_folder = get_config_dir()
    if not os.path.exists(azure_folder):
        os.makedirs(azure_folder)
    ACCOUNT.load(os.path.join(azure_folder, 'azureProfile.json'))
    CONFIG.load(os.path.join(azure_folder, 'az.json'))
    SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)

    global_parser = AzCliCommandParser(prog='az', add_help=False)
    global_group = global_parser.add_argument_group('global', 'Global Arguments')
    # self.raise_event(self.GLOBAL_PARSER_CREATED, global_group=global_group)

    parser = AzCliCommandParser(prog='az', parents=[global_parser])
    cmd_table = APPLICATION.configuration.get_command_table()
    for cmd in cmd_table:
        cmd_table[cmd].load_arguments()

    try:
        mods_ns_pkg = import_module('azure.cli.command_modules')
        installed_command_modules = [modname for _, modname, _ in
                                     pkgutil.iter_modules(mods_ns_pkg.__path__)]
    except ImportError:
        pass
    for mod in installed_command_modules:
        # print('loading params for', mod)
        try:
            import_module('azure.cli.command_modules.' + mod).load_params(mod)
        except Exception as ex:
            print("EXCPETION: " + ex.message)
    _update_command_definitions(cmd_table)
    parser.load_command_table(cmd_table)

    complete = MyCompleterFinder()
    # print(self.pars ?/der.__dict__)
    # args = args[1:]
    # args = " ".join(arg for arg in args)
    args = "az vm c"
    print(args)

    completions = complete(parser, \
    validator=lambda c, p: c.lower().startswith(p.lower()),\
                                default_completer=lambda _: (), line=args)
    # print(completions)
    for cmd in cmd_table:
        com_descip = {}
        param_descrip = {}
        com_descip['help'] = cmd_table[cmd].description
        com_descip['examples'] = ""

        for key in cmd_table[cmd].arguments:
            if cmd_table[cmd].arguments[key].completer:
                continue

    print(cmd_table['cloud show'].arguments['cloud_name'].completer("AzureU", None, 'cloud show -n'))
    # print(parser.parse_args('vm create'.split()))

    sys.exit(0)
if __name__ == '__main__':
    main(sys.argv)
