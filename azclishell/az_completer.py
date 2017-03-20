""" a completer for the commands and parameters """
from __future__ import print_function

from prompt_toolkit.completion import Completer, Completion
import azclishell.configuration
from azclishell.layout import default_command

from azure.cli.core.parser import AzCliCommandParser
from azure.cli.core._util import CLIError

SELECT_SYMBOL = azclishell.configuration.SELECT_SYMBOL
GLOBAL_PARAM = ['--output', '-o', '--verbose', '--debug']
OUTPUT_CHOICES = ['json', 'tsv', 'table', 'jsonc']
OUTPUT_OPTIONS = ['--output', '-o']

class AzCompleter(Completer):
    """ Completes Azure CLI commands """
    def __init__(self, commands):
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

        self.global_parser = AzCliCommandParser(prog='az', add_help=False)
        self.global_parser.add_argument_group('global', 'Global Arguments')
        self.parser = AzCliCommandParser(prog='az', parents=[self.global_parser])

        from azclishell._dump_commands import CMD_TABLE as cmd_table
        self.cmdtab = cmd_table
        self.parser.load_command_table(self.cmdtab)

    def validate_param_completion(self, param, words, text_before_cursor, double=True):
        """ validates that a param should be completed """
        double_flag = True
        if double:
            if param in self.same_param_doubles:
                double_flag = self.same_param_doubles[param] not in text_before_cursor.split()
        return param.lower().startswith(words.lower()) and \
                param.lower() != words.lower() and\
                param not in text_before_cursor.split()\
                and double_flag

    # def get_global_params(self, text):
    #     """ completions for global params """
    #     if text.split() and len(text.split()) > 1:
    #         for param in GLOBAL_PARAM:
    #             if self.validate_param_completion(param, text.split()[-1], text, double=False):
    #                 return Completion(param, -len(param))

    def get_completions(self, document, complete_event):
        try:
            text_before_cursor = document.text_before_cursor
            command = ""
            is_command = True
            branch = self.command_tree
            not_command = False
            if len(text_before_cursor.split()) > 0\
            and text_before_cursor.split()[0] == 'az': # remove optional az
                text_before_cursor = ' '.join(text_before_cursor.split()[1:])

            if SELECT_SYMBOL['default'] in text_before_cursor:
                text_before_cursor = text_before_cursor.replace(SELECT_SYMBOL['default'], "")
            if SELECT_SYMBOL['undefault'] in text_before_cursor:
                text_before_cursor = text_before_cursor.replace(SELECT_SYMBOL['undefault'], "")

            if default_command():
                # print(DEFAULT_COMMAND)
                text_before_cursor = default_command() + ' ' + text_before_cursor

            if text_before_cursor.split() and len(text_before_cursor.split()) > 0:
                for param in GLOBAL_PARAM:
                    if self.validate_param_completion(
                            param,
                            text_before_cursor[-len(param):],
                            text_before_cursor,
                            double=False):
                        yield Completion(param, -len(param))
                if text_before_cursor.split()[-1] in OUTPUT_OPTIONS:
                    for opt in OUTPUT_CHOICES:
                        yield Completion(opt)
                if len(text_before_cursor.split()) > 1 and\
                text_before_cursor.split()[-2] in OUTPUT_OPTIONS:
                    for opt in OUTPUT_CHOICES:
                        if self.validate_param_completion(
                                opt,
                                text_before_cursor[-len(opt):],
                                text_before_cursor,
                                double=False
                            ):
                            yield Completion(opt, -len(opt))

            if text_before_cursor.split():
                if text_before_cursor.split():
                    for words in text_before_cursor.split():
                        if words.startswith("-") and not words.startswith("--"):
                            is_command = False
                            if self.has_parameters(command):
                                for param in self.get_param(command):
                                    if self.validate_param_completion(
                                            param, words, text_before_cursor)\
                                    and not param.startswith("--"):
                                        yield Completion(param, -len(words), display_meta=\
                                        self.get_param_description(
                                            command + " " + str(param)).replace('\n', ''))

                        elif words.startswith("--"):
                            is_command = False
                            if self.has_parameters(command):  # Everything should, map to empty list
                                for param in self.get_param(command):
                                    if self.validate_param_completion(
                                            param, words, text_before_cursor):
                                        yield Completion(param, -len(words),\
                                        display_meta=self.get_param_description(
                                            command + " " + str(param)).replace('\n', ''))
                        else:
                            if is_command:
                                if command:
                                    command += " " + str(words)
                                else:
                                    command += str(words)
                            try:
                                if branch.has_child(words):
                                    branch = branch.get_child(words, branch.children)
                                elif text_before_cursor.split()[0] in SELECT_SYMBOL.values():
                                    # print('help')
                                    not_command = True
                            except ValueError:
                                continue # do something

                    if branch.children is not None and not not_command:
                        for kid in branch.children:
                            if kid.data.lower().startswith(
                                    text_before_cursor[-len(kid.data):].lower()):
                                yield Completion(str(kid.data),\
                                    -len(text_before_cursor.split()[-1]))

            if not text_before_cursor:
                if branch.children is not None:
                    for com in branch.children:
                        yield Completion(com.data)
            elif text_before_cursor[-1].isspace():
                if branch is not self.command_tree:
                    for com in branch.children:
                        yield Completion(com.data)

            is_param = False
            started_param = False
            prefix = ""
            param = ""
            if text_before_cursor.split():
                param = text_before_cursor.split()[-1]
                if param.startswith("-"):
                    is_param = True
                elif len(text_before_cursor.split()) > 2 and text_before_cursor.split()[-2]\
                and text_before_cursor.split()[-2].startswith('-'):
                    is_param = True
                    param = text_before_cursor.split()[-2]
                    started_param = True
                    prefix = text_before_cursor.split()[-1]

            arg_name = ""
            if command in self.cmdtab:
                if is_param:
                    for arg in self.cmdtab[command].arguments:
                        for name in self.cmdtab[command].arguments[arg].options_list:
                            if name == param:
                                arg_name = arg
                                break
                        if arg_name:
                            break
                    if arg_name and (text_before_cursor.split()[-1].startswith('-') or\
                    text_before_cursor.split()[-2].startswith('-')):
                        try:
                            for choice in self.cmdtab[command].arguments[arg_name].choices:
                                if started_param:
                                    if choice.lower().startswith(prefix.lower())\
                                    and choice not in text_before_cursor.split():
                                        yield Completion(choice, -len(prefix))
                                else:
                                    yield Completion(choice, -len(prefix))
                        except TypeError:
                            pass
                        if self.cmdtab[command].arguments[arg_name].completer:
                            try:
                                for comp in self.cmdtab[command].\
                                arguments[arg_name].completer(prefix=prefix, action=None,\
                                parser=self.parser, parsed_args=None):
                                    if started_param:
                                        if comp.lower().startswith(prefix.lower())\
                                            and comp not in text_before_cursor.split():
                                            yield Completion(comp, -len(prefix))
                                    else:
                                        yield Completion(comp, -len(prefix))
                            except TypeError:
                                try:
                                    for comp in self.cmdtab[command].\
                                    arguments[arg_name].completer(prefix):
                                        if started_param:
                                            if comp.lower().startswith(prefix.lower())\
                                                and comp not in text_before_cursor.split():
                                                yield Completion(comp, -len(prefix))
                                        else:
                                            yield Completion(comp, -len(prefix))
                                except TypeError:
                                    try:
                                        for comp in self.cmdtab[command].\
                                        arguments[arg_name].completer():
                                            if started_param:
                                                if comp.lower().startswith(prefix.lower())\
                                                    and comp not in text_before_cursor.split():
                                                    yield Completion(comp, -len(prefix))
                                            else:
                                                yield Completion(comp, -len(prefix))
                                    except TypeError:
                                        print("TypeError: " + TypeError.message)
        except CLIError:
            print("\nPlease login\n")
            # yield Completion('')


    def is_completable(self, symbol):
        """ whether the word can be completed as a command or parameter """
        return self.has_parameters(symbol) or symbol in self.param_description.keys()

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

    def has_description(self, param):
        """ if a parameter has a description """
        return param in self.param_description.keys() and \
        not self.param_description[param].isspace()
