from pygments.lexer import RegexLexer, words
from pygments.token import Name, Literal, Keyword, Operator, Text, Number
from az_completer import AzCompleter


class ArgsLexer(RegexLexer):
    """
    A custom lexer for the help and arguments
    """
    completer = AzCompleter()

    # should be the commandlist dump
    tokens = {
        'root': [
            (words(
                tuple(completer.param_dict.values()),
                prefix=r'\b',
                suffix=r'\b'),
             Keyword),
        ]
    }
