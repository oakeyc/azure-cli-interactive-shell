import shutil
import os
import collections

def get_window_dim():
    """ returns the rows, columns of terminal """
    dim = shutil.get_terminal_size()
    return dim.lines, dim.columns

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
