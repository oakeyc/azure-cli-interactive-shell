

from prompt_toolkit.enums import DEFAULT_BUFFER, SEARCH_BUFFER
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, FloatContainer, ConditionalContainer, Float
from prompt_toolkit.layout.controls import BufferControl, FillControl, TokenListControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.lexers import PygmentsLexer
from prompt_toolkit.filters import Always, HasFocus, IsDone, RendererHeightIsKnown
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.processors import HighlightSearchProcessor, \
    HighlightSelectionProcessor, \
    ConditionalProcessor, AppendAutoSuggestion
from prompt_toolkit.layout.lexers import Lexer as PromptLex
from prompt_toolkit.layout.prompt import DefaultPrompt
from prompt_toolkit.layout.screen import Char

from pygments.token import Token
from pygments.lexer import Lexer as PygLex

from azure.clishell.az_lexer import ExampleLexer, ToolbarLexer
import azure.clishell.configuration

MAX_COMPLETION = 16

# TODO fix this somehow
input_processors = [
    ConditionalProcessor(
        # By default, only highlight search when the search
        # input has the focus. (Note that this doesn't mean
        # there is no search: the Vi 'n' binding for instance
        # still allows to jump to the next match in
        # navigation mode.)
        HighlightSearchProcessor(preview_search=Always()),
        HasFocus(SEARCH_BUFFER)),
    HighlightSelectionProcessor(),
    ConditionalProcessor(
        AppendAutoSuggestion(), HasFocus(DEFAULT_BUFFER)),
]

def get_prompt_tokens(cli):
    """ returns prompt tokens """
    return [(Token.Az, 'az>> ')]

def get_height(cli):
    """ gets the height of the cli """
    if not cli.is_done:
        return D(min=8)

def create_layout(lex):
    """ creates the layout """
    config = azure.clishell.configuration.CONFIGURATION


    lexer = None
    if issubclass(lex, PromptLex):
        lexer = lex
    elif issubclass(lex, PygLex):
        lexer = PygmentsLexer(lex)

    exampleLex = ExampleLexer
    if issubclass(exampleLex, PygLex):
        examLex = PygmentsLexer(exampleLex)

    toolbarLex = ToolbarLexer
    if issubclass(toolbarLex, PygLex):
        toolbarLex = PygmentsLexer(toolbarLex)

    input_processors.append(DefaultPrompt(get_prompt_tokens))

    layout = HSplit([
        FloatContainer(
            Window(
                BufferControl(
                    input_processors=input_processors,
                    lexer=lexer,
                    preview_search=Always()),
                get_height=get_height,
            ),
            [
                Float(xcursor=True,
                      ycursor=True,
                      content=CompletionsMenu(
                          max_height=MAX_COMPLETION,
                          scroll_offset=1,
                          extra_filter=(HasFocus(DEFAULT_BUFFER))
                          ))
            ]),
        Window(width=D.exact(1), height=D.exact(1), content=FillControl('-', token=Token.Line)),

        get_descriptions(config, examLex, lexer),
        get_examplehline(config),
        get_example(config, examLex),
        # Window(
        #     content=BufferControl(
        #         buffer_name='bottom_toolbar',
        #         lexer=toolbarLex
        #     )
        # ),

    ])
    return layout

def get_descript(lexer):
    return Window(
        content=BufferControl(
            buffer_name="description",
            lexer=lexer

            ),
        )

def get_param(lexer):
    return Window(
        content=BufferControl(
            buffer_name="parameter",
            lexer=lexer
            ),
        )

def get_example(config, examLex):
    if config.config.get('Layout', 'examples') == 'yes':
        return Window(
            content=BufferControl(
                buffer_name="examples",
                lexer=examLex
                ),
            )
    else:
        return get_empty()

def get_examplehline(config):
    if config.config.get('Layout', 'examples') == 'yes':
        return get_hline()
    else:
        return get_empty()

def get_empty():
    return Window(
        content=FillControl(' ')
    )

def get_hline():
    return Window(
        width=D.exact(1),
        height=D.exact(1),
        content=FillControl('-', token=Token.Line))

def get_vline():
    return Window(
        width=D.exact(1),
        height=D.exact(1),
        content=FillControl('*', token=Token.Line))

def get_descriptions(config, examLex, lexer):
    if config.config.get('Layout', 'command_description') == 'yes':
        if config.config.get('Layout', 'param_description') == 'yes':
            return VSplit([
                get_descript(examLex),
                get_vline(),
                get_param(lexer),
            ])
        else:
            return get_descript(examLex)

    elif config.config.get('Layout', 'param_description') == 'yes':
        return get_param(lexer)
    else:
        return get_empty()

