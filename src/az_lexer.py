from pygments.lexer import RegexLexer
from pygments.lexer import words
from pygments.token import Name, Literal, Keyword, Operator, Text, Number
from commands_inventory import CompletionIndex


"""
Az_Lexer is a lexer for Microsoft Azure
"""
class Az_Lexer(RegexLexer):
    # should be the commandlist dump
    completion_index = CompletionIndex()
    completion_index.load_completions()
    tokens = {
        'root': [
            # 
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
                prefix=r'\b',
                suffix=r'\b'),
             Keyword.Declaration),
            # Everything else
            (r'.*\n', Text),
        ]
    }
