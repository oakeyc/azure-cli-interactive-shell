from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

DEPENDENCIES = [
    'azure-cli',
    'prompt_toolkit'
]

setup(
    name='az-cli-shell',
    version='0.1.0.9',
    author='Microsoft Corporation',
    scripts=['dev_setup.py', 'az-cli'],
    packages=[
        "azure.clishell"
    ],
    url='https://github.com/oakeyc/azure-cli-interactive-shell',
    install_requires=DEPENDENCIES,
)