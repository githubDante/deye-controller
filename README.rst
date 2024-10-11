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

* Monkey patching:
    - direct value assignment on read for the Register and RegistersGroup types (see the examples dir)

* Tested with:
    - SUN-12K-SG04LP3 / LSW-3

INSTALL
========

.. code-block:: console

  pip install deye-controller


TODO List
=============
* Support single phase inverters, eventually with auto detection.

Examples
==============
* After version 0.2.0 PySolarmanV5 can be patched for even easier reading `see here <examples/README_PATCH.rst>`_
* Basic usage:

    * read a register from the inverter

    .. code-block:: python

        >>> from deye_controller import HoldingRegisters, WritableRegisters
        >>> from pysolarmanv5 import PySolarmanV5
        >>> inv = PySolarmanV5('192.168.1.100', 2712345678)
        >>> register = HoldingRegisters.BMSBatteryCapacity
        >>> res = inv.read_holding_registers(register.address, register.len)
        >>> register.value = res[0] if register.len == 1 else res
        >>> print(register.description, register.format(), register.suffix)
        bms_battery_SOC 24 %
        >>> inv.disconnect()
    ..

    * write

    .. code-block:: python

        >>> from deye_controller import HoldingRegisters, WritableRegisters
        >>> from pysolarmanv5 import PySolarmanV5
        >>> inv = PySolarmanV5('192.168.1.100', 2712345678)
        >>> register = WritableRegisters.SellModeSOC3
        >>> register.set(23)

        >>> inv.write_multiple_holding_registers(register.address, [register.modbus_value])
        1
        >>> inv.disconnect()



* SellMode programming:

  .. code-block:: python

    >>> from deye_controller import SellProgrammer
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
    >>> prog.disconnect()  # Needed if PySolarmanV5 >= 3.0.0


Notes
=========
* It is possible the inverter to be completely deactivated by writing 0 to register 80
  WritableRegisters.SwitchOnOff.set(False) but it will raise an alarm and will show error F19.
  The normal state is restored as soon as the register is set to its default value 1.
* The WritableRegisters.GridExportLimit register can be used if the grid export is not desired
  when the battery is charged and the PV generation exceeds the load.
