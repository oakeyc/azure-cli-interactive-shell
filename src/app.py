""" Azure Command Line Interface's Interactive Shell """

import os, subprocess, logging, sys

from prompt_toolkit.interface import CommandLineInterface, Application
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory, FileHistory