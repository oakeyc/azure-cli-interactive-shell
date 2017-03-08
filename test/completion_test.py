import six

import azure.clishell.command_tree as tree
from azure.clishell.az_completer import AzCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completion

import unittest


class _Commands():
    def __init__(self, descrip=None, completable=None, command_param=None,\
    completable_param=None, command_tree=None, param_descript=None, \
    command_example=None, same_param_doubles=None):
        self.descrip = descrip
        self.completable = completable
        self.command_param = command_param
        self.completable_param = completable_param

        self.command_tree = command_tree
        self.param_descript = param_descript
        self.command_example = command_example
        self.same_param_doubles = same_param_doubles

class CompletionTest(unittest.TestCase):
    def init(self):
        com_tree1 = tree.generate_tree("command can")
        com_tree2 = tree.generate_tree("create")
        com_tree3 = tree.CommandHead()
        com_tree3.add_child(com_tree2)
        com_tree3.add_child(com_tree1)

        commands = _Commands(
            command_tree=com_tree3
        )
        self.completer = AzCompleter(commands)

    def test_command_completion(self):
        self.init()

        doc = Document(u'')
        gen = self.completer.get_completions(doc, None)
        self.assertEqual(gen.__next__(), Completion("create"))
        self.assertEqual(gen.__next__(), Completion("command"))

        doc = Document(u'c')
        gen = self.completer.get_completions(doc, None)
        self.assertEqual(gen.__next__(), Completion("create", -1))
        self.assertEqual(gen.__next__(), Completion("command", -1))

        doc = Document(u'cr')
        gen = self.completer.get_completions(doc, None)
        self.assertEqual(gen.__next__(), Completion("create", -2))

if __name__ == '__main__':
    unittest.main()
