import six
from azure.clishell.az_completer import AzCompleter
from unittest import TestCase


class _Commands():
    def __init__(self, descrip=None, completable=None, command_param=None,\
    completable_param=None, command_tree=None, param_descript=None, \
    command_example=None, same_param_doubles=None):
        self.command_description = descrip
        self.completable = completable
        self.command_parameters = command_param
        self.completable_param = completable_param

        self.command_tree = command_tree
        self.param_description = param_descript
        self.command_examples = command_example
        self.same_param_doubles = same_param_doubles

class CompletionTest(TestCase):
    def __init__(self):
        commands = _Commands()
        self.completer = AzCompleter(commands)
