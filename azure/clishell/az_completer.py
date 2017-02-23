import math
import os
import argcomplete
import sys

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion
from azure.cli.core.parser import AzCliCommandParser
from azure.cli.core.application import APPLICATION, Application, Configuration
from azure.clishell.gather_commands import GatherCommands

from azure.clishell.completion_finder import CompletionFinder, FilesCompleter
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

from azure.cli.core.application import APPLICATION
import os, sys, argparse, contextlib
from argcomplete import completers, my_shlex as shlex
from argcomplete.compat import USING_PYTHON2, str, sys_encoding, ensure_str, ensure_bytes
from argcomplete.completers import FilesCompleter
from argcomplete.my_argparse import IntrospectiveArgumentParser, action_is_satisfied, action_is_open, action_is_greedy


class AzCompleter(Completer):
    """ Completes Azure CLI commands """
    def __init__(self):
        commands = GatherCommands()
        # a completable to the description of what is does
        self.command_description = commands.descrip
        self.completable = commands.completable
        # from a command to a list of parameters
        self.command_parameters = commands.command_param
        self.completable_param = commands.completable_param

        self.command_tree = commands.command_tree
        self.param_description = commands.param_descript
        self.command_examples = commands.command_example



        self.global_parser = AzCliCommandParser(prog='az', add_help=False)
        global_group = self.global_parser.add_argument_group('global', 'Global Arguments')
        # self.raise_event(self.GLOBAL_PARSER_CREATED, global_group=global_group)

        self.parser = AzCliCommandParser(prog='az', parents=[self.global_parser])
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


        self.parser.load_command_table(cmd_table)
        argcomplete.autocomplete = CompletionFinder(self.parser, \
        validator=lambda c, p: c.lower().startswith(p.lower()),
                                 default_completer=lambda _: ())
        # argcomplete.autocomplete(self.parser, \
        # validator=lambda c, p: c.lower().startswith(p.lower()),
        #                          default_completer=lambda _: ())


        # print("completions for: %r" % line)

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        command = ""
        is_command = True
        branch = self.command_tree
        flip = False
        # if text_before_cursor.split():
        #     for words in text_before_cursor.split():
        #         if words.startswith("!"):
        #             flip = True

        # if flip:
        line = text_before_cursor
        complete = CompletionFinder()
        completions = complete(self.parser, \
        validator=lambda c, p: c.lower().startswith(p.lower()),\
                                 default_completer=lambda _: (),
                                 line=line)
        # comp_line = text_before_cursor
        # comp_point = len(text_before_cursor) - len(text_before_cursor.split()[-1])
        # comp_point = len(comp_line.encode(sys_encoding)[:comp_point].decode(sys_encoding))

        # (cword_prequote, cword_prefix, cword_suffix,
        #  comp_words, first_colon_pos) = argcomplete.split_line(line)
        # completions = argcomplete.autocomplete._get_completions(
        #     comp_words, cword_prefix, cword_prequote, first_colon_pos)

        if completions:
            for comp in completions:
                yield Completion(comp, -len(comp))





    def is_completable(self, command):
        """ whether the command can be completed """
        return self.has_parameters(command) or command in self.param_description.keys()

    def get_param(self, command):
        """ returns the parameters for a given command """
        return self.command_parameters[command]

    def get_param_description(self, param):
        """ gets a description of an empty string """
        if param in self.param_description:
            return self.param_description[param]
        else:
            return ""

    def get_description(self, command):
        """ returns the description for a given command """
        return self.command_description[command]

    def has_parameters(self, command):
        """ returns whether given command is valid """
        return command in self.command_parameters.keys()

    def get_all_subcommands(self):
        """ returns all the subcommands """
        subcommands = []
        for command in self.command_description:
            for word in command.split():
                for kid in self.command_tree.children:
                    if word != kid.data and word not in subcommands:
                        subcommands.append(word)
        return subcommands

    def has_description(self, param):
        """ if a parameter has a description """
        return param in self.param_description.keys() and \
        not self.param_description[param].isspace()
