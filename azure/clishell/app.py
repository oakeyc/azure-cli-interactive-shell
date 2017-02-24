from __future__ import unicode_literals, print_function

import subprocess
import os
import sys
import math
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.shortcuts import create_eventloop
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.document import Document
from prompt_toolkit.interface import CommandLineInterface, Application
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.filters import Always
from prompt_toolkit.keys import Keys
from prompt_toolkit.enums import DEFAULT_BUFFER
from pygments.token import Token

from azure.clishell.az_lexer import AzLexer
from azure.clishell.az_completer import AzCompleter
from azure.clishell.layout import create_layout

import azure.cli.core.telemetry as telemetry
from azure.cli.core._util import (show_version_info_exit, handle_exception)
from azure.cli.core.application import APPLICATION, Configuration
import azure.cli.core.telemetry as telemetry

manager = KeyBindingManager(
    enable_system_bindings=True,
    enable_auto_suggest_bindings=True,
)
registry = manager.registry

_SECTION = 1

@registry.add_binding(Keys.ControlQ, eager=True)
def exit_(event):
    """ exits the program when Control Q is pressed """
    event.cli.set_return_value(None)

@registry.add_binding(Keys.Enter, eager=True)
def enter_(event):
    """ Sends the command to the terminal"""
    event.cli.set_return_value(event.cli.current_buffer)

@registry.add_binding(Keys.ControlP, eager=True)
def panUp_(event):
    """ Pans the example pan up"""
    global _SECTION
    if _SECTION > 0:
        _SECTION -= 1

@registry.add_binding(Keys.ControlL, eager=True)
def panDown_(event):
    """ Pans the example pan down"""
    global _SECTION
    if _SECTION < 5:
        _SECTION += 1

def default_style():
    """ Default coloring """
    styles = style_from_dict({
        # Completion colors
        Token.Menu.Completions.Completion.Current: 'bg:#7c2c80 #ffffff',
        Token.Menu.Completions.Completion: 'bg:#00b7b7 #ffffff',
        Token.Menu.Completions.ProgressButton: 'bg:#b78991',
        Token.Menu.Completions.ProgressBar: 'bg:#ffc0cb',

        Token.Az: '#7c2c80',
        Token.Prompt.Arg: '#888888',
        # Toolbar
        Token.Toolbar: 'bg:#000000 #00b700',
        # Pretty Words
        Token.Keyword: '#965699',
        Token.Keyword.Declaration: '#ab77ad',
        Token.Name.Class: '#c49fc5',
        Token.Text: '#666666',

        # Toolbar
        Token.Toolbar: 'bg:#000000 #00b700',
        Token.RPrompt: 'bg:#ffffff #800080',

        Token.Line: '#E500E5',
        Token.Number: '#3d79db',
    })

    return styles

