# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from setuptools import setup
from codecs import open

DEPENDENCIES = [
    'azure-cli',
    'prompt_toolkit',
    'six',
    'pyyaml',
    'jmespath',
]
with open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()

setup(
    name='azure-cli-shell',
    version='0.1.1a8',
    description='Microsoft Azure Command-Line Interactive Shell',
    long_description=README + '\n\n',
    license='MIT',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    scripts=['az-shell.bat', 'az-shell'],
    packages=[
        "azclishell"
    ],
    url='https://github.com/oakeyc/azure-cli-interactive-shell',
    install_requires=DEPENDENCIES,
)
