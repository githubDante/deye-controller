DEYE-controller
===================

* A library and simple tools for interaction with DEYE hybrid inverters
* The communication with the inverter requires a SOLARMAN datalogger
* `pysloarmanv5 <https://github.com/jmccrohan/pysolarmanv5>`_  based library
* Command line tools (exposed after install):
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
    ____________________________________________________
    | Grid  |  Gen  |      Time     |   Pwr    |  SOC % |
    |       |       | 00:00 | 03:00 |     3500 |   100% |
    |       |       | 03:00 | 04:00 |     3500 |    30% |
    |       |       | 04:00 | 05:00 |     3500 |    30% |
    |       |       | 05:00 | 10:00 |     3500 |    30% |
    |       |       | 10:00 | 23:00 |     3500 |   100% |
    |       |       | 23:00 | 00:00 |     3500 |    30% |
    ----------------------------------------------------
    >>> prog.update_program(3, start_t='6:30', power=2500, soc=35, grid_ch=True)
    Program updated
     >>> prog.show_as_screen()  # For visual confirmation of the settings
    ____________________________________________________
    | Grid  |  Gen  |      Time     |   Pwr    |  SOC % |
    |       |       | 00:00 | 03:00 |     3500 |   100% |
    |       |       | 03:00 | 04:00 |     3500 |    30% |
    |       |       | 04:00 | 06:30 |     3500 |    30% |
    |   ✓   |       | 06:30 | 10:00 |     2500 |    35% |
    |       |       | 10:00 | 23:00 |     3500 |   100% |
    |       |       | 23:00 | 00:00 |     3500 |    30% |
    ----------------------------------------------------
    >>> prog.upload_settings()  # In order to upload the settings to the inverter


Notes
=========
* It is possible the inverter to be completely deactivated by writing 0 to register 80
  WritableRegisters.SwitchOnOff.set(False) but it will raise an alarm and will show error F19.
  The normal state is restored as soon as the register is set to its default value 1.
