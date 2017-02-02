
class CompletionIndex(object):
    """ Reads in commands from files """
    def __init__(self):
        self.com = open("dump.txt", 'r')
        self.param = open("params_dump.txt", 'r')
        self.commands = ['quit', 'exit']
        self.subcommands = []
        self.args_opts = []

    def load_completions(self):
        """ loads the commands from files """
        for line in self.com:
            self.subcommands.append(line.strip("\n"))

        for line in self.param:
            for arg in line.partition("|")[2].split():
                if arg not in self.args_opts:
                    self.args_opts.append(arg.replace("[required]", ""))

        self.com.close()
        self.param.close()
