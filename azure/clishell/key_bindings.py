""" makes all the key bindings for the app """
from __future__ import print_function

from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.filters import Filter
from prompt_toolkit.keys import Keys
from prompt_toolkit import prompt

import azure.clishell.configuration

manager = KeyBindingManager(
    enable_system_bindings=True,
    enable_auto_suggest_bindings=True,
)
registry = manager.registry

_SECTION = 1

PROMPTING = False
EXAMPLE_REPL = False

class _PromptFilter(Filter):
    def __call__(self, *a, **kw):
        return not PROMPTING

class _ExampleFilter(Filter):
    def __call__(self, *a, **kw):
        return not EXAMPLE_REPL

@registry.add_binding(Keys.ControlQ, eager=True)
def exit_(event):
    """ exits the program when Control Q is pressed """
    event.cli.set_return_value(None)

@registry.add_binding(Keys.Enter, filter=_PromptFilter() & _ExampleFilter())
def enter_(event):
    """ Sends the command to the terminal"""
    event.cli.set_return_value(event.cli.current_buffer)

@registry.add_binding(Keys.ControlH, eager=True)
def pan_up_(event):
    """ Pans the example pan up"""
    global _SECTION
    if _SECTION > 1:
        _SECTION -= 1

@registry.add_binding(Keys.ControlN, eager=True)
def pan_down_(event):
    """ Pans the example pan down"""
    global _SECTION
    if _SECTION < 10:
        _SECTION += 1

@registry.add_binding(Keys.F1, eager=True)
def config_settings_(event):
    """ opens the configuration """
    global PROMPTING
    PROMPTING = True
    config = azure.clishell.configuration.CONFIGURATION
    answer = ""
    questions = {
        "Do you want command descriptions" : "command_description",
        "Do you want parameter descriptions" : "param_description",
        "Do you want examples" : "examples"
    }
    for question in questions:
        while answer.lower() != 'y' and answer.lower() != 'n':
            answer = prompt(u'\n%s (y/n): ' %question)
        config.set_val('Layout', questions[question], format_response(answer))
        answer = ""
    PROMPTING = False
    print("\nChanges won't take effect until you restart the program\n\n")
    event.cli.set_return_value(event.cli.current_buffer)

def format_response(response):
    """ formats a response in a binary """
    conversion = azure.clishell.configuration.CONFIGURATION.BOOLEAN_STATES
    if response in conversion:
        if conversion[response]:
            return 'yes'
        else:
            return 'no'
    else:
        raise ValueError('Invalid response: input should equate to true or false')

def get_section():
    """ gets which section to display """
    return _SECTION

def sub_section():
    """ subtracts which section so not to overflow """
    global _SECTION
    _SECTION -= 1
