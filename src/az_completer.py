from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion
import math
from command_tree import CommandBranch, CommandHead, CommandTree
from azure.cli.core.parser import AzCliCommandParser, enable_autocomplete

class AzCompleter(Completer):
    """ Completes Azure CLI commands """
    def __init__(self):
        # everything that is completable
        self.completable = []
        # a completable to the description of what is does
        self.descrip = {}
        # from a command to a list of parameters
        self.param_dict = {}
        self.current_comamand = ""
        self.last_option = ""
        self.command_tree = CommandHead()
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
            self.completable.append(line.strip("\n"))

            branch = self.command_tree
            for sing_word in line.split():
                if branch.children is None or sing_word not in branch.children:
                    branch.children = []
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
            args = ""
            if "*" in line:  # if there is a help
                for arg in line.partition("|")[2].split():
                    args += str(arg) + "\n"
                    self.descrip[arg] = str(line.partition("|")[2])
                self.param_dict[key] = args
            else:
                for arg in line.partition("|")[2].split():
                    param_no_res = arg.replace("[required]", "")
                    if param_no_res not in self.completable:
                        self.completable.append(param_no_res)

                    args += str(arg) + "\n"
                    self.descrip[arg] = ""
            self.param_dict[key] = args

        # for key in self.param_dict:
        #     for arg in self.param_dict[key]:
        #         self.words.append(arg)

        # for key in self.words:
        #     print key

        self.completer = WordCompleter(words=self.completable, sentence=True)

        command.close()
        help_file.close()
        param.close()

    def get_completions(self, document, complete_event):
        # self.global_parser = AzCliCommandParser(prog='az', add_help=False)
        # self.parser = AzCliCommandParser(prog='az', parents=[self.global_parser])
        
        # text_before_cursor = document.text_before_cursor
        # if self.is_command(text_before_cursor.split()[0]):
        #     # text = text_before_cursor.split()
        #     # text = ' '.join(text)
        #     for word in self.command_tree.get_subbranch(text_before_cursor):
        #         yield Completion(word)

        return self.completer.get_completions(document, complete_event)

    def is_completable(self, command):
        """ whether the command can be completed """
        return command in self.completable

    def get_param(self, command):
        """ returns the parameters for a given command """
        return self.param_dict[command]

    def get_description(self, command):
        """ returns the description for a given command """
        return self.descrip[command]

    def is_command(self, command):
        """ returns whether given command is valid """
        return command in self.param_dict.keys()
        