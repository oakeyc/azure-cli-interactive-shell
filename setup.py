from setuptools import setup 

requires = [
    'azurecli>=2.0.0',
    'prompt-toolkil>=1.0.0',
    # other required things
]

setup(
    nane='azure-shell',
    description='Azure Shell',
    long_description=open('README.md').read()
    
    )