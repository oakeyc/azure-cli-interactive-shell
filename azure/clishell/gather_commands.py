import math
import os
import json

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion

from azure.clishell.command_tree import CommandBranch, CommandHead
import azure.clishell.configuration

CONFIGURATION = azure.clishell.configuration.CONFIGURATION
ROWS, COLS = os.popen('stty size', 'r').read().split()

TOLERANCE = 10
LINE_MINIMUM = math.floor(int(COLS) / 2 - 15)

class GatherCommands(object):
    """ grabs all the cached commands from files """
    def __init__(self):
        # everything that is completable
        self.completable = []
        # a completable to the description of what is does
        self.descrip = {}
        # from a command to a list of parameters
        self.command_param = {}

        self.completable_param = []
        self.command_example = {}
        self.command_tree = CommandHead()
        self.param_descript = {}
        self.completer = None
        self.same_param_doubles = {}

        self.gather_from_files()

    def add_exit(self):
        """ adds the exits from the application """
        self.completable.append("quit")
        self.completable.append("exit")

        self.descrip["quit"] = "Exits the program"
        self.descrip["exit"] = "Exits the program"

        self.command_tree.children.append(CommandBranch("quit"))
        self.command_tree.children.append(CommandBranch("exit"))

        self.command_param["quit"] = ""
        self.command_param["exit"] = ""

        self.completable.append("az")
        self.descrip["az"] = ""
        self.command_tree.children.append(CommandBranch("az"))
        self.command_param["az"] = ""

    def add_random_new_lines(self, long_phrase, line_min, tolerance=TOLERANCE):
        """ not everything fits on the screen, based on the size, add newlines """
        if long_phrase is None:
            return long_phrase
        if len(long_phrase) > line_min:
            for num in range(int(math.ceil(len(long_phrase) / line_min))):
                index = int((num + 1) * line_min)
                while index < len(long_phrase) and \
                not long_phrase[index].isspace() and index < tolerance + line_min:
                    index += 1
                if index < len(long_phrase):
                    if long_phrase[index].isspace():
                        index += 1
                    long_phrase = long_phrase[:index] + "\n" \
                    + long_phrase[index:]
        return long_phrase + "\n"

    def gather_from_files(self):
        """ gathers from the files in a way that is convienent to use """
        command_file = CONFIGURATION.get_help_files()
        cache_path = os.path.join(CONFIGURATION.get_config_dir(), 'cache')
        with open(os.path.join(cache_path, \
        command_file), 'r') as help_file:
            data = json.load(help_file)

        self.add_exit()
        commands = data.keys()

        for command in commands:
            branch = self.command_tree
            for word in command.split():
                if word not in self.completable:
                    self.completable.append(word)
                if branch.children is None:
                    branch.children = []
                if not branch.has_child(word):
                    branch.children.append(CommandBranch(word))
                branch = branch.get_child(word, branch.children)

            description = data[command]['help']
            self.descrip[command] = self.add_random_new_lines(description, LINE_MINIMUM)

            if 'examples' in data[command]:
                self.command_example[command] = self.add_random_new_lines(
                    data[command]['examples'], int(COLS))

            all_params = []
            for param in data[command]['parameters']:
                suppress = False

                if data[command]['parameters'][param]['help'] and \
                '==SUPPRESS==' in data[command]['parameters'][param]['help']:
                    suppress = True
                if data[command]['parameters'][param]['help'] and not suppress:
                    param_double = None
                    for par in data[command]['parameters'][param]['name']:
                        if not param_double:
                            param_double = par
                        else:
                            self.same_param_doubles[par] = param_double
                            self.same_param_doubles[param_double] = par

                        self.param_descript[command + " " + par] =  \
                        self.add_random_new_lines(data[command]['parameters'][param]['required']\
                        + " " + data[command]['parameters'][param]['help'], LINE_MINIMUM)
                        if par not in self.completable_param:
                            self.completable_param.append(par)
                        all_params.append(par)

            self.command_param[command] = all_params

    def get_all_subcommands(self):
        """ returns all the subcommands """
        subcommands = []
        for command in self.descrip:
            for word in command.split():
                for kid in self.command_tree.children:
                    if word != kid.data and word not in subcommands:
                        subcommands.append(word)
        return subcommands
