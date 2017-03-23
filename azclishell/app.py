""" The Main Application """
from __future__ import unicode_literals, print_function

import subprocess
import os
import sys
import math
import json
import collections
import re
import jmespath

from six.moves import configparser

# from prompt_toolkit import prompt
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.shortcuts import create_eventloop
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.document import Document
from prompt_toolkit.interface import CommandLineInterface, Application
from prompt_toolkit.filters import Always
from prompt_toolkit.enums import DEFAULT_BUFFER

from pygments.token import Token

# from tabulate import tabulate

import azclishell.configuration
from azclishell.az_lexer import AzLexer, ExampleLexer, ToolbarLexer
from azclishell.az_completer import AzCompleter
from azclishell.layout import create_layout, create_layout_completions, set_default_command
from azclishell.key_bindings import registry, get_section, sub_section, EXAMPLE_REPL
from azclishell.util import get_window_dim, default_style, parse_quotes
from azclishell.gather_commands import add_random_new_lines

import azure.cli.core.azlogging as azlogging
import azure.cli.core.telemetry as telemetry
from azure.cli.core._util import (show_version_info_exit, handle_exception)
from azure.cli.core._util import CLIError
from azure.cli.core.application import APPLICATION, Configuration
from azure.cli.core._session import ACCOUNT, CONFIG, SESSION
from azure.cli.core._environment import get_config_dir
from azure.cli.core.cloud import get_active_cloud_name
from azure.cli.core._profile import _SUBSCRIPTION_NAME, Profile
from azure.cli.core._output import format_json, TableOutput
from azure.cli.core._config import az_config, DEFAULTS_SECTION

logger = azlogging.get_az_logger(__name__)
SHELL_CONFIGURATION = azclishell.configuration.CONFIGURATION
NOTIFICATIONS = ""
PROFILE = Profile()
SELECT_SYMBOL = azclishell.configuration.SELECT_SYMBOL

# shell_help = {
#     "#[command]" : "use commands outside the application",
#     "?[path]" : "query previous command using jmespath syntax",
#     "[command] :: [example number]" : "do a step by step tutorial of example",
#     "$" : "get the exit code of the previous command",
#     "%%" : "default a value",
#     "^^" : "undefault a value"
# }
shell_help = \
    "#[cmd]          : use commands outside the application\n" +\
    "?[path]         : query previous command using jmespath syntax\n" +\
    "[cmd] :: [num]  : do a step by step tutorial of example\n" +\
    "$               : get the exit code of the previous command\n" +\
    "%%              : default a scope\n" +\
    "^^              : undefault a scope\n" + \
    "Crtl+N          : Scroll down the documentation\n" +\
    "Crtl+Y          : Scroll up the documentation"


