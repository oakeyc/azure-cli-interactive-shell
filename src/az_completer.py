from prompt_toolkit.contrib.completers import WordCompleter

# import the command table

class Az_Completer(object):
    def __init__(self):
        x = 3 + 3
        # does something

    def wordCompleter(self):
        x = 3 + 3
        return WordCompleter([
            'az',
            'configure',
            'account',
            'fill',
            'this',
            'in',
            'later',
            'yay'
        ])