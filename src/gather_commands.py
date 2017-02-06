from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion
import math
from command_tree import CommandBranch, CommandHead, CommandTree
import argcomplete
import azure.cli.core.azlogging as azlogging

from azure.cli.core.parser import AzCliCommandParser, enable_autocomplete
from azure.cli.core.application import _explode_list_args
from azure.cli.core.application import Configuration
from azure.cli.core.application import APPLICATION, Application

app = APPLICATION


class GatherCommands(object):
    def __init__(self):
        # everything that is completable
        self.completable = []
        # a completable to the description of what is does
        self.descrip = {}
        # from a command to a list of parameters
        self.param_dict = {}
        self.current_comamand = ""
        self.last_option = ""

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

        self.param_dict["quit"] = ""
        self.param_dict["exit"] = ""

    def gather_from_files(self):
        command = open("dump.txt", 'r')
        help_file = open("help_dump.txt", 'r')
        param = open("params_dump.txt", 'r')

        for line in command:
            for word in line.split():
                if word not in self.completable:
                    self.completable.append(word)

            branch = self.command_tree
            for sing_word in line.split():
                if branch.children is None:
                    branch.children = []
                if not branch.has_child(sing_word):
                    branch.children.append(CommandBranch(sing_word))
                branch = branch.get_child(sing_word, branch.children)

        # add exiting
        self.add_exit()

        for line in help_file:
            description = line.partition(":")[2]
            description_with_newline = description
            if len(description) > 50:
                for num in range(int(math.ceil(len(description) / 60))):
                    index = (num + 1) * 60
                    while index < len(description) and \
                    not description_with_newline[index].isspace():
                        index += 1
                    description_with_newline = description_with_newline[:index] + "\n" \
                    + description_with_newline[index + 1:]
            self.descrip[line.partition(":")[0]] = description_with_newline

        for line in param:
            key = str(line.partition("|")[0])
            args = []
            if "*" in line:
                  # if there is a help
                name_to_description = line.partition("|")[2]
                name = ""
                param_description = False
                description = ""
                for symbol in name_to_description.split():
                    if symbol.startswith('[required]') or symbol.startswith("--"):
                        args.append(symbol)

                        if description != "" and name != "":
                            self.param_descript[name] = description
                            description = ""
                        name = symbol.replace("[required]", "")

                        if name not in self.completable_param:
                            self.completable_param.append(name)
                        param_description = False

                    elif symbol.startswith("*"):
                        param_description = True
                    elif param_description:
                        description += symbol + " "
                # for arg in line.partition("|")[2].partition("*")[2].split():
                #     args += str(arg) + "\n"
                #     self.descrip[arg] = str(line.partition("|")[2].partition("*")[2])
                # self.param_dict[key] = args
            else:
                for arg in line.partition("|")[2].split():
                    param_no_res = arg.replace("[required]", "")
                    if param_no_res not in self.completable_param:
                        self.completable_param.append(param_no_res)

                    args.append(arg)
                    self.descrip[arg] = ""
            self.param_dict[key] = args

        self.completer = WordCompleter(words=self.completable,\
         sentence=True, meta_dict=self.param_descript)

        command.close()
        help_file.close()
        param.close()
