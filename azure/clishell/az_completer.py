import math
import os
import argcomplete
import sys

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion
from azure.cli.core.parser import AzCliCommandParser
from azure.cli.core.application import APPLICATION, Application, Configuration
from azure.clishell.gather_commands import GatherCommands
from argcomplete import CompletionFinder, FilesCompleter

# class AzCompletionFinder(CompletionFinder):
#     def __call__(self, argument_parser, always_complete_options=True, exit_method=os._exit, output_stream=None,
#                 exclude=None, validator=None, print_suppressed=False, append_space=None,
#                 default_completer=FilesCompleter()):
#         """
#         :param argument_parser: The argument parser to autocomplete on
#         :type argument_parser: :class:`argparse.ArgumentParser`
#         :param always_complete_options:
#             Controls the autocompletion of option strings if an option string opening character (normally ``-``) has not
#             been entered. If ``True`` (default), both short (``-x``) and long (``--x``) option strings will be
#             suggested. If ``False``, no option strings will be suggested. If ``long``, long options and short options
#             with no long variant will be suggested. If ``short``, short options and long options with no short variant
#             will be suggested.
#         :type always_complete_options: boolean or string
#         :param exit_method:
#             Method used to stop the program after printing completions. Defaults to :meth:`os._exit`. If you want to
#             perform a normal exit that calls exit handlers, use :meth:`sys.exit`.
#         :type exit_method: callable
#         :param exclude: List of strings representing options to be omitted from autocompletion
#         :type exclude: iterable
#         :param validator:
#             Function to filter all completions through before returning (called with two string arguments, completion
#             and prefix; return value is evaluated as a boolean)
#         :type validator: callable
#         :param print_suppressed:
#             Whether or not to autocomplete options that have the ``help=argparse.SUPPRESS`` keyword argument set.
#         :type print_suppressed: boolean
#         :param append_space:
#             Whether to append a space to unique matches. The default is ``True``.
#         :type append_space: boolean
#         .. note::
#             If you are not subclassing CompletionFinder to override its behaviors,
#             use ``argcomplete.autocomplete()`` directly. It has the same signature as this method.
#         Produces tab completions for ``argument_parser``. See module docs for more info.
#         Argcomplete only executes actions if their class is known not to have side effects. Custom action classes can be
#         added to argcomplete.safe_actions, if their values are wanted in the ``parsed_args`` completer argument, or
#         their execution is otherwise desirable.
#         """
#         self.__init__(argument_parser, always_complete_options=always_complete_options, exclude=exclude,
#                       validator=validator, print_suppressed=print_suppressed, append_space=append_space,
#                       default_completer=default_completer)

#         comp_line = os.environ["COMP_LINE"]
#         comp_point = int(os.environ["COMP_POINT"])

#         # Adjust comp_point for wide chars
#         # if USING_PYTHON2:
#         #     comp_point = len(comp_line[:comp_point].decode(sys_encoding))
#         # else:
#         comp_point = len(comp_line.encode(sys_encoding)[:comp_point].decode(sys_encoding))

#         comp_line = ensure_str(comp_line)
#         cword_prequote, cword_prefix, cword_suffix, comp_words, last_wordbreak_pos = split_line(comp_line, comp_point)

#         # _ARGCOMPLETE is set by the shell script to tell us where comp_words
#         # should start, based on what we're completing.
#         # 1: <script> [args]
#         # 2: python <script> [args]
#         # 3: python -m <module> [args]
#         start = int(os.environ["_ARGCOMPLETE"]) - 1
#         comp_words = comp_words[start:]

#         return self._get_completions(comp_words, cword_prefix, cword_prequote, last_wordbreak_pos)

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

        cmd_table = APPLICATION.configuration.get_command_table()
        self.parser = AzCliCommandParser()
        self.parser.load_command_table(cmd_table)
        argcomplete.autocomplete = CompletionFinder()
        argcomplete.autocomplete(self.parser, \
        validator=lambda c, p: c.lower().startswith(p.lower()),
                                 default_completer=lambda _: ())


    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        command = ""
        branch = self.command_tree
        if text_before_cursor.split():
            # args = self.parser.parse_args()
            # ## TODO 
            # parameter = text_before_cursor.split()[-1].replace("--", "")
            # args.parameter.completer(prefix=text_before_cursor.split()[-1],\
            # parsed_args=text_before_cursor.text.rsplit(' ', 1)[0]())

            # end = False
            # for opts in args:
            #     if opts.completer:
            #         yield Completion("THE NAME OF THINGS")
            #         end = True
            # if end:
            #     return
            ## Param

            for words in text_before_cursor.split():
                if words.startswith("-"):
                    if self.has_parameters(command[:-1]): # gets rid of the trailing whitespace
                        for param in self.get_param(command[:-1]):
                            if param.lower().startswith(words.lower()) and \
                            param.lower() != words.lower():
                                yield Completion(param, -len(words))
                    else:
                        for param in self.completable_param:
                            if param.lower().startswith(words.lower()) and \
                            param.lower() != words.lower():
                                yield Completion(param, -len(words))
                else:
                    command += words + " "
                    try:
                        if branch.has_child(words):
                            branch = branch.get_child(words, branch.children)
                    except ValueError:
                        continue # do something

            if branch.children is not None:
                for kid in branch.children:
                    if kid.data.lower().startswith(text_before_cursor.split()[-1].lower()):
                        yield Completion(str(kid.data),
                                         -len(text_before_cursor.split()[-1]))

        if not text_before_cursor.split() or text_before_cursor[-1] == " ":
            if branch.children is not None:
                for com in branch.children:
                    yield Completion(com.data)


    def is_completable(self, command):
        """ whether the command can be completed """
        return self.has_parameters(command) or command in self.param_description.keys()

    def get_param(self, command):
        """ returns the parameters for a given command """
        return self.command_parameters[command]

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
