=============
Probe Manager
=============

|Licence| |Version|


|Code_Health| |Coverage_Status|

+------------------+--------------------+
| Status           | Operating system   |
+==================+====================+
| |Build_Status|   | Linux x86\_64      |
+------------------+--------------------+

.. |Licence| image:: https://img.shields.io/github/license/matleses/ProbeManager.svg
.. |Stars| image:: https://img.shields.io/github/stars/matleses/ProbeManager.svg
.. |Forks| image:: https://img.shields.io/github/forks/matleses/ProbeManager.svg
.. |Downloads| image:: https://img.shields.io/github/downloads/matleses/ProbeManager/total.svg
.. |Version| image:: https://img.shields.io/github/tag/matleses/ProbeManager.svg
.. |Commits| image:: https://img.shields.io/github/commits-since/matleses/ProbeManager/latest.svg
.. |Code_Health| image:: https://landscape.io/github/matleses/ProbeManager/master/landscape.svg?style=flat
   :target: https://landscape.io/github/matleses/ProbeManager/master
.. |Coverage_Status| image:: https://coveralls.io/repos/github/matleses/ProbeManager/badge.svg?branch=master
   :target: https://coveralls.io/github/matleses/ProbeManager?branch=master
.. |Build_Status| image:: https://travis-ci.org/matleses/ProbeManager.svg?branch=master
   :target: https://travis-ci.org/matleses/ProbeManager



Presentation
~~~~~~~~~~~~

It is common to note that many IDS which are installed on a system,
are not updated, as well on the side of the software, as rules.
This can be explained because maintenance and rule management are complicated.
This observation made me want to develop an application that would better manage network
and machine detection probes on a system.

ProbeManager is an application that centralizes the management of intrusion detection system.
For the moment the NIDS Suricata is implemented and Bro and OSSEC are being implemented.

features
^^^^^^^^

 * Search rules in those of all probes.
 * List of installed probes and their status.
 * Push notifications (change of status, ...)
 * API.

TODO
^^^^

 * Create an IHM for show all the running tasks.

Installation
~~~~~~~~~~~~

Operating System
================

OSX and Debian are Supported.

Requirements
============

-  Python3.
-  Pip with access to repository
-  Rabbitmq-server (installed with install script)
-  Postgresql (installed with install script)

Retrieve the project
====================

.. code-block:: sh

    git clone --recursive https://github.com/matleses/ProbeManager.git

Install
=======


For developer :
---------------

.. code-block:: sh

    ./install.sh
    ./start.sh

For Production :
----------------

.. code-block:: sh

    sudo ./install.sh prod [destination path]

With Django server (not recommended) :

.. code-block:: sh

    [destination path]./start.sh prod

With Apache (Only for Debian) :

.. code-block:: sh

     http://localhost

Launch the tests
================

.. code-block:: sh

    ./test.sh


Open the file with a web browser :

::

    coverage_html/index.html


Modules
~~~~~~~


Add a submodule
===============

.. code-block:: sh

    git submodule add -b master --name suricata https://github.com/matleses/ProbeManager_Suricata.git probemanager/suricata

Modules must respect a few rules:
 * A file version.txt (generate by install script)
 * A folder doc with a file index.rst
 * A folder api with a variable urls_to_register into urls.py


Documentation
~~~~~~~~~~~~~


Respect the standard : reStructuredText (RST).

.. code-block:: sh

    venv/bin/python probemanager/manage.py runscript generate_doc --settings=probemanager.settings.dev --script-args -


Open the file with a web browser :

::

    docs/_build/html/index.html


Conventions
~~~~~~~~~~~

Respect the syntax and rules PEP8

.. code-block:: sh

    flake8 .


Update
~~~~~~


Repository
==========

.. code-block:: sh

    git pull origin master
    git submodule foreach git pull origin master


PIP Packets
===========

.. code-block:: sh

    See upgrades :
    pip list --outdated --format=freeze
    Apply upgrades :
    pip list --outdated | cut -d' ' -f1 | xargs pip install --upgrade

    Upgrade pip :
    pip install --upgrade pip
