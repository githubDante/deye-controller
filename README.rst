DEYE-controller
===================

* A library and simple tools for interaction with DEYE hybrid inverters
* The communication with the inverter requires a SOLARMAN datalogger
* `pysloarmanv5 <https://github.com/jmccrohan/pysolarmanv5>`_ is used by the command line tools (exposed after install):
    - deye-read - read everything from the inverter (use --help for filters/options)
    - deye-regcheck - for quick check on specific register(s)
    - deye-scan is a scanner for dataloggers in the local network (not DEYE related)

* Tested with:
    - SUN-12K-SG04LP3 / LSW-3

TODO List
=============
* Support writing to all registers
* Register writing tool
* SellTime programmer
