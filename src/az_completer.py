import sys
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer

# import the command table

class Az_Completer(Completer):
    def __init__(self):
        words = []
        d = {}
        command = open("dump.txt", 'r')
        meta = open("meta_dump.txt", 'r')

        for line in command:
            words.append(line.strip("\n"))

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

        command.close()
        meta.close()

        self.completer = WordCompleter(words, False, d, False, True, False)

    def get_completions(self, document, complete_event):
        return self.completer.get_completions(document, complete_event)
        