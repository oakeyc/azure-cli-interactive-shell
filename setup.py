from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

DEPENDENCIES = [
    'azure-cli',
    'prompt_toolkit',
    'six',
    'pyyaml'
]

setup(
    name='az-cli-shell',
    version='0.1.1a310',
    author='Microsoft Corporation',
    scripts=['dev_setup.py', 'az-cli'],
    packages=[
        "azure.clishell", "test"
    ],
    namespace_packages=[
        'azure',
    ],
    url='https://github.com/oakeyc/azure-cli-interactive-shell',
    install_requires=DEPENDENCIES,
)
