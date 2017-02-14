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
from azure.cli.core.commands import load_params, _update_command_definitions

from azure.clishell.configuration import get_config_dir

from collections import OrderedDict, defaultdict


root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '../'))


def dump_command_table():
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

    param_file = open(get_cache_dir() + "/params_dump.txt", 'w')
    command_help = open(get_cache_dir() + "/help_dump.txt", 'w')
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
    # sys.exit(0)


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

def get_cache_dir():
    azure_folder = get_config_dir()
    cache_path = os.path.join(azure_folder, 'cache')
    if not os.path.exists(azure_folder):
        os.makedirs(azure_folder)
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    return cache_path

dump_command_table()