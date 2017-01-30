from prompt_toolkit.enums import DEFAULT_BUFFER, SEARCH_BUFFER
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, FloatContainer, ConditionalContainer, Float
from prompt_toolkit.layout.controls import BufferControl, FillControl, TokenListControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.lexers import PygmentsLexer
from pygments.lexer import Lexer
from prompt_toolkit.filters import Always, HasFocus
from prompt_toolkit.layout.menus import CompletionsMenu, MultiColumnCompletionsMenu
from prompt_toolkit.layout.processors import PasswordProcessor, \
    HighlightSearchProcessor, HighlightSelectionProcessor, \
    ConditionalProcessor, AppendAutoSuggestion

from pygments.token import Token
# from az_lexer import AzLexer


def get_options_tokens(self):
    return[(
        Token.Hello, "Hello",
        Token.World, "World"
    )]
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

def get_height(cli):
    return D(min=8)

def create_layout(lexer):
    try:
        if isinstance(lexer, Lexer):
            lexer = PygmentsLexer(lexer)
    except TypeError:
        pass  # no lexer
    layout = HSplit([
        # One window that holds the BufferControl with the default buffer on the
        # left.
        Window(content=BufferControl(buffer_name=DEFAULT_BUFFER)),

        # Window(
        #     BufferControl(
        #         # lexer=PygmentsLexer(lexer)
        #     )
        # ),
          FloatContainer(
                Window(
                    BufferControl(
                        input_processors=input_processors,
                        lexer=lexer,
                        # Enable preview_search, we want to have immediate
                        # feedback in reverse-i-search mode.
                        preview_search=Always()),
                    get_height=get_height,
                ),
                [
                    Float(xcursor=True,
                          ycursor=True,
                          content=CompletionsMenu(
                              max_height=16,
                              scroll_offset=1,
                              extra_filter=(HasFocus(DEFAULT_BUFFER)))),
                    # Float(xcursor=True,
                    #       ycursor=True,
                    #       content=MultiColumnCompletionsMenu(
                    #           extra_filter=(HasFocus(DEFAULT_BUFFER)),
                    #           show_meta=Always()))
                ]
            ),

        Window(width=D.exact(1),
                content=FillControl(' ', token=Token.Line)),

        # A vertical line in the middle. We explicitely specify the width, to make
        # sure that the layout engine will not try to divide the whole width by
        # three for all these windows. The `FillControl` will simply fill the whole
        # window by repeating this character.
        Window(width=D.exact(1),
                content=FillControl('-', token=Token.Line)),

        Window(width=D.exact(1),
                content=TokenListControl(get_options_tokens, align_center=True)),
    ])
    return layout
 