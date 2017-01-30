from __future__ import unicode_literals

import sys
import subprocess

from prompt_toolkit import prompt, AbortAction
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.shortcuts import create_eventloop
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.document import Document
from prompt_toolkit.interface import CommandLineInterface, Application
from pygments.style import Style
from pygments.token import Token, Name, Keyword
from pygments.lexers.c_like import ArduinoLexer
from pygments.styles.default import DefaultStyle
from az_completer import Az_Completer
from az_lexer import Az_Lexer

def create_shell(completer):
    return Shell(completer)

def Shell(object):
    def __init__(self, completer):
        self.styles = style_from_dict({
            # Completion colors
            Token.Menu.Completions.Completion.Current: 'bg:#ffc0cb #000000',
            Token.Menu.Completions.Completion: 'bg:#00b7b7 #ffffff',
            Token.Menu.Completions.ProgressButton: 'bg:#b78991',
            Token.Menu.Completions.ProgressBar: 'bg:#ffc0cb',
            # Prompt
            Token.Az: '#7e70ff',
            # Toolbar
            Token.Toolbar: 'bg:#000000 #00b700',
            Token.RPrompt: 'bg:#ffffff #800080',
            # Pretty Words
            Token.Keyword: '#ff0000 bold',
            Token.Name.Class:'#e050e5',
            Token.Keyword.Declaration: '#f5a3f5',
            Token.Text: '#008080',
        })
        self.completer = completer
        self.history = InMemoryHistory()
        self._cli = None
        self.refresh_cli = False
        self.create_interface()

    @property
    def cli(self):
        if self._cli is None or self.refresh_cli:
            self._cli = self.create_interface()
            self.refresh_cli = False
        return self._cli

    def get_prompt_tokens(cli):
        return [(Token.Az, 'az>> ')]

    def get_bottom_toolbar_tokens(cli):
        return [(Token.Toolbar, "HELP IS ON THE WAY")]


    def get_rprompt_tokens(cli):
        return [(Token.RPrompt, "For help --help")]

    # hook up to the meta data
    def on_input_timeout(self, cli):
        document = cli.current_buffer.document
        text = document.text
        if text.strip():
            command = self.completer.current_command
            last_option = self.completer.last_option
            if last_option:
                # self.current_docs = self._docs.extract_param( # get the parameters
                #     key_name, last_option) 
                self.current_docs = self.completer.get_param(command)
            else:
                # self.current_docs = self._docs.extract_description(key_name) # get the metadata
                self.current_docs = self.completer.get_description(command)
        else:
            self.current_docs = u''
        cli.buffers['clidocs'].reset(
            initial_document=Document(self.current_docs, cursor_position=0))
        cli.request_redraw()

    def create_application(self):
        return Application(
            mouse_support=False,
            style=self.styles,
            buffer=self.create_buffer(self.completer, self.history),
            on_input_timeout=self.on_input_timeout
        )
    
    def create_buffer(self, completer, history):
        return Buffer(
            history=self.history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
            completer=self.completer
        )

    def create_interface(self):
        app = self.create_application()
        return CommandLineInterface(application=app, eventloop=create_eventloop())

    def run(self, database):
    # connection = azure.connect(database) TODO fix this
        az_lexer = Az_Lexer
        # margin = PromptMargin(get_margin_tokens)
        while True:
            try:
                document = self.cli.run(reset_current_buffer=True)
                text = document.text

                text = prompt(get_prompt_tokens=get_prompt_tokens, lexer=az_lexer,
                              get_bottom_toolbar_tokens=get_bottom_toolbar_tokens,
                              #   on_input_timeout=on_input_timeout, # application time?
                              get_rprompt_tokens=get_rprompt_tokens)
            except EOFError:
                break  # Control-D pressed.
            if text == "quit" or text == "exit":
                break
            p = subprocess.Popen("az " + text, shell=True)
            p.communicate()
        print('Have a lovely day!!')