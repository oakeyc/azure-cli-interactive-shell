import sys
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer

# import the command table

class Az_Completer(Completer):
    def __init__(self):
        words = []
        d = {}
        param_dict = {}
        command = open("dump.txt", 'r')
        meta = open("meta_dump.txt", 'r')
        param = open("params_dump.txt", 'r')

        for line in command:
            words.append(line.strip("\n"))
        words.append("quit")
        words.append("exit")

        d["quit"] = "Exits the program"
        d["exit"] = "Exits the program"
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
            d[com] = description.strip("\n")

        for line in param:
            param_dict[str(line.partition(":")[0])] = str(line.partition(":")[2]).split()

        command.close()
        meta.close()
        param.close()

        self.completer = WordCompleter(words, False, d, False, True, False)

    def get_completions(self, document, complete_event):
        return self.completer.get_completions(document, complete_event)
        