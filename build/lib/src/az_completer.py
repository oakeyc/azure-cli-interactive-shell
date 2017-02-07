from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion
import math
from gather_commands import GatherCommands

class AzCompleter(Completer):
    """ Completes Azure CLI commands """
    def __init__(self):
        commands = GatherCommands()
        # everything that is completable
        self.completable = commands.completable
        # a completable to the description of what is does
        self.descrip = commands.descrip
        # from a command to a list of parameters
        self.param_dict = commands.param_dict
        self.current_comamand = ""
        self.last_option = ""

        self.completable_param = commands.completable_param

        self.command_tree = commands.command_tree

        self.competer = commands.completer
        self.param_description = commands.param_descript

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        command = ""
        branch = self.command_tree
        if text_before_cursor.split():
            for words in text_before_cursor.split():
                if words.startswith("--"):
                    if self.is_command(command[:-1]): # gets rid of the trailing whitespace
                        for param in self.get_param(command[:-1]):
                            param = param.replace("[required]", "")
                            if param.lower().startswith(words.lower()) and \
                            param.lower() != words.lower():
                                yield Completion(param, -len(words))
                    else:
                        for param in self.completable_param:
                            param = param.replace("[required]", "")
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
                                         -len(text_before_cursor.split()[-1])) # this has a bug

        if not text_before_cursor.split() or text_before_cursor[-1] == " ":
            if branch.children is not None:
                for com in branch.children:
                    yield Completion(com.data)


    def is_completable(self, command):
        """ whether the command can be completed """
        return self.is_command(command) or command in self.completable_param

    def get_param(self, command):
        """ returns the parameters for a given command """
        return self.param_dict[command]

    def get_description(self, command):
        """ returns the description for a given command """
        return self.descrip[command]

    def is_command(self, command):
        """ returns whether given command is valid """
        return command in self.param_dict.keys()

    def get_all_subcommands(self):
        """ returns all the subcommands """
        subcommands = []
        for command in self.completable:
            for com in self.command_tree.children:
                if com.data != command:
                    subcommands.append(command)
        return subcommands

    def has_description(self, param):
        return param in self.param_description.keys()
