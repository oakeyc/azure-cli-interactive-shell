Azure CLI Interactive Shell
****************************
The interactive shell for Microsoft Azure CLI (Command Line Interface)
######################################################################

* Completion Suggestions
* On the fly documentation
* Auto-suggestions from history
* Fun Colors

Installation
############
.. code-block:: console

   $ pip install az-cli-shell

Running
########

To start the application

.. code-block:: console

   $ az-cli

Then type your commands and hit [Enter]

*to run commands outside of the shell, start the command with #*

To scroll through the examples Control H to page up and Control N to page down

To Search through the last command as json

.. code-block:: console

   $ ? [param]

Dev Setup
########

Fork and clone repository

.. code-block:: console

   $ . dev_setup.py

To get the Exit Code of the previous command:

.. code-block:: console

   $ $
