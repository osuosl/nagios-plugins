=====================
OSUOSL Nagios Plugins
=====================

This is a collection of perl and python nagios checks used by the
OSUOSL_. Some of them are written using the pynagios_ library.

Plugins:

* check_bacula.py
    Check bacula to make sure specific jobs are getting executed.

Sample check_bacula.py usage::

  $ ./check_bacula.py -c1: -w2: --hours 72 -j <JOB>


.. _OSUOSL: http://osuosl.org
.. _pynagios: http://github.com/kiip/pynagios
