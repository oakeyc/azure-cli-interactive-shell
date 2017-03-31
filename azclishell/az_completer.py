""" a completer for the commands and parameters """
from __future__ import absolute_import, division, print_function, unicode_literals

import azclishell.configuration
from azclishell.argfinder import ArgsFinder
from azclishell.layout import get_scope
from azclishell.util import parse_quotes

from azure.cli.core.parser import AzCliCommandParser
from azure.cli.core._util import CLIError

from prompt_toolkit.completion import Completer, Completion


SELECT_SYMBOL = azclishell.configuration.SELECT_SYMBOL
GLOBAL_PARAM = ['--output', '-o', '--verbose', '--debug']
OUTPUT_CHOICES = ['json', 'tsv', 'table', 'jsonc']
OUTPUT_OPTIONS = ['--output', '-o']


class AzCompleter(Completer):
    """ Completes Azure CLI commands """

    def __init__(self, commands, global_params=True):
        # dictionary of command to descriptions
        self.command_description = commands.descrip
        # from a command to a list of parameters
        self.command_parameters = commands.command_param
        # a list of all the possible parameters
        self.completable_param = commands.completable_param
        # the command tree
        self.command_tree = commands.command_tree
        # a dictionary of parameter (which is command + " " + parameter name)
        # to a description of what it does
        self.param_description = commands.param_descript
        # a dictionary of command to examples of how to use it
        self.command_examples = commands.command_example
        # a dictionary of which parameters mean the same thing
        self.same_param_doubles = commands.same_param_doubles or {}

        self._is_command = True

        self.branch = self.command_tree
        self.curr_command = ""

        if not global_params:
            global GLOBAL_PARAM, OUTPUT_CHOICES, OUTPUT_OPTIONS
            GLOBAL_PARAM = []
            OUTPUT_CHOICES = []
            OUTPUT_OPTIONS = []

        self.global_parser = AzCliCommandParser(add_help=False)
        self.global_parser.add_argument_group('global', 'Global Arguments')
        self.parser = AzCliCommandParser(parents=[self.global_parser])

        from azclishell._dump_commands import CMD_TABLE
        self.cmdtab = CMD_TABLE
        self.parser.load_command_table(CMD_TABLE)
        self.argsfinder = ArgsFinder(self.parser)

    def validate_completion(self, param, words, text_before_cursor, double=True):
        """ validates that a param should be completed """
        double_flag = True
        if double:
            if param in self.same_param_doubles:
                double_flag = self.same_param_doubles[param] not in text_before_cursor.split()
        return param.lower().startswith(words.lower()) and \
                param.lower() != words.lower() and\
                param not in text_before_cursor.split()\
                and not text_before_cursor[-1].isspace()\
                and double_flag

    def dynamic_param_logic(self, text):
        """ validates parameter values for dynamic completion """
        is_param = False
        started_param = False
        prefix = ""
        param = ""
        if text.split():
            param = text.split()[-1]
            if param.startswith("-"):
                is_param = True
            elif len(text.split()) > 2 and text.split()[-2]\
            and text.split()[-2].startswith('-'):
                is_param = True
                param = text.split()[-2]
                started_param = True
                prefix = text.split()[-1]
        return is_param, started_param, prefix, param

    def reformat_cmd(self, text):
        """ reformat the text to be stripped of noise """
        # remove az if there
        text = text.replace('az', '')
        # disregard defaulting symbols
        if SELECT_SYMBOL['default'] in text:
            text = text.replace(SELECT_SYMBOL['default'], "")

        if SELECT_SYMBOL['undefault'] in text:
            text = text.replace(SELECT_SYMBOL['undefault'], "")

        if get_scope():
            text = get_scope() + ' ' + text
        return text

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        self.branch = self.command_tree
        self.curr_command = ''
        self._is_command = True

        text = self.reformat_cmd(text)

        if text.split():
            for comp in self.gen_cmd_and_param_completions(text):
                yield comp

        for cmd in self.gen_cmd_completions(text):
            yield cmd

        for val in self.gen_dynamic_completions(text):
            yield val

    def gen_dynamic_completions(self, text):
        """ generates the dynamic values, like the names of resource groups """
        try:
            is_param, started_param, prefix, param = self.dynamic_param_logic(text)

            # dynamic param completion
            arg_name = ""
            if self.curr_command in self.cmdtab:
                if is_param: # finding the name of the arg
                    for arg in self.cmdtab[self.curr_command].arguments:

                        for name in self.cmdtab[self.curr_command].arguments[arg].options_list:
                            if name == param:
                                arg_name = arg
                                break

                        if arg_name:
                            break

                    if arg_name and (text.split()[-1].startswith('-') or\
                    text.split()[-2].startswith('-')):
                        try:  # if enum completion
                            for choice in self.cmdtab[
                                    self.curr_command].arguments[arg_name].choices:
                                if started_param:
                                    if choice.lower().startswith(prefix.lower())\
                                    and choice not in text.split():
                                        yield Completion(choice, -len(prefix))
                                else:
                                    yield Completion(choice, -len(prefix))

                        except TypeError: # there is no choices option
                            pass

                        parse_args = self.argsfinder.get_parsed_args(
                            parse_quotes(text, quotes=False))

                        # there are 3 formats for completers the cli uses
                        # this try catches which format it is
                        if self.cmdtab[self.curr_command].arguments[arg_name].completer:
                            try:
                                for comp in self.cmdtab[self.curr_command].\
                                arguments[arg_name].completer(prefix=prefix, action=None,\
                                parser=None, parsed_args=parse_args):

                                    for comp in self.gen_dyn_completion(
                                            comp, started_param, prefix, text):
                                        yield comp

                            except TypeError:
                                try:
                                    for comp in self.cmdtab[self.curr_command].\
                                    arguments[arg_name].completer(prefix):

                                        for comp in self.gen_dyn_completion(
                                                comp, started_param, prefix, text):
                                            yield comp
                                except TypeError:
                                    try:
                                        for comp in self.cmdtab[self.curr_command].\
                                        arguments[arg_name].completer():

                                            for comp in self.gen_dyn_completion(
                                                    comp, started_param, prefix, text):
                                                yield comp

                                    except TypeError:
                                        print("TypeError: " + TypeError.message)

            global_params = self.gen_global_param_completions(text)
            for param in global_params:
                yield param
        except CLIError:  # if the user isn't logged in
            pass

    def gen_dyn_completion(self, comp, started_param, prefix, text):
        """ how to validate and generate completion for dynamic params """
        if len(comp.split()) > 1:
            completion = '\"' + comp + '\"'
        else:
            completion = comp
        if started_param:
            if comp.lower().startswith(prefix.lower())\
                and comp not in text.split():
                yield Completion(completion, -len(prefix))
        else:
            yield Completion(completion, -len(prefix))

    def gen_cmd_completions(self, text):
        """ whether is a space or no text typed, send the current branch """
        # if nothing, so first level commands
        if not text.split() and self._is_command:
            if self.branch.children is not None:
                for com in self.branch.children:
                    yield Completion(com.data)

        # if space show current level commands
        elif len(text.split()) > 0 and text[-1].isspace() and self._is_command:
            if self.branch is not self.command_tree:
                for com in self.branch.children:
                    yield Completion(com.data)

    def gen_cmd_and_param_completions(self, text):
        """ generates command and parameter completions """

        for words in text.split():
            # this is for single char parameters
            if words.startswith("-") and not words.startswith("--"):
                self._is_command = False

                if self.has_parameters(self.curr_command):
                    for param in self.command_parameters[self.curr_command]:
                        if self.validate_completion(param, words, text) and\
                        not param.startswith("--"):
                            yield Completion(param, -len(words), display_meta=\
                            self.get_param_description(
                                self.curr_command + " " + str(param)).replace('\n', ''))
            # for regular parameters
            elif words.startswith("--"):
                self._is_command = False

                if self.has_parameters(self.curr_command):  # Everything should, map to empty list
                    for param in self.command_parameters[self.curr_command]:
                        if self.validate_completion(param, words, text):
                            yield Completion(
                                param, -len(words),
                                display_meta=self.get_param_description(
                                    self.curr_command + " " + str(param)).replace('\n', ''))
            else:  # otherwises it's a command
                if self.branch.has_child(words):
                    self.branch = self.branch.get_child(words, self.branch.children)
                    if self._is_command:
                        if self.curr_command:
                            self.curr_command += " " + str(words)
                        else:
                            self.curr_command += str(words)

        if self.branch.children is not None and self._is_command: # all underneath commands
            for kid in self.branch.children:
                if self.validate_completion(kid.data, text.split()[-1], text, False):
                    yield Completion(str(kid.data),\
                        -len(text.split()[-1]))

    def gen_global_param_completions(self, text):
        """ Global parameter stuff hard-coded in """
        if text.split() and len(text.split()) > 0:
            for param in GLOBAL_PARAM:
                if text.split()[-1].startswith('-') \
                    and not text.split()[-1].startswith('--') and \
                    param.startswith('-') and not param.startswith('--') and\
                    self.validate_completion(param, text.split()[-1], text, double=False):
                    yield Completion(param, -len(text.split()[-1]))

                elif text.split()[-1].startswith('--') and \
                    self.validate_completion(param, text.split()[-1], text, double=False):
                    yield Completion(param, -len(text.split()[-1]))

            if text.split()[-1] in OUTPUT_OPTIONS:
                for opt in OUTPUT_CHOICES:
                    yield Completion(opt)
            if len(text.split()) > 1 and\
            text.split()[-2] in OUTPUT_OPTIONS:
                for opt in OUTPUT_CHOICES:
                    if self.validate_completion(opt, text.split()[-1], text, double=False):
                        yield Completion(opt, -len(text.split()[-1]))

    def is_completable(self, symbol):
        """ whether the word can be completed as a command or parameter """
        return self.has_parameters(symbol) or symbol in self.param_description.keys()

    def get_param_description(self, param):
        """ gets a description of an empty string """
        if param in self.param_description:
            return self.param_description[param]
        else:
            return ""

    def has_parameters(self, command):
        """ returns whether given command is valid """
        return command in self.command_parameters.keys()

    def has_description(self, param):
        """ if a parameter has a description """
        return param in self.param_description.keys() and \
        not self.param_description[param].isspace()
