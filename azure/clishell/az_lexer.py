from pygments.lexer import RegexLexer, words
from pygments.token import Name, Literal, Keyword, Operator, Text, Number

from azure.clishell.gather_commands import GatherCommands
class AzLexer(RegexLexer):
    """
    A custom lexer for Azure CLI
    """
    commands = GatherCommands()
    # top_level = []
    # top_level.append(kid.data for kid in completer.command_tree.children)
    # top_level.append('az')
    tokens = {
        'root': [
            (words(
                tuple(kid.data for kid in commands.command_tree.children),
                prefix=r'\b',
                suffix=r'\b'),
             Keyword),
            # describe-instances
            (words(
                tuple(commands.get_all_subcommands()),
                prefix=r'\b',
                suffix=r'\b'),
             Keyword.Declaration),
            # --instance-ids
            (words(
                tuple(param for param in commands.completable_param),
                prefix=r'',
                suffix=r'\b'),
             Name.Class),
            # Everything else
            (r'.', Text),
            (r' .', Text),
        ]
    }

class ExampleLexer(RegexLexer):
    """ Lexer for the example description """
    tokens = {
        'root' : [
            (r' .', Number),
            (r'.', Number),
        ]
    }

class ToolbarLexer(RegexLexer):
    """ Lexer for the example description """
    tokens = {
        'root' : [
            (r' .', Operator),
            (r'.', Operator),
        ]
    }
