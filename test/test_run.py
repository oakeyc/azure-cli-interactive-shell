from __future__ import unicode_literals

from prompt_toolkit.key_binding.input_processor import InputProcessor, KeyPress
from prompt_toolkit.key_binding.registry import Registry
from prompt_toolkit.keys import Keys

import six
# from azclishell.app import Shell
import unittest

# class ControlsTest(unittest.TestCase):

#     def registry(self, handlers):
#         registry = Registry()
#         registry.add_binding(
#             Keys.ControlQ
#         )(handlers.control_q)

#     def test_feed(self, processor, handlers):
#         processor.feed(KeyPress(Keys.ControlQ, '\x18'))
#         processor.process_keys()
#         assert handlers.called == ['control_q']



# class _ProcessorMock(object):

#     def __init__(self):
#         self.keys = []

#     def feed_key(self, key_press):
#         self.keys.append(key_press)


if __name__ == '__main__':
    unittest.main()
