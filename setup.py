from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

DEPENDENCIES = [
    'azure-cli',
    'prompt_toolkit',
    'six',
    'pyyaml',
    'pytest',
    'jmespath',
]

setup(
    name='az-cli-shell',
    version='0.1.1a27',
    author='Microsoft Corporation',
    scripts=['dev_setup.py', 'az-cli'],
    packages=[
        "azclishell", "test"
    ],
    namespace_packages=[
        'azclishell',
    ],
    url='https://github.com/oakeyc/azure-cli-interactive-shell',
    install_requires=DEPENDENCIES,
)
