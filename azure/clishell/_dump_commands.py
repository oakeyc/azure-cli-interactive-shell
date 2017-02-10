from __future__ import print_function

import argparse
import inspect
import json
import re
import types
import os
import sys

from azure.cli.core.application import APPLICATION, Application
from azure.cli.core.application import Configuration
from azure.cli.core.commands import CliArgumentType
# import azure.cli.core
# from azure.cli.core.commands import load_params
from importlib import import_module

from collections import OrderedDict, defaultdict

import azure.cli.core._help as _help
app = APPLICATION
command_module_map = {}
config = Configuration([])
cmd_table = config.get_command_table()

class Exporter(json.JSONEncoder):

    def default(self, o):#pylint: disable=method-hidden
        try:
            return super(Exporter, self).default(o)
        except TypeError:
            return str(o)

def load_params(command):
    try:
        cmd_table[command].load_arguments()
    except KeyError:
        return
    command_module = command_module_map.get(command, None)
    if not command_module:
        # logger.debug("Unable to load commands for '%s'. No module in command module map found.",
        #              command)  # pylint: disable=line-too-long
        return
    module_to_load = command_module[:command_module.rfind('.')]
    import_module(module_to_load).load_params(command)
    _update_command_definitions(cmd_table)

def _dump_command_table(**kwargs):
    cmd_table = APPLICATION.configuration.get_command_table()

    cmd_list = []
    if cmd_set_names is None :
        # if no command prefix specified, use all command table entries
        cmd_list = list(cmd_table.keys())
    else:
        # if the command name matches a prefix, add it to the output list
        for name in cmd_table.keys():
            for prefix in cmd_set_names:
                if name.startswith(prefix):
                    cmd_list.append(name)
                    break

    filtered_cmd_list = []
    param_dict = {k : [] for k in param_names} if param_names else {}
    if param_names:
        for cmd_name in cmd_list:
            table_entry = cmd_table[cmd_name]
            table_entry.arguments.update(table_entry.arguments_loader())
            cmd_args = list(table_entry.arguments.keys())
            for arg in cmd_args:
                if arg in param_names:
                    param_dict[arg].append(cmd_name)
                    if cmd_name not in filtered_cmd_list:
                        filtered_cmd_list.append(cmd_name)
    else:
        filtered_cmd_list = cmd_list

    table_entries = []
    for cmd_name in filtered_cmd_list:
        table_entry = cmd_table[cmd_name]
        table_entry.arguments.update(table_entry.arguments_loader())

    param_file = open("../cache_ish/params_dump.txt", 'w')
    help = open("../cache_ish/help_dump.txt", 'w')
    for cmd in cmd_table:
        config.load_params(cmd)
        descrip = cmd_table[cmd].description

        param_file.write(cmd + "|")
        for key in cmd_table[cmd].arguments:
            param_file.write(str(cmd_table[cmd].arguments[key].options_list[0]) + " ")
            if cmd_table[cmd].arguments[key].type.settings.get('required'):
                param_file.write("* [REQUIRED] ")
            else:
                param_file.write("* ")
            if cmd_table[cmd].arguments[key].type.settings.get('help'):
                param_file.write(cmd_table[cmd].arguments[key].type.settings.get('help') + " ")
        param_file.write("\n")


        help.write(cmd + ":" + str(descrip) + "\n")
    help.close()
    param_file.close()
    sys.exit(0)

def _get_cli_argument(command, argname):
    return _cli_argument_registry.get_cli_argument(command, argname)


def _get_cli_extra_arguments(command):
    return _cli_extra_argument_registry[command].items()


def _update_command_definitions(command_table_to_update):
    for command_name, command in command_table_to_update.items():
        for argument_name in command.arguments:
            overrides = _get_cli_argument(command_name, argument_name)
            command.update_argument(argument_name, overrides)

        # Add any arguments explicitly registered for this command
        for argument_name, argument_definition in _get_cli_extra_arguments(command_name):
            command.arguments[argument_name] = argument_definition
            command.update_argument(argument_name, _get_cli_argument(command_name, argument_name))

class _ArgumentRegistry(object):
    def __init__(self):
        self.arguments = defaultdict(lambda: {})

    def register_cli_argument(self, scope, dest, argtype, **kwargs):
        argument = CliArgumentType(overrides=argtype,
                                   **kwargs)
        self.arguments[scope][dest] = argument

    def get_cli_argument(self, command, name):
        parts = command.split()
        result = CliArgumentType()
        for index in range(0, len(parts) + 1):
            probe = ' '.join(parts[0:index])
            override = self.arguments.get(probe, {}).get(name, None)
            if override:
                result.update(override)
        return result

_cli_argument_registry = _ArgumentRegistry()
_cli_extra_argument_registry = defaultdict(lambda: {})

def _get_parameter_scope(param, cmd_list): 
    if not cmd_list:
        return 'N/A (NOT FOUND)'
    test_list = cmd_list[0].split(' ')
    while len(test_list) > 0:
        test_entry = ' '.join(test_list)
        all_match = True
        for entry in cmd_list[1:]:
            if test_entry not in entry:
                all_match = False
                break
        if not all_match:
            test_list.pop()
        else:
            return test_entry
    return '_ROOT_'

def _dashed_to_camel(string):
    return string.replace('-', '_')

parser = argparse.ArgumentParser(description='Command Table Parser')
parser.add_argument('--commands', metavar='N', nargs='+', help='Filter by first level command (OR)')
parser.add_argument('--params', metavar='N', nargs='+', help='Filter by parameters (OR)')
parser.add_argument('--hide-nulls', action='store_true', default=False, help='Show null entries')
args = parser.parse_args()
cmd_set_names = args.commands
param_names = [_dashed_to_camel(x) for x in args.params or []]

hide_nulls = args.hide_nulls

PRIMITIVES = (str, int, bool, float)
IGNORE_ARGS = ['help', 'help_file', 'base_type', 'arguments_loader']
sys.argv = sys.argv[:1]

APPLICATION.register(Application.COMMAND_PARSER_LOADED, _dump_command_table)

APPLICATION.execute([])