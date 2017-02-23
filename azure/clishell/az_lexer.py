from pygments.lexer import RegexLexer, words
from pygments.token import Name, Literal, Keyword, Operator, Text, Number
from azure.clishell.az_completer import AzCompleter

class AzLexer(RegexLexer):
    """
    A custom lexer for Azure CLI
    """
    completer = AzCompleter()

    tokens = {
        'root': [
            (r' .*\n', Text),
            (words(
                tuple(kid.data for kid in completer.command_tree.children),
                prefix=r'\b',
                suffix=r'\b'),
             Keyword),
            # describe-instances
            (words(
                tuple(completer.get_all_subcommands()),
                prefix=r'\b',
                suffix=r'\b'),
             Keyword.Declaration),
            # --instance-ids
            (words(
                tuple(param for param in completer.completable_param),
                prefix=r'',
                suffix=r'\b'),
             Name.Class),
            # Everything else
            (r'.*\n', Text),
        ]
    }

class ExampleLexer(RegexLexer):
    """ Lexer for the example description """
    tokens = {
        'root' : [
            (r' .*\n', Number),
            (r'.*\n', Number),
        ]
    }