class Shell(object):
    """ represents the shell """

    def __init__(self, completer=None, styles=None, lexer=None, history=InMemoryHistory(),
                 app=None, input_custom=sys.stdout, output_custom=None):
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
        self.input = input_custom
        self.output = output_custom
        self.config_default = ""
        # self.default_params = []
        self.default_command = ""

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
        rows, cols = get_window_dim()
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
        text = text.replace('az', '')
        if self.default_command:
            text = self.default_command + ' ' + text

        for word in text.split():
            if word.startswith("-"):
                is_command = False
            if is_command:
                command += str(word) + " "

            if self.completer.is_completable(command.rstrip()):
                cmdstp = command.rstrip()
                any_documentation = True

                if word in self.completer.command_parameters[cmdstp] and \
                self.completer.has_description(cmdstp + " " + word):
                    all_params = word + ":\n" + \
                    self.completer.get_param_description(cmdstp+ \
                    " " + word)

                self.description_docs = u'{}'.format(
                    self.completer.get_description(cmdstp))

                if cmdstp in self.completer.command_examples:
                    string_example = ""
                    for example in self.completer.command_examples[cmdstp]:
                        for part in example:
                            string_example += part
                    example = self.space_examples(
                        self.completer.command_examples[cmdstp], rows)

        if not any_documentation:
            self.description_docs = u''

        self.param_docs = u'{}'.format(all_params)
        self.example_docs = u'{}'.format(example)

        try:
            options = az_config.config_parser.options(DEFAULTS_SECTION)
            self.config_default = ""
            for opt in options:
                self.config_default += opt + ": " + az_config.get(DEFAULTS_SECTION, opt) + "  "
        except configparser.NoSectionError:
            self.config_default = ""
        settings, empty_space = self._toolbar_info(cols, empty_space)

        cli.buffers['description'].reset(
            initial_document=Document(self.description_docs, cursor_position=0)
        )
        cli.buffers['parameter'].reset(
            initial_document=Document(self.param_docs)
        )
        cli.buffers['examples'].reset(
            initial_document=Document(self.example_docs)
        )
        cli.buffers['bottom_toolbar'].reset(
            initial_document=Document(u'{}{}{}'.format(NOTIFICATIONS, settings, empty_space))
        )
        cli.buffers['default_values'].reset(
            initial_document=Document(
                u'{}'.format(self.config_default if self.config_default else 'No Default Values'))
        )
        cli.request_redraw()

    def _toolbar_info(self, cols, empty_space):
        sub_name = ""
        try:
            sub_name = PROFILE.get_subscription()[_SUBSCRIPTION_NAME]
        except CLIError:
            pass

        # if self.default_params:
        #     toolbar_value = "Default Param: %s" % ' '.join(self.default_params)
        # else:
        toolbar_value = "Cloud: {}".format(get_active_cloud_name())
        sub_value = '{}'.format('Subscription: {}'.format(sub_name) if sub_name else toolbar_value)

        settings_items = [
            " [F1]Layout",
            "[F2]Defaults",
            "[F3]Keys",
            "[Crtl+Q]Quit",
            sub_value
        ]
        counter = 0
        for part in settings_items:
            counter += len(part)
        spacing = empty_space[:int(math.floor((cols - counter) / (len(settings_items) - 1)))]
        settings = ""
        for i in range(len(settings_items)):
            if i != len(settings_items) - 1:
                settings += settings_items[i] + spacing
            else:
                settings += settings_items[i]
        empty_space = empty_space[len(NOTIFICATIONS) + len(settings) + 1:]
        return settings, empty_space

    def space_examples(self, list_examples, rows):
        """ makes the example text """
        examples_with_index = []
        for i in range(len(list_examples)):
            examples_with_index.append("[" + str(i + 1) + "] " + list_examples[i][0] +\
            list_examples[i][1])

        example = "".join(exam for exam in examples_with_index)
        num_newline = example.count('\n')
        if num_newline > rows / 3:
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
            layout = create_layout(self.lexer, ExampleLexer, ToolbarLexer)
        else:
            layout = create_layout_completions(self.lexer)

        buffers = {
            DEFAULT_BUFFER: Buffer(is_multiline=True),
            'description': Buffer(is_multiline=True, read_only=True),
            'parameter' : Buffer(is_multiline=True, read_only=True),
            'examples' : Buffer(is_multiline=True, read_only=True),
            'bottom_toolbar' : Buffer(is_multiline=True),
            'example_line' : Buffer(is_multiline=True),
            'default_values' : Buffer(),
            'symbols' : Buffer()
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
        return CommandLineInterface(application=app, eventloop=run_loop)

    def set_prompt(self, prompt_command="", position=0):
        """ clears the prompt line """
        self.description_docs = u'{}'.format(prompt_command)
        self.cli.current_buffer.reset(
            initial_document=Document(self.description_docs,\
            cursor_position=position))
        self.cli.request_redraw()

    # def handle_default_param(self, text):
    #     """ defaults a value """
    #     # assert len(text) > 2
    #     value = " ".join(text[:2])
    #     self.default_params.append(value)
    #     return value

    def handle_default_command(self, text):
        """ default commands """
        value = text[0]
        set_default_command(value)
        if self.default_command:
            self.default_command += ' ' + value
        else:
            self.default_command += value
        return value

    def handle_example(self, text):
        """ parses for the tutortial """
        cmd = text.partition(SELECT_SYMBOL['example'])[0].rstrip()
        num = text.partition(SELECT_SYMBOL['example'])[2].strip()
        example = ""
        try:
            num = int(num) - 1
        except ValueError:
            print("An Integer should follow the colon")
            return ""
        if cmd in self.completer.command_examples and num >= 0 and\
        num < len(self.completer.command_examples[cmd]):
            example = self.completer.command_examples[cmd][num][1]
            example = example.replace('\n', '')

        example = example.replace('az', '')

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

        return self.example_repl(example_no_fill, example, starting_index)

    def example_repl(self, text, example, start_index):
        """ REPL for interactive tutorials """
        global EXAMPLE_REPL
        EXAMPLE_REPL = True
        if start_index:
            start_index = start_index + 1
            cmd = ' '.join(text.split()[:start_index])
            example_cli = CommandLineInterface(
                application=self.create_application(
                    all_layout=False),
                eventloop=create_eventloop())
            example_cli.buffers['example_line'].reset(
                initial_document=Document(u'{}\n'.format(
                    add_random_new_lines(example)))
            )
            # counter = 0
            while start_index < len(text.split()):
                if self.default_command:
                    cmd = cmd.replace(self.default_command + ' ', '')
                example_cli.buffers[DEFAULT_BUFFER].reset(
                    initial_document=Document(
                        u'{}'.format(cmd),
                        cursor_position=len(cmd)))
                example_cli.request_redraw()
                answer = example_cli.run()
                if not answer:
                    return ""
                answer = answer.text
                if answer.strip('\n') == cmd.strip('\n'):
                    continue
                else:
                    if len(answer.split()) > 1:
                        start_index += 1
                        cmd += " " + answer.split()[-1] + " " +\
                        u' '.join(text.split()[start_index:start_index + 1])
            example_cli.exit()
            del example_cli
        else:
            cmd = text

        EXAMPLE_REPL = False
        return cmd

    def _special_cases(self, text, cmd, outside):
        b_flag = False
        c_flag = False
        if text.split() and text.split()[0] == 'az':
            cmd = ' '.join(text.split()[1:])
        if self.default_command:
            cmd = self.default_command + " " + cmd

        if text.strip() == "quit" or text.strip() == "exit":
            b_flag = True
        elif text.strip() == "clear":  # clears the history, but only when you restart
            outside = True
            cmd = 'echo -n "" >' +\
                os.path.join(
                    SHELL_CONFIGURATION.get_config_dir(),
                    SHELL_CONFIGURATION.get_history())
        # elif text.strip() == "help":
        #     print(shell_help)
        if text:
            if text[0] == SELECT_SYMBOL['outside']:
                cmd = text[1:]
                outside = True
            # elif text.split()[0] == "az":  # dumps the extra az
            #     cmd = " ".join(text.split()[1:])
            elif text[0] == SELECT_SYMBOL['exit_code']:
                print(self.last_exit)
                self.set_prompt()
                c_flag = True
            elif SELECT_SYMBOL['query'] in text:  # query previous output
                if self.last and self.last.result:
                    if hasattr(self.last.result, '__dict__'):
                        input_dict = dict(self.last.result)
                    else:
                        input_dict = self.last.result
                    try:
                        result = jmespath.search(
                            text.partition(SELECT_SYMBOL['query'])[2], input_dict)
                        if isinstance(result, str):
                            print(result)
                        else:
                            print(json.dumps(result, sort_keys=True, indent=2))
                    except jmespath.exceptions.ParseError:
                        print("Invalid Query")

                self.set_prompt()
                c_flag = True
            elif "|" in text or ">" in text:  # anything I don't parse, send off
                outside = True
                cmd = "az " + cmd
            elif SELECT_SYMBOL['example'] in text:
                global NOTIFICATIONS
                cmd = self.handle_example(cmd)
        if SELECT_SYMBOL['default'] in text:
            default = text.partition(SELECT_SYMBOL['default'])[2].split()
            value = self.handle_default_command(default)
            print("defaulting: " + value)
            self.set_prompt()
            c_flag = True
        if SELECT_SYMBOL['undefault'] in text:
            value = text.partition(SELECT_SYMBOL['undefault'])[2].split()
            if len(value) == 0:
                self.default_command = ""
                set_default_command("", add=False)
                print('undefaulting all')
            elif len(value) == 1 and value[0] == self.default_command:
                self.default_command = ""
                set_default_command("", add=False)
                print('undefaulting: ' + value[0])

            self.set_prompt()
            c_flag = True

        return b_flag, c_flag, outside, cmd


    def run(self):
        """ runs the CLI """
        telemetry.start()
        self.cli.buffers['symbols'].reset(
            initial_document=Document(u'{}'.format(shell_help)))
        while True:
            try:
                document = self.cli.run(reset_current_buffer=True)
                text = document.text
                if not text: # not input
                    self.set_prompt()
                    continue
                cmd = text
                outside = False
            except AttributeError:  # when the user pressed Control Q
                break
            else:
                b_flag, c_flag, outside, cmd = self._special_cases(text, cmd, outside)
                if b_flag:
                    break
                if c_flag:
                    continue

                self.history.append(cmd)
                self.set_prompt()
                if outside:
                    subprocess.Popen(cmd, shell=True).communicate()
                else:
                    try:
                        args = parse_quotes(cmd)
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
                        self.last_exit = 0
                        if result and result.result is not None:
                            from azure.cli.core._output import OutputProducer
                            if self.output:
                                self.output.out(result)
                            else:
                                formatter = OutputProducer.get_formatter(
                                    self.app.configuration.output_format)
                                OutputProducer(formatter=formatter, file=self.input).out(result)
                                self.last = result

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
