
class CompletionIndex(object):
    def __init__(self):
        self.com = open("dump.txt", 'r')
        self.commands = ['az']
        self.subcommands = []
        self.args_opts = []

    def load_completions(self):
        for line in self.com:
            sent = line.strip("\n").strip('az').split()
            if len(sent) % 2 == 0: #TODO fix this to make actual sense
                for word in sent:
                    self.subcommands.append(word)
            else:
                for word in sent:
                    self.args_opts.append(word)
        self.com.close()
