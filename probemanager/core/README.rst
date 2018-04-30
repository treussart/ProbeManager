****
Core
****

Presentation
============

App for general things about project and probe.

Features
--------

* Jobs. To see the results of asynchronous tasks.
* List of the operating systems supported by this application.
* Server, remote server.
* Ssh Key, to authenticate on the remote server.
* General configuration of this application. (Pushbullet API KEY, MISP API KEY, SPLUNK HOST ...)
* Generic Probe.
* Genreic Probe configuration.

Usage
=====

Administration Page of the module :
-----------------------------------

.. image:: https://raw.githubusercontent.com/treussart/ProbeManager/develop/core/data/admin-index.png
  :align: center
  :width: 80%

Page to add a remote server :
-----------------------------

.. image:: https://raw.githubusercontent.com/treussart/ProbeManager/develop/core/data/admin-server-add.png
  :align: center
  :width: 70%

* Name: Give a unique name for this instance, example: server-tap1.
* Host:
* Os:
* Remote User:
* Remote port:
* Become
* Become method:
* Become user:
* Become pass:
* Ssh private key file:


Page to add a SSH Key :
-----------------------

.. image:: https://raw.githubusercontent.com/treussart/ProbeManager/develop/core/data/admin-sshkey-add.png
  :align: center
  :width: 60%

* Name:
* File:

Page to see results of asynchronous jobs :
------------------------------------------

.. image:: https://raw.githubusercontent.com/treussart/ProbeManager/develop/core/data/admin-jobs-full.png
  :align: center
  :width: 90%
