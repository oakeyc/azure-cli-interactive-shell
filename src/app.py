from __future__ import unicode_literals

import subprocess
import os

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
from pygments.token import Token, Name, Keyword
from az_lexer import AzLexer
from layout import create_layout

manager = KeyBindingManager(
    enable_system_bindings=True,
    enable_auto_suggest_bindings=True,
)
registry = manager.registry


@registry.add_binding(Keys.ControlQ, eager=True)
def exit_(event):
    """ exits the program when Control Q is pressed """
    event.cli.set_return_value(None)


@registry.add_binding(Keys.Enter, eager=True)
def enter_(event):
    """ Sends the command to the terminal"""
    event.cli.set_return_value(event.cli.current_buffer)
    # event.cli.set_return_value(event.cli.current_doc)


def create_shell(completer):
    """ creates the shell """
    return Shell(completer)


class Shell(object):
    """ represents the shell """

    def __init__(self, completer):
        # TODO abstract styles
        self.styles = style_from_dict({
            # Completion colors
            Token.Menu.Completions.Completion.Current: 'bg:#ffc0cb #000000',
            Token.Menu.Completions.Completion: 'bg:#00b7b7 #ffffff',
            Token.Menu.Completions.ProgressButton: 'bg:#b78991',
            Token.Menu.Completions.ProgressBar: 'bg:#ffc0cb',
            Token.Az: '#7c2c80',
            # Toolbar
            Token.Toolbar: 'bg:#000000 #00b700',
            # Pretty Words
            Token.Keyword: '#ff0000',
            Token.Keyword.Declaration: '#b27cb2',
            Token.Name.Class: '#e050e5',
            Token.Text: '#ec96ef',
            # Temperary
            Token.Hello: '#008080',
            # Toolbar
            Token.Toolbar: 'bg:#000000 #00b700',
            Token.RPrompt: 'bg:#ffffff #800080',
        })
        self.completer = completer
        self.history = InMemoryHistory()
        self._cli = None
        self.refresh_cli = False
        self.lexer = AzLexer
        self.layout = None
        self.current_docs = u''
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
        document = cli.current_buffer.document
        text = document.text
        split_text = text.split()
        command = ""
        for word in split_text:
            command += str(word) + " "
            if self.completer.is_completable(command.rstrip()):
                if self.completer.is_command(command.rstrip()):
                    self.current_docs = unicode(self.completer.get_description(command.rstrip()) +
                                                "\n\n" + self.completer.get_param(command.rstrip()))
                else:
                    self.current_docs = unicode(self.completer.get_description(command.rstrip()))
                break
        else:
            self.current_docs = u''
        cli.buffers['description'].reset(
            initial_document=Document(self.current_docs, cursor_position=0))
        cli.request_redraw()

    def create_application(self):
        """ makes the application object and the buffers """
        buffers = {
            DEFAULT_BUFFER: Buffer(is_multiline=True),
            'description': Buffer(is_multiline=True, read_only=True)
        }

        return Application(
            mouse_support=False,
            style=self.styles,
            buffer=self.create_buffer(self.completer, self.history),
            on_input_timeout=self.on_input_timeout,
            key_bindings_registry=registry,
            layout=create_layout(self.lexer),
            buffers=buffers,
        )

    def create_buffer(self, completer, history):
        """ makes the buffer """
        return Buffer(
            history=history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
            completer=completer,
            complete_while_typing=Always()
        )

    def create_interface(self):
        """ instantiates the intereface """
        run_loop = create_eventloop()
        app = self.create_application()
        return CommandLineInterface(application=app, eventloop=run_loop)

    def run(self, database):
        """ runs the CLI """
        while True:
            try:
                document = self.cli.run(reset_current_buffer=True)
                text = document.text
            except AttributeError:  # when the user pressed Control Q
                break
            else:
                if text == "quit" or text == "exit":
                    break
                try:
                    if text[0] == "#":
                        cmd = text[1:]
                    else:
                        cmd = "az " + text
                except IndexError:  # enter blank for welcome message
                    cmd = "az"
                self.history.append(text)
                self.current_docs = u''
                self.cli.buffers["description"].reset(
                    initial_document=Document(self.current_docs,
                                              cursor_position=0))
                self.cli.request_redraw()
                proc = subprocess.Popen(cmd, shell=True, env=self._env)
                proc.communicate()
        print('Have a lovely day!!')
