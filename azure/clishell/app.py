from __future__ import unicode_literals, print_function

import subprocess
import os
import sys
import math
import json
import collections
import shutil

from prompt_toolkit import prompt
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.shortcuts import create_eventloop
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.document import Document
from prompt_toolkit.interface import CommandLineInterface, Application
from prompt_toolkit.filters import Always
from prompt_toolkit.enums import DEFAULT_BUFFER

from pygments.token import Token

import azure.clishell.configuration
from azure.clishell.az_lexer import AzLexer
from azure.clishell.az_completer import AzCompleter
from azure.clishell.layout import create_layout, create_layout_completions
from azure.clishell.key_bindings import registry, get_section, sub_section, EXAMPLE_REPL
from azure.clishell.util import dict_path

import azure.cli.core.azlogging as azlogging
import azure.cli.core.telemetry as telemetry
from azure.cli.core._util import (show_version_info_exit, handle_exception)
from azure.cli.core._util import CLIError
from azure.cli.core.application import APPLICATION, Configuration
from azure.cli.core._session import ACCOUNT, CONFIG, SESSION
from azure.cli.core._environment import get_config_dir

logger = azlogging.get_az_logger(__name__)
SHELL_CONFIGURATION = azure.clishell.configuration.CONFIGURATION
NOTIFICATIONS = ""

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

        # Pretty Words
        Token.Keyword: '#965699',
        Token.Keyword.Declaration: '#ab77ad',
        Token.Name.Class: '#c49fc5',
        Token.Text: '#666666',

        Token.Line: '#E500E5',
        Token.Number: '#3d79db',
        # toolbar
        Token.Operator: 'bg:#000000 #ffffff',
        Token.Toolbar: 'bg:#000000 #ffffff'
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
        self.last = None
        self.last_exit = 0

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
        empty_space = ""
        for i in range(cols):
            empty_space += " "
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
                    all_params = word + ":\n" + \
                    self.completer.get_param_description(cmdstp+ \
                    " " + word)

                self.description_docs = u"%s" % \
                self.completer.get_description(cmdstp)

                if cmdstp in self.completer.command_examples:
                    string_example = ""
                    for example in self.completer.command_examples[cmdstp]:
                        for part in example:
                            string_example += part
                    example = self.space_examples(
                        string_example, self.completer.command_examples[cmdstp], rows)

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
        spacing = '      '
        settings_items = [
            "[F1] Layout Settings",
            "[Control-Q] Quit"
        ]
        settings = ""
        for item in settings_items:
            settings += item + spacing
        empty_space = empty_space[len(NOTIFICATIONS) + len(settings) + 1:]

        cli.buffers['bottom_toolbar'].reset(
            initial_document=Document(u'%s%s%s' % \
            (NOTIFICATIONS, settings, empty_space))
        )
        cli.request_redraw()

    def space_examples(self, string_examples, list_examples, rows):
        """ makes the example text """
        examples_with_index = []
        for i in range(len(list_examples)):
            examples_with_index.append("[" + str(i + 1) + "]" + list_examples[i][0] +\
            list_examples[i][1])

        example = "".join(exam for exam in examples_with_index)
        num_newline = example.count('\n')
        if num_newline > rows / 2:
            len_of_excerpt = math.floor(rows / 3)
            group = example.split('\n')
            end = int(get_section() * len_of_excerpt)
            begin = int((get_section() - 1) * len_of_excerpt)

            if get_section() * len_of_excerpt < num_newline:
                example = '\n'.join(group[begin:end]) + "\n"
            else: # default chops top off
                example = '\n'.join(group[begin:]) + "\n"
                while ((get_section() - 1) * len_of_excerpt) > num_newline:
                    sub_section()
        return example

    def create_application(self, all_layout=True):
        """ makes the application object and the buffers """
        if all_layout:
            layout = create_layout(self.lexer)
        else:
            layout = create_layout_completions(self.lexer)

        buffers = {
            DEFAULT_BUFFER: Buffer(is_multiline=True),
            'description': Buffer(is_multiline=True, read_only=True),
            'parameter' : Buffer(is_multiline=True, read_only=True),
            'examples' : Buffer(is_multiline=True, read_only=True),
            'bottom_toolbar' : Buffer(is_multiline=True),
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
            layout=layout,
            buffers=buffers,
        )

    def create_interface(self):
        """ instantiates the intereface """
        run_loop = create_eventloop()
        app = self.create_application()
        return CommandLineInterface(application=app, eventloop=run_loop,)

    def set_prompt(self, prompt="", position=0):
        """ clears the prompt line """
        self.description_docs = u'%s' %prompt
        self.cli.buffers[DEFAULT_BUFFER].reset(
            initial_document=Document(self.description_docs,\
            cursor_position=position))
        self.cli.request_redraw()

    def handle_example(self, text):
        cmd = text.partition(":")[0].rstrip()
        num = text.partition(":")[2].strip()
        example = ""
        try:
            num = int(num) - 1
        except ValueError:
            print("An Integer should follow the colon")
        if cmd in self.completer.command_examples and num >= 0 and\
        num < len(self.completer.command_examples[cmd]):
            example = self.completer.command_examples[cmd][num][1]
            example = example.replace('\n', '')

        if example.split()[0] == 'az':
            example = ' '.join(example.split()[1:])

        starting_index = None
        counter = 0
        example_no_fill = ""
        flag_fill = True
        for word in example.split():
            if flag_fill:
                example_no_fill += word + " "
            if word.startswith('-'):
                example_no_fill += word + " "
                if not starting_index:
                    starting_index = counter
                flag_fill = False
            counter += 1
        # if not starting_index:
        #     starting_index = 0
        return self.example_repl(example_no_fill, starting_index)

    def example_repl(self, text, start_index):
        global EXAMPLE_REPL
        EXAMPLE_REPL = True
        if start_index:
            start_index = start_index + 1
            cmd = ' '.join(text.split()[:start_index])
            example_cli = CommandLineInterface(
                application=self.create_application(
                    all_layout=False),
                eventloop=create_eventloop())

            for i in range(len(text.split()) - start_index):
                ########## BROKEN
                example_cli.application.buffer.reset(
                    initial_document=Document(u'%s' %cmd,\
                    cursor_position=len(cmd)))
                example_cli.request_redraw()
                answer = example_cli.run(reset_current_buffer=True)
                answer = answer.text
                start_index += 1
                cmd += " " + answer.split()[-1] + " " +\
                u' '.join(text.split()[start_index:start_index + 1])
            example_cli.exit()
            del example_cli
        else:
            cmd = text

        EXAMPLE_REPL = False
        return cmd
        # self.set_prompt(cmd)


    def run(self):
        """ runs the CLI """
        telemetry.start()
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
                if text: # some bandaids
                    if text[0] == "#":
                        cmd = text[1:]
                        outside = True
                    elif text.split()[0] == "az":
                        cmd = " ".join(text.split()[1:])
                    elif text[0] == "$":
                        print(self.last_exit)
                        self.set_prompt()
                        continue
                    elif "?" in text:
                        answer = []
                        failed = False
                        dump = False
                        curr_dict = []
                        curr_dict.append(self.last.result)


                        if self.last and self.last.result:
                            for arg in text.partition("?")[2].split():
                                arg = str(arg)
                                for value in dict_path(arg, curr_dict):
                                    answer.append(value)
                        if not failed:
                            for ans in answer:
                                print(ans)
                                print('\n')
                        self.set_prompt()
                        continue
                    elif "|" in text:
                        outside = True
                        cmd = "az " + cmd
                    elif ":" in text:
                        global NOTIFICATIONS
                        # NOTIFICATIONS = "IN TUTORIAL MODE        "
                        cmd = self.handle_example(text)
                        # NOTIFICATIONS = ""

                if not text:
                    self.set_prompt()
                    continue

                # except IndexError:  # enter blank for welcome message
                self.history.append(cmd)
                self.set_prompt()
                if outside:
                    subprocess.Popen(cmd, shell=True).communicate()
                else:
                    try:
                        args = [str(command) for command in cmd.split()]
                        azlogging.configure_logging(args)

                        azure_folder = get_config_dir()
                        if not os.path.exists(azure_folder):
                            os.makedirs(azure_folder)
                        ACCOUNT.load(os.path.join(azure_folder, 'azureProfile.json'))
                        CONFIG.load(os.path.join(azure_folder, 'az.json'))
                        SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)

                        config = Configuration(args)
                        self.app.initialize(config)

                        result = self.app.execute(args)
                        if result and result.result is not None:
                            from azure.cli.core._output import OutputProducer, format_json
                            formatter = OutputProducer.get_formatter(
                                self.app.configuration.output_format)
                            OutputProducer(formatter=formatter, file=sys.stdout).out(result)
                            self.last = result
                            self.last_exit = 0
                    except Exception as ex:  # pylint: disable=broad-except
                        self.last_exit = handle_exception(ex)
                    except SystemExit as ex:
                        self.last_exit = ex.code
                    if self.last_exit != 0:
                        telemetry.set_failure()
                    else:
                        telemetry.set_success()

        print('Have a lovely day!!')
        telemetry.conclude()
