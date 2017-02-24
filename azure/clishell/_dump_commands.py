from __future__ import print_function

import json
import os
import pkgutil
import yaml
from importlib import import_module

from azure.cli.core.application import APPLICATION, Application, Configuration
from azure.cli.core.commands import CliArgumentType
from azure.cli.core.commands import load_params, _update_command_definitions
from azure.clishell.configuration import get_config_dir, Configuration
from azure.cli.core.help_files import helps


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
    for cmd in cmd_table:
        com_descip = {}
        param_descrip = {}
        com_descip['help'] = cmd_table[cmd].description
        com_descip['examples'] = ""

        for key in cmd_table[cmd].arguments:
            required = ""
            help_desc = ""
            if cmd_table[cmd].arguments[key].type.settings.get('required'):
                required = "[REQUIRED]"
            if cmd_table[cmd].arguments[key].type.settings.get('help'):
                help_desc = cmd_table[cmd].arguments[key].type.settings.get('help')

            name_options = []
            for name in cmd_table[cmd].arguments[key].options_list:
                name_options.append(name)

            options = {
                'name' : name_options,
                'required' : required,
                'help' : help_desc
            }
            param_descrip[cmd_table[cmd].arguments[key].options_list[0]] = options

        com_descip['parameters'] = param_descrip
        data[cmd] = com_descip

    for cmd in helps:
        diction_help = yaml.load(helps[cmd])
        if "short-summary" in diction_help:
            if cmd in data:
                data[cmd]['help'] = diction_help["short-summary"]
            else:
                data[cmd] = {
                    'help': diction_help["short-summary"],
                    'parameters' : {}
                }

        if "parameters" in diction_help:
            for param in diction_help["parameters"]:
                if param["name"].split()[0] not in data[cmd]['parameters']:
                    options = {
                        'name' : name_options,
                        'required' : required,
                        'help' : help_desc
                    }
                    data[cmd]['parameters'] = {
                        param["name"].split()[0]: options
                    }
                if "short-summary" in param:
                    data[cmd]['parameters'][param["name"].split()[0]]['help']\
                     = param["short-summary"]
        if "examples" in diction_help:
            string_example = ""
            for name in diction_help["examples"]:
                for prop in name:
                    string_example += name[prop] + "\n"
            data[cmd]['examples'] = string_example


    with open(os.path.join(get_cache_dir(), command_file), 'w') as help_file:
        json.dump(data, help_file)

def get_cache_dir():
    """ gets the location of the cache """
    azure_folder = get_config_dir()
    cache_path = os.path.join(azure_folder, 'cache')
    if not os.path.exists(azure_folder):
        os.makedirs(azure_folder)
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    return cache_path