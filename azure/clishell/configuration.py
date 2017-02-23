"""
Configuration settings
"""
from six.moves import configparser
import os

class Configuration():
    """ Configuration information """
    def __init__(self):
        self.config = configparser.ConfigParser({
            'firsttime' : 'yes',
            'lexer' : 'AzLexer',
        })
        self.config.add_section('Help Files')
        self.config.set('Help Files', 'command', 'help_dump.json')

        self.config.set('Help Files', 'history', 'history.txt')

        azure_folder = get_config_dir()
        if not os.path.exists(azure_folder):
            os.makedirs(azure_folder)
        if not os.path.exists(os.path.join(get_config_dir(), 'config')):
            with open(os.path.join(get_config_dir(), 'config'), 'w') as config_file:
                self.config.write(config_file)
        else:
            with open(os.path.join(get_config_dir(), 'config'), 'r') as config_file:
                self.config.readfp(config_file)

    def get_history(self):
        """ returns the history """
        return self.config.get('Help Files', 'history')

    def get_help_files(self):
        """ returns where the command table is cached """
        return self.config.get('Help Files', 'command')

    def load(self, path):
        """ loads the configuration settings """
        self.config.read(path)

    def get_lexer(self):
        """ gets the kind of the lexer """
        return self.config.get('DEFAULT', 'lexer')

    def firsttime(self):
        """ sets it as already done"""
        self.config.set('DEFAULT', 'firsttime', 'no')
        with open(os.path.join(get_config_dir(), 'config'), 'w') as config_file:
            self.config.write(config_file)

def get_config_dir():
    """ gets the directory of the configuration """
    if os.getenv('AZURE_CONFIG_DIR'):
        return os.getenv('AZURE_CONFIG_DIR')
    else:
        return os.path.expanduser(os.path.join('~', '.azure-shell'))

