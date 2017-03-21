import os
import collections
import platform

from prompt_toolkit.styles import style_from_dict
from pygments.token import Token

def get_window_dim():
    """ gets the dimensions depending on python version and os"""
    if platform.system() == 'Windows':
        return _size_36_windows()
    if platform.python_version() == "3.6.0":
        return _size_36_windows()
    else:
        return _size_27()

def _size_27():
    """ works for python """
    return os.popen('stty size', 'r').read().split()

def _size_36_windows():
    """ returns the rows, columns of terminal """
    from shutil import get_terminal_size
    dim = get_terminal_size()
    return dim.lines, dim.columns

def default_style():
    """ Default coloring """
    if platform.system() == 'Windows':
        styles = style_from_dict({
            # Completion colors
            Token.Menu.Completions.Completion.Current: 'bg:#7c2c80 #ffffff',
            Token.Menu.Completions.Completion: 'bg:#00b7b7 #ffffff',
            Token.Menu.Completions.ProgressButton: 'bg:#b78991',
            Token.Menu.Completions.ProgressBar: 'bg:#ffc0cb',

            Token.Az: '#7c2c80',
            Token.Prompt.Arg: '#888888',

            # Pretty Words
            Token.Keyword: '#965699',
            Token.Keyword.Declaration: '#ab77ad',
            Token.Name.Class: '#c49fc5',
            Token.Text: '#0f5050',

            Token.Line: '#E500E5',
            Token.Number: '#00ffff',
            # toolbar
            Token.Operator: 'bg:#000000 #ffffff',
            Token.Toolbar: 'bg:#000000 #ffffff'
        })

    else:
        styles = style_from_dict({
            # Completion colors
            Token.Menu.Completions.Completion.Current: 'bg:#7c2c80 #ffffff',
            Token.Menu.Completions.Completion: 'bg:#00b7b7 #ffffff',
            Token.Menu.Completions.ProgressButton: 'bg:#b78991',
            Token.Menu.Completions.ProgressBar: 'bg:#ffc0cb',

            Token.Az: '#7c2c80',
            Token.Prompt.Arg: '#888888',

            # Pretty Words
            Token.Keyword: '#965699',
            Token.Keyword.Declaration: '#ab77ad',
            Token.Name.Class: '#c49fc5',
            Token.Text: '#666666',

            Token.Line: '#E500E5',
            Token.Number: '#3d79db',
            # toolbar
            Token.Operator: 'bg:#000000 #ffffff',
            Token.Toolbar: 'bg:#000000 #ffffff'
        })

    return styles
# def get_window_size_osx():
#     rows, cols = os.popen('stty size', 'r').read().split()
#     return int(cols), int(cols)

def dict_path(keyword, dictionaries):
    """ finds the path to the keyword """
    list_of_options = []
    if isinstance(dictionaries, list):
        for dictionary in dictionaries:
            _dict_path(keyword, dictionary, list_of_options)
    elif isinstance(dictionaries, dict):
        _dict_path(keyword, dictionaries, list_of_options)
    return list_of_options

def _dict_path(keyword, dictionary, list_of_options):
    if not isinstance(dictionary, collections.Iterable):
        list_of_options.append(dictionary)
    elif keyword in dictionary:
        if isinstance(dictionary, dict):
            list_of_options.append(dictionary[keyword])
        else:
            list_of_options.append(keyword)
    else:
        for item in dictionary:
            if isinstance(item, dict):
                list_of_options.extend(dict_path(keyword, item))
