from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

DEPENDENCIES = [
    'azure-cli',
    'prompt_toolkit'
]

setup(
    name='az-cli-shell',
    version='0.1.0.3',
    author='Microsoft Corporation',
    scripts=['dev_setup.py', 'src/dump_commands.py'],
    packages=[
        "src",
    ],
    entry_points={
        'console_scripts' : ['src=src:main']
    },
    url='https://github.com/oakeyc/azure-cli-interactive-shell',
    install_requires=DEPENDENCIES,
)