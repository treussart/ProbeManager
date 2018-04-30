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

.. image:: https://raw.githubusercontent.com/treussart/ProbeManager/develop/probemanager/core/data/admin-index.png
  :align: center
  :width: 80%

Page to add a remote server :
-----------------------------

.. image:: https://raw.githubusercontent.com/treussart/ProbeManager/develop/probemanager/core/data/admin-server-add.png
  :align: center
  :width: 70%

* Name: Give a unique name for this instance, example: server-tap1.
* Host: The IP address or Hostname.
* Os: The Operating system (Debian or Ubuntu).
* Remote User: The user used for the connection 'ssh user@hostname'
* Remote port: The remote port 'ssh -p 22'.
* Become: True or False, if he needs to elevate the privileges to be root.
* Become method:
* Become user: Often root, but you can use an another user with fewer privileges than root.
* Become pass: The password if needed for the user you have become.
* Ssh private key file: The private key file for authenticate.


Page to add a SSH Key :
-----------------------

.. image:: https://raw.githubusercontent.com/treussart/ProbeManager/develop/probemanager/core/data/admin-sshkey-add.png
  :align: center
  :width: 60%

* Name: A name for this key. (In the API, the name is the name of the file)
* File: The file to upload. (In the API, the file is the text file of the private key)

Page to see results of asynchronous jobs :
------------------------------------------

.. image:: https://raw.githubusercontent.com/treussart/ProbeManager/develop/probemanager/core/data/admin-jobs-full.png
  :align: center
  :width: 90%
