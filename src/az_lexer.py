from pygments.lexer import RegexLexer, words
from pygments.token import Name, Literal, Keyword, Operator, Text, Number
from commands_inventory import CompletionIndex


class AzLexer(RegexLexer):
    """
    A custom lexer for Azure CLI
    """

    # should be the commandlist dump
    completion_index = CompletionIndex()
    completion_index.load_completions()
    tokens = {
        'root': [
            (words(
                tuple(completion_index.commands),
                prefix=r'\b',
                suffix=r'\b'),
             Keyword),
            # describe-instances
            (words(
                tuple(completion_index.subcommands),
                prefix=r'\b',
                suffix=r'\b'),
             Name.Class),
            # --instance-ids
            (words(
                tuple(completion_index.args_opts),
                prefix='',
                suffix=''),
             Keyword.Declaration),
            # Everything else
            (r'.*\n', Text),
        ]
    }
