import six
from azclishell.command_tree import CommandBranch, CommandHead, CommandTree
import unittest

class TreeTest(unittest.TestCase):

    def test_basic_children(self):
        tree = CommandTree(data=None)
        self.assertFalse(tree.has_child(""))
        with self.assertRaises(ValueError):
            tree.get_child("nothing", tree.children)
        tree.add_child(CommandBranch("Kid1"))
        self.assertTrue(tree.has_child("Kid1"))
        self.assertFalse(tree.has_child("Kid2"))
        self.assertFalse(
            isinstance(tree.get_child("Kid1", tree.children), six.string_types)
        )
        self.assertTrue(
            isinstance(tree.get_child("Kid1", tree.children), CommandTree)
        )

    def test_subbranch(self):
        tree3 = CommandBranch("Again")
        tree2 = CommandBranch("World")
        tree2.add_child(tree3)
        tree1 = CommandBranch("Hello")
        tree1.add_child(tree2)
        tree = CommandHead()
        tree.add_child(tree1)
        self.assertEqual(tree.get_subbranch("Hello"), ["World", "Again"])

if __name__ == '__main__':
    unittest.main()
