from __future__ import unicode_literals

import unittest

from prompt_toolkit.input import PipeInput
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.key_binding.input_processor import KeyPress, InputProcessor
from prompt_toolkit.keys import Keys

from azclishell.key_bindings import registry as reg
# from azclishell.app import Shell

class KeyBindingsTest(unittest.TestCase):

    def init(self):
        self.input = PipeInput()
        output = DummyOutput()
        # self.shell = Shell(input=self.input, output=output)
        self.processor = InputProcessor

    def tearDown(self):
        self.input.close()

    # def feed_key(self, key):
    #     self.processor.feed(KeyPress(key, u''))
    #     self.processor.process_keys()

    # def test_press_f1(self):
    #     self.feed_key(Keys.F1)