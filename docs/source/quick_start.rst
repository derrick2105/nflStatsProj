Getting Started
***************

Introduction
============
This section contains information on how to clone the repo, install the \
modules, and run the provided scripts. There is also a section on installing \
sphinx and the sphinx_rst_theme.


Clone and install the project Module
====================================
Clone the repository into the location of your choosing.
In order to run the provided scripts, you must add the src dir to your python path.

Linux:
To do this it is easiest to just add the following line of code to your
bash profile.

.. testcode::

    export PYTHONPATH=$HOME/nflStatsProj/src

This is assuming the name of your project dir is nflStatsProj and is located in your home folder. 


Run the populateDataBase script
===============================
.. WARNING:: Python must be installed on your computer in order to continue.
    Click `here <https://www.python.org/downloads/>`_ to install python.


From the terminal
-----------------
navigate to the nflStatsProj/src/scripts directory and enter the
following command.

 ..  testcode::

     $ python populateDataBase.py

Also note, this will only work for Mac and Linux machines. 

From  Pycharm
-------------
After opening the project, navigate to popoulateDataBase.py, right click 
the name and select run or debug.


Run the Driver script
=====================

From the terminal
-----------------
navigate to the nflStatsProj/src directory and enter the
following command.

 .. testcode::

    $ python Driver.py

From  Pycharm
-------------
After opening the project, navigate to Driver.py, right click the name and 
select run or debug. 

Install Sphinx Document generator
=================================
To install sphinx and the specific sphinx theme used in this project, follow
the below instructions

.. testcode::

    $ apt-get install python-sphinx
    $ pip install sphinx_rtd_theme


generate Sphinx Documents
=========================
To make the documents perform the following commands:

.. testcode::

    $ cd ~/nflStatsProj/docs
    $ make html

The generated html pages are located in the build/html folder.