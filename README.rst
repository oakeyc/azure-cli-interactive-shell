Azure CLI Interactive Shell
****************************
The interactive shell for Microsoft Azure CLI (Command Line Interface)
######################################################################

* Lightweight Drop Down Completions 
* Fun Colors 
* Auto Cached Suggestions 
* On the fly descriptions of the commands AND parameters 
* On the fly examples of how to utilize each command 
* Optional layout configurations 
* Navigation of example pane 
* Command recall with arrow keys 
* Dynamic parameter completion 
* Optional "az" component 
* Query the previous command

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

But Wait, There Will Be More!
#############################
* Interactive Tutorials
* Telemetry
* Real-time Notifications