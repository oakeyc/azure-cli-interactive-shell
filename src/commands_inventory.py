
class CompletionIndex(object):
    def __init__(self):
        self.commands = ['az', 'help']
        self.subcommands = [
            'configure',
            'account',
            'login',
            'storage',
            'vm'
            'help'
        ]
        self.args_opts = ['--name', '--account-name', '--account-key',
                          '--verbose', '--container']

    def load_completions(self):
        # dump the commands here
        print "LOADING...\n"
