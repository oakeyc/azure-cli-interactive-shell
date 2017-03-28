""" gets the parsed args """
import argparse
import contextlib
import os
import sys

from argcomplete import CompletionFinder, mute_stderr
from argcomplete.compat import USING_PYTHON2, ensure_bytes

class ArgsFinder(CompletionFinder):
    """ gets the parsed args """
    def get_parsed_args(self, comp_words):
        """ gets the parsed args from a patched parser """
        active_parsers = self._patch_argument_parser()

        parsed_args = argparse.Namespace()

        self.completing = True
        if USING_PYTHON2:
            # Python 2 argparse only properly works with byte strings.
            comp_words = [ensure_bytes(word) for word in comp_words]

        try:
            with mute_stderr():
                args = self._parser.parse_known_args(comp_words, namespace=parsed_args)
        except BaseException as exp:
            pass
            # print("\nexception", type(e), str(e), "while parsing args")

        self.completing = False
        return parsed_args
