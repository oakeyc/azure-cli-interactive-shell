import sys
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion

# import the command table

class Az_Completer(Completer):
    def __init__(self):
        words = []
        self.descrip = {}
        self.param_dict = {}
        self.current_comamand = ""
        self.last_option = ""

        command = open("dump.txt", 'r')
        meta = open("meta_dump.txt", 'r')
        param = open("params_dump.txt", 'r')

        for line in command:
            words.append(line.strip("\n"))
        words.append("quit")
        words.append("exit")

        self.descrip["quit"] = "Exits the program"
        self.descrip["exit"] = "Exits the program"
        for line in meta:
            com = ""
            description = ""
            desc = False
            for char in line:
                if char == ':':
                    desc = True
                elif desc:
                    description += char
                else:
                    com += char
            self.descrip[com] = description.strip("\n")

        for line in param:
            # list_of_args = str(line.partition(":")[2]).split()
            self.param_dict[str(line.partition(":")[0])] = str(line.partition(":")[2]).strip("\n")

        command.close()
        meta.close()
        param.close()

        self.completer = WordCompleter(words, False, self.param_dict, False, True, False)

    def get_completions(self, document, complete_event):
        return self.completer.get_completions(document, complete_event)

    def get_param(self, command):
        return self.param_dict[command]

    def get_description(self, command):
        return self.descrip[command]
        