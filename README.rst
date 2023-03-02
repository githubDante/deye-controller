DEYE-controller
===================

* A library and simple tools for interaction with DEYE hybrid inverters
* The communication with the inverter requires a SOLARMAN datalogger
* `pysloarmanv5 <https://github.com/jmccrohan/pysolarmanv5>`_ is used by the command line tools (exposed after install):
    - deye-read - read everything from the inverter (use --help for filters/options)
    - deye-regcheck - for quick check on specific register(s)
    - deye-scan is a scanner for dataloggers in the local network (not DEYE related)
    - deye-regwrite - for writing to individual registers

* Tested with:
    - SUN-12K-SG04LP3 / LSW-3

TODO List
=============
* Support for writing to all registers


Examples
==============

* SellMode programming:

  .. code-block::

    >>> from deye_controller.sell_programmer import SellProgrammer
    >>> prog = SellProgrammer('192.168.1.108', 2799999999)
    >>> prog.show_as_screen()
    _____________________________________
    |      Time     |   Pwr    |  SOC % |
    | 00:00 | 18:00 |     3500 |   100% |
    | 18:00 | 19:00 |     3500 |    30% |
    | 19:00 | 20:00 |     3500 |    30% |
    | 20:00 | 21:00 |     3500 |    30% |
    | 21:00 | 22:00 |     3500 |    30% |
    | 22:00 | 00:00 |     3500 |    30% |
    -------------------------------------
    >>> prog.update_program(3, start_t='20:30', power=2500, soc=35)
    Program updated
    >>> prog.show_as_screen()  # For visual confirmation of the settings
    _____________________________________
    |      Time     |   Pwr    |  SOC % |
    | 00:00 | 18:00 |     3500 |   100% |
    | 18:00 | 19:00 |     3500 |    30% |
    | 19:00 | 20:30 |     3500 |    30% |
    | 20:30 | 21:00 |     2500 |    35% |
    | 21:00 | 22:00 |     3500 |    30% |
    | 22:00 | 00:00 |     3500 |    30% |
    -------------------------------------
    >>> prog.upload_settings()  # In order to upload the settings to the inverter
