from __future__ import print_function

import argparse
import inspect
import json
import re
import os
import pkgutil
import sys
import types

from importlib import import_module

from azure.cli.core.application import APPLICATION, Application
from azure.cli.core.application import Configuration
from azure.cli.core.commands import CliArgumentType
# import azure.cli.core
from azure.cli.core.commands import load_params, _update_command_definitions

from collections import OrderedDict, defaultdict

import azure.cli.core._help as _help
# app = APPLICATION
# command_module_map = {}
# config = Configuration([])
# cmd_table = config.get_command_table()

class Exporter(json.JSONEncoder):

    def default(self, o):#pylint: disable=method-hidden
        try:
            return super(Exporter, self).default(o)
        except TypeError:
            return str(o)

def _dump_command_table(**kwargs):
    cmd_table = APPLICATION.configuration.get_command_table()


    cmd_list = []
    if cmd_set_names is None:
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


    for cmd in cmd_table:
        cmd_table[cmd].load_arguments()


    try:
        mods_ns_pkg = import_module('azure.cli.command_modules')
        installed_command_modules = [modname for _, modname, _ in
                                     pkgutil.iter_modules(mods_ns_pkg.__path__)]
    except ImportError:
        pass
    for mod in installed_command_modules:
        print('loading params for', mod)
        try:
            import_module('azure.cli.command_modules.' + mod).load_params(mod)
        except Exception as ex:
            print("EXCPETION: " + ex.message)
    _update_command_definitions(cmd_table)

    param_file = open("./.cache/params_dump.txt", 'w')
    command_help = open("./.cache/help_dump.txt", 'w')
    for cmd in cmd_table:
        # if (cmd )
        # config.load_params(cmd)
        # cmd_table[cmd].load_arguments()
        descrip = cmd_table[cmd].description

        param_file.write(cmd + "|")
        for key in cmd_table[cmd].arguments:
            param_file.write("**" + str(cmd_table[cmd].arguments[key].options_list[0]) + " ")
            if cmd_table[cmd].arguments[key].type.settings.get('required'):
                param_file.write("* [REQUIRED] ")
            else:
                param_file.write("* ")
            if cmd_table[cmd].arguments[key].type.settings.get('help'):
                param_file.write(cmd_table[cmd].arguments[key].type.settings.get('help') + " ")
        param_file.write("\n")


        command_help.write(cmd + ":" + str(descrip) + "\n")
    command_help.close()
    param_file.close()
    sys.exit(0)


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