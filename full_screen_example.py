from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.application import Application
from prompt_toolkit.shortcuts import create_eventloop
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FillControl, TokenListControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.buffer import Buffer


from pygments.token import Token
layout = VSplit([
    # One window that holds the BufferControl with the default buffer on the
    # left.
    Window(content=BufferControl(buffer_name=DEFAULT_BUFFER)),

    # A vertical line in the middle. We explicitely specify the width, to make
    # sure that the layout engine will not try to divide the whole width by
    # three for all these windows. The `FillControl` will simply fill the whole
    # window by repeating this character.
    Window(width=D.exact(1),
           content=FillControl('|', token=Token.Line)),    
    Window(width=D.exact(1),
           content=FillControl('|', token=Token.Line)),
           

    # Display the Result buffer on the right.
    Window(content=BufferControl(buffer_name='RESULT')),
])


def get_titlebar_tokens(cli):
    return [
        (Token.Title, ' Hello world '),
        (Token.Title, ' (Press [Ctrl-Q] to quit.)'),
    ]

layout = HSplit([
    # The titlebar.
    Window(height=D.exact(1),
           content=TokenListControl(get_titlebar_tokens, align_center=True)),

    Window(height=D.exact(5),
           content=TokenListControl(get_titlebar_tokens, align_center=True)),

    # Horizontal separator.
    Window(height=D.exact(5),
           content=FillControl('*', token=Token.Line)),

    # The 'body', like defined above.
    layout,
])

buffers={
    DEFAULT_BUFFER: Buffer(is_multiline=True),
    'RESULT': Buffer(is_multiline=True),
}

# Now we add an event handler that captures change events to the buffer on the
# left. If the text changes over there, we'll update the buffer on the right.

def default_buffer_changed(default_buffer):
    """
    When the buffer on the left (DEFAULT_BUFFER) changes, update the buffer on
    the right. We just reverse the text.
    """
    buffers['RESULT'].text = buffers[DEFAULT_BUFFER].text[::-1]


buffers[DEFAULT_BUFFER].on_text_changed += default_buffer_changed


manager = KeyBindingManager()
registry = manager.registry

@registry.add_binding(Keys.ControlQ, eager=True)
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `CommandLineInterface.run()` call.
    """
    event.cli.set_return_value(None)

loop = create_eventloop()
application = Application(
    key_bindings_registry=registry,
    layout=layout,
    buffers=buffers)
cli = CommandLineInterface(application=application, eventloop=loop)
cli.run()
print('Exiting')