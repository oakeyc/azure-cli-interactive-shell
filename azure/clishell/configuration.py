"""
Configuration settings
"""
import configparser
import os

class Configuration():
    """ Configuration information """
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config['DEFAULT'] = {
            'lexer' : 'AzLexer'
        }
        azure_folder = get_config_dir()
        if not os.path.exists(azure_folder):
            os.makedirs(azure_folder)
        with open(os.path.join(get_config_dir(), 'config'), 'w') as config_file:
            self.config.write(config_file)

    def load(self, path):
        """ loads the configuration settings """
        self.config.read(path)

    def get_lexer(self):
        return self.config.get('DEFAULT', 'lexer')

def get_config_dir():
    if os.getenv('AZURE_CONFIG_DIR'):
        return os.getenv('AZURE_CONFIG_DIR')
    else:
        return os.path.expanduser(os.path.join('~', '.azure-shell'))

