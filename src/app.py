from __future__ import unicode_literals

import sys
import subprocess

from prompt_toolkit import prompt, AbortAction
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from pygments.style import Style
from pygments.token import Token, Name, Keyword, Text
from pygments.lexers.c_like import ArduinoLexer
from pygments.styles.default import DefaultStyle
from az_completer import Az_Completer
from az_lexer import Az_Lexer


styles = style_from_dict({
    # Completion colors
    Token.Menu.Completions.Completion.Current: 'bg:#ffc0cb #000000',
    Token.Menu.Completions.Completion: 'bg:#00b7b7 #ffffff',
    Token.Menu.Completions.ProgressButton: 'bg:#b78991',
    Token.Menu.Completions.ProgressBar: 'bg:#ffc0cb',
    # Prompt
    Token.Az: '#7c2c80',
    # Toolbar
    Token.Toolbar: 'bg:#000000 #00b700',
    # Pretty Words
    Token.Keyword: '#ff0000 bold',
    Token.Name.Class:'#e050e5',
    Token.Text: '#ec96ef',
})

def get_prompt_tokens(cli):
    return [(Token.Az, 'az>> ')]

def get_bottom_toolbar_tokens(cli):
    return [(Token.Toolbar, "HELP IS ON THE WAY")]


def get_rprompt_tokens(cli):
    param = open("params_dump.txt", 'r')
    param_dict = {}
    for line_pre in param:
        line = line_pre.strip("\n")
        param_dict[str(line.partition(":")[0])] = str(line.partition(":")[2]).split()

def main(database):
    history = InMemoryHistory()
    az_completer = Az_Completer()
   # connection = azure.connect(database) TODO fix this
    az_lexer = Az_Lexer
    while True:
        try:
            text = prompt(get_prompt_tokens=get_prompt_tokens, lexer=az_lexer,
                          completer=az_completer, style=styles, history=history,
                          on_abort=AbortAction.RETRY, auto_suggest=AutoSuggestFromHistory(),
                          get_bottom_toolbar_tokens=get_bottom_toolbar_tokens)
                        #   get_rprompt_tokens=get_rprompt_tokens)
        except EOFError:
            break  # Control-D pressed.
        if text == "quit" or text == "exit":
            break
        p = subprocess.Popen("az " + text, shell=True)
        p.communicate()
    print('Have a lovely day!!')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        db = ':memory:'
    else:
        db = sys.argv[1]

    main(db)