import shutil
import os

def get_window_size_p3_windows():
    dim = shutil.get_terminal_size()
    return dim.columns, dim.lines

def get_window_size_osx():
    rows, cols = os.popen('stty size', 'r').read().split()
    return int(cols), int(cols)