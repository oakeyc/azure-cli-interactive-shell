from setuptools import setup

DEPENDENCIES = [

]

setup(
    name='az-cli-shell',
    version='0.1.0.3',
    author='Microsoft Corporation',
    scripts=['dev_setup.py', 'az-cli'],
    packages=[
        # '',
    ],
    install_requires=DEPENDENCIES,
)