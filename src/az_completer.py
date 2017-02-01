from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion

class AzCompleter(Completer):
    """ Completes Azure CLI commands """
    def __init__(self):
        self.words = []
        self.descrip = {}
        self.param_dict = {}
        self.current_comamand = ""
        self.last_option = ""

        command = open("dump.txt", 'r')
        meta = open("meta_dump.txt", 'r')
        param = open("params_dump.txt", 'r')

        for line in command:
            self.words.append(line.strip("\n"))
        self.words.append("quit")
        self.words.append("exit")

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
            self.param_dict[str(line.partition(":")[0])] = str(line.partition(":")[2]).strip("\n")

        command.close()
        meta.close()
        param.close()

        self.completer = WordCompleter(self.words, False, self.param_dict, False, True, False)

    def get_completions(self, document, complete_event):
        return self.completer.get_completions(document, complete_event)

    def get_param(self, command):
        """ returns the parameters for a given command """
        return self.param_dict[command]

    def get_description(self, command):
        """ returns the description for a given command """
        return self.descrip[command]

    def is_command(self, command):
        """ returns whether given command is valid """
        return command in self.words
        