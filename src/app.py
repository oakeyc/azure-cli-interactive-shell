from __future__ import unicode_literals
import sys

from prompt_toolkit import prompt, AbortAction
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter
from pygments.style import Style
from pygments.token import Token
from pygments.styles.default import DefaultStyle
from az_completer import Az_Completer
from az_lexer import Az_Lexer

class DocumentStyle(Style):
    styles = {
        Token.Menu.Completions.Completion.Current: 'bg:#ffc0cb #000000',
        Token.Menu.Completions.Completion: 'bg:#00b7b7 #ffffff',
        Token.Menu.Completions.ProgressButton: 'bg:#b78991',
        Token.Menu.Completions.ProgressBar: 'bg:#ffc0cb',
    }
    styles.update(DefaultStyle.styles)

def main(database):
    history = InMemoryHistory()
    az_completer = Az_Completer().wordCompleter()
   # connection = azure.connect(database) TODO fix this
    az_lexer = Az_Lexer
    while True:
        try:
            text = prompt('az>> ', lexer=az_lexer, completer=az_completer,
                          style=DocumentStyle, history=history,
                          on_abort=AbortAction.RETRY)
        except EOFError:
            break  # Control-D pressed.
        #with connection:
         #   messages = connection.execute(text)
          #  for message in messages:
           #     print(message)
    print('GoodBye!')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        db = ':memory:'
    else:
        db = sys.argv[1]

    main(db)