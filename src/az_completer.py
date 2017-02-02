from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completer
import math
from command_tree import CommandBranch, CommandHead, CommandTree

class AzCompleter(Completer):
    """ Completes Azure CLI commands """
    def __init__(self):
        # everything that is completable
        self.words = []
        # a completable to the description of what is does
        self.descrip = {}
        # from a command to a list of parameters
        self.param_dict = {}
        self.current_comamand = ""
        self.last_option = ""
        self.command_tree = CommandHead()
        self.gather_from_files()

    def gather_from_files(self):
        command = open("dump.txt", 'r')
        help_file = open("help_dump.txt", 'r')
        param = open("params_dump.txt", 'r')

        for line in command:
            self.words.append(line.strip("\n"))
            branch = self.command_tree
            for sing_word in line.split():
                if branch.children is None or sing_word not in branch.children:
                    branch.children = []
                    branch.children.append(CommandBranch(sing_word))
                branch = branch.get_child(sing_word, branch.children)

        # add exiting
        self.words.append("quit")
        self.words.append("exit")

        self.descrip["quit"] = "Exits the program"
        self.descrip["exit"] = "Exits the program"

        self.command_tree.children.append("quit").append("exit")

        self.param_dict["quit"] = ""
        self.param_dict["exit"] = ""

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
            args = ""
            if "*" in line:  # if there is a help
                for arg in line.partition("|")[2].split():
                    args += str(arg) + "\n"
                    self.descrip[arg] = str(line.partition("|")[2])
                self.param_dict[key] = args
            else:
                for arg in line.partition("|")[2].split():
                    args += str(arg) + "\n"
                    self.descrip[arg] = ""
                self.param_dict[key] = args

        # for key in self.param_dict:
        #     for arg in self.param_dict[key]:
        #         self.words.append(arg)

        # for key in self.words:
        #     print key

        self.completer = WordCompleter(words=self.words, sentence=True)

        command.close()
        help_file.close()
        param.close()

    def get_completions(self, document, complete_event):
        return self.completer.get_completions(document, complete_event)

    def is_completable(self, command):
        """ whether the command can be completed """
        return command in self.words

    def get_param(self, command):
        """ returns the parameters for a given command """
        return self.param_dict[command]

    def get_description(self, command):
        """ returns the description for a given command """
        return self.descrip[command]

    def is_command(self, command):
        """ returns whether given command is valid """
        return command in self.param_dict.keys()
        