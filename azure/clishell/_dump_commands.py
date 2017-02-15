from __future__ import print_function

import argparse
import inspect
import json
import re
import os
import pkgutil
import sys
import types
import json

from importlib import import_module

from azure.cli.core.application import APPLICATION, Application
from azure.cli.core.application import Configuration
from azure.cli.core.commands import CliArgumentType
from azure.cli.core.commands import load_params, _update_command_definitions

from azure.clishell.configuration import get_config_dir, Configuration

from collections import OrderedDict, defaultdict


def dump_command_table():
    cmd_table = APPLICATION.configuration.get_command_table()
    command_file = Configuration().get_help_files()

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

    data = {}
    com_descip = {}
    for cmd in cmd_table:
        param_descrip = {}
        com_descip['help'] = cmd_table[cmd].description

        for key in cmd_table[cmd].arguments:
            required = None
            help_desc = None
            if cmd_table[cmd].arguments[key].type.settings.get('required'):
                required = "[REQUIRED]"
            if cmd_table[cmd].arguments[key].type.settings.get('help'):
                help_desc = cmd_table[cmd].arguments[key].type.settings.get('help')

            param_descrip[cmd_table.arguements[key].options_list[0]] = {
                'required' : required,
                'help' : help_desc
            }

        com_descip['parameters'] = param_descrip
        data[cmd] = com_descip

    with open(get_cache_dir() + "/" + str(command_file), 'w') as help_file:
        json.dump(com_descip, help_file)

def get_cache_dir():
    """ gets the location of the cache """
    azure_folder = get_config_dir()
    cache_path = os.path.join(azure_folder, 'cache')
    if not os.path.exists(azure_folder):
        os.makedirs(azure_folder)
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    return cache_path