class Shell(object):
    """ represents the shell """

    def __init__(self, completer=None, styles=None, lexer=None, history=InMemoryHistory(),
                 app=None):
        self.styles = styles or default_style()
        self.lexer = lexer or AzLexer
        self.app = app
        self.completer = completer
        self.history = history
        self._cli = None
        self.refresh_cli = False
        self.layout = None
        self.description_docs = u''
        self.param_docs = u''
        self.example_docs = u''
        self._env = os.environ.copy()


    @property
    def cli(self):
        """ Makes the interface or refreshes it """
        if self._cli is None or self.refresh_cli:
            self._cli = self.create_interface()
            self.refresh_cli = False
        return self._cli

    def on_input_timeout(self, cli):
        """
        When there is a pause in typing
        Brings up the metadata for the command if
        there is a valid command already typed
        """
        rows, cols = os.popen('stty size', 'r').read().split()
        rows = int(rows)
        cols = int(cols)
        document = cli.current_buffer.document
        text = document.text
        command = ""
        all_params = ""
        example = ""

        any_documentation = False
        is_command = True
        for word in text.split():
            if word.startswith("-"):
                is_command = False
            if is_command:
                if not word == 'az':
                    command += str(word) + " "

            if self.completer.is_completable(command.rstrip()):
                cmdstp = command.rstrip()
                any_documentation = True

                if word in self.completer.command_parameters[cmdstp] and \
                self.completer.has_description(cmdstp + " " + word):
                    all_params += word + ":\n" + \
                    self.completer.get_param_description(cmdstp+ \
                    " " + word) + "\n"

                self.description_docs = u"%s" % \
                self.completer.get_description(cmdstp)

                if cmdstp in self.completer.command_examples:
                    example = self.create_examples(cmdstp, rows)

        if not any_documentation:
            self.description_docs = u''

        self.param_docs = u"%s" % all_params
        self.example_docs = u'%s' % example

        cli.buffers['description'].reset(
            initial_document=Document(self.description_docs, cursor_position=0)
        )
        cli.buffers['parameter'].reset(
            initial_document=Document(self.param_docs)
        )
        cli.buffers['examples'].reset(
            initial_document=Document(self.example_docs)
        )
        cli.request_redraw()

    def create_examples(self, cmdstp, rows):
        """ makes the example text """
        global _SECTION

        example = self.completer.command_examples[cmdstp]

        num_newline = example.count('\n')
        if num_newline > rows / 2:
            len_of_excerpt = math.floor(rows / 2)
            group = example.split('\n')
            if _SECTION * len_of_excerpt < num_newline:
                end = _SECTION * len_of_excerpt
                example = '\n'.join(group[:-end]) + "\n"
            else: # default chops top off
                example = '\n'.join(group) + "\n"
                while (_SECTION * len_of_excerpt) % num_newline > len_of_excerpt:
                    _SECTION -= 1
        return example

    def create_application(self):
        """ makes the application object and the buffers """
        buffers = {
            DEFAULT_BUFFER: Buffer(is_multiline=True),
            'description': Buffer(is_multiline=True, read_only=True),
            'parameter' : Buffer(is_multiline=True, read_only=True),
            'examples' : Buffer(is_multiline=True, read_only=True)
        }

        writing_buffer = Buffer(
            history=self.history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
            completer=self.completer,
            complete_while_typing=Always()
        )

        return Application(
            mouse_support=False,
            style=self.styles,
            buffer=writing_buffer,
            on_input_timeout=self.on_input_timeout,
            key_bindings_registry=registry,
            layout=create_layout(self.lexer),
            buffers=buffers,
        )

    def create_interface(self):
        """ instantiates the intereface """
        run_loop = create_eventloop()
        app = self.create_application()
        return CommandLineInterface(application=app, eventloop=run_loop)

    def run(self):
        """ runs the CLI """
        while True:
            try:
                document = self.cli.run(reset_current_buffer=True)
                text = document.text
                cmd = text
                outside = False
            except AttributeError:  # when the user pressed Control Q
                break
            else:
                if text.strip() == "quit" or text.strip() == "exit":
                    break
                if text:
                    if text[0] == "#":
                        cmd = text[1:]
                        outside = True
                    elif text.split()[0] == "az":
                        cmd = " ".join(text.split()[1:])
                # except IndexError:  # enter blank for welcome message
                self.history.append(cmd)
                self.description_docs = u''
                self.cli.buffers[DEFAULT_BUFFER].reset(
                    initial_document=Document(self.description_docs,
                                              cursor_position=0))
                self.cli.request_redraw()
                if outside:
                    subprocess.Popen(cmd).communicate()
                else:
                    # try:
                    config = Configuration(str(command) for command in cmd.split())
                    self.app.initialize(config)

                    result = self.app.execute([str(command) for command in cmd.split()])
                    if result and result.result is not None:
                        from azure.cli.core._output import OutputProducer
                        formatter = OutputProducer.get_formatter(
                            self.app.configuration.output_format)
                        OutputProducer(formatter=formatter, file=sys.stdout).out(result)

                    # except Exception as ex:  # pylint: disable=broad-except
                    #     print(ex.message)
                    #     # TODO: include additional details of the exception in telemetry
                    #     telemetry.set_exception(ex, 'outer-exception',
                    #                             'Unexpected exception caught during application execution.')
                    #     telemetry.set_failure()
                    #     break
                    #     # error_code = handle_exception(ex)
                    #     # return error_code

        print('Have a lovely day!!')
