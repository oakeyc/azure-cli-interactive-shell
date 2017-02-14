import math
import os

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion
from azure.clishell.command_tree import CommandBranch, CommandHead, CommandTree
from azure.clishell._dump_commands import get_cache_dir
root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), '../'))

TOLERANCE = 10
LINE_MINIMUM = 60

class GatherCommands(object):
    def __init__(self):
        # everything that is completable
        self.completable = []
        # a completable to the description of what is does
        self.descrip = {}
        # from a command to a list of parameters
        self.command_param = {}

        self.completable_param = []

        self.command_tree = CommandHead()
        self.param_descript = {}
        self.completer = None
        self.gather_from_files()

    def add_exit(self):
        self.completable.append("quit")
        self.completable.append("exit")

        self.descrip["quit"] = "Exits the program"
        self.descrip["exit"] = "Exits the program"

        self.command_tree.children.append(CommandBranch("quit"))
        self.command_tree.children.append(CommandBranch("exit"))

        self.command_param["quit"] = ""
        self.command_param["exit"] = ""

    def add_random_new_lines(self, long_phrase):
        if len(long_phrase) > LINE_MINIMUM:
            for num in range(int(math.ceil(len(long_phrase) / LINE_MINIMUM))):
                index = (num + 1) * LINE_MINIMUM
                while index < len(long_phrase) and \
                not long_phrase[index].isspace() and index < TOLERANCE + LINE_MINIMUM:
                    index += 1
                if index < len(long_phrase):
                    if long_phrase[index].isspace():
                        index += 1
                    long_phrase = long_phrase[:index] + "\n" \
                    + long_phrase[index:]
        return long_phrase

    def gather_from_files(self):
        help_file = open(get_cache_dir() + "/help_dump.txt", 'r')
        param = open(get_cache_dir() + "/params_dump.txt", 'r')

         # add exiting
        self.add_exit()

        for line in help_file:
            command = line.partition(":")[0]
            for word in command.split():
                if word not in self.completable:
                    self.completable.append(word)

            branch = self.command_tree
            for sing_word in command.split():
                if branch.children is None:
                    branch.children = []
                if not branch.has_child(sing_word):
                    branch.children.append(CommandBranch(sing_word))
                branch = branch.get_child(sing_word, branch.children)

            description = line.partition(":")[2]
            self.descrip[command] = self.add_random_new_lines(description)

        for line in param:
            command_name = str(line.partition("|")[0])
            all_params = []
            if "*" in line:  # if there is a help
                name_to_description = line.partition("|")[2]
                name = ""
                param_description = False
                description = ""
                suppress = False
                for symbol in name_to_description.split():
                    if symbol.startswith("**"):
                        symbol = symbol[2:]
                        all_params.append(symbol)
                        description = ""
                        suppress = False
                        param_description = False
                        name = symbol
                        if symbol not in self.completable_param:
                            self.completable_param.append(symbol)
                    elif symbol == "==SUPPRESS==":
                        # self.command_param.pop(name)
                        # self.param_descript.
                        all_params.remove(name)
                        self.param_descript.pop(command_name + " " + name, None)
                        suppress = True
                    elif symbol.startswith("*"):
                        param_description = True
                    elif param_description:
                        description += symbol + " "
                        if not suppress:
                            self.param_descript[command_name + " " + name] = description

            else:
                for arg in line.partition("|")[2].split():
                    if arg not in self.completable_param:
                        self.completable_param.append(arg)
                    all_params.append(arg)
                    self.descrip[arg] = ""
            self.command_param[command_name] = all_params

        for command_name in self.param_descript:
            self.param_descript[command_name] = \
            self.add_random_new_lines(self.param_descript[command_name])

        help_file.close()
        param.close()
