Additional examples
====================

* Custom scaling

  .. code-block:: python

    >>> HoldingRegisters.PV1InPower.value = 5000
    >>> HoldingRegisters.PV1InPower.format()
    5000
    >>> HoldingRegisters.PV1InPower.suffix
    'W'
    >>> HoldingRegisters.PV1InPower.format_custom(1000, 'k')
    5.0
    >>> HoldingRegisters.PV1InPower.suffix
    'kW'

* Faster reading

  .. code-block:: python

    >>> from pysolarmanv5 import PySolarmanV5
    >>> from deye_controller.utils import group_registers, map_response
    >>> from deye_controller.modbus.protocol import BatteryOnlyRegisters, TotalPowerOnly, HoldingRegisters
    >>>
    >>> selection = ['BatteryChargeToday', 'BatteryDischargeToday', 'BatteryChargeTotal',
    ...  'BMSChargedVoltage', 'BMSDischargedVoltage', 'BMSChargingCurrentLimit',
    ...  'BMSDischargeCurrentLimit', 'BMSBatteryCapacity', 'BMSBatteryVoltage',
    ...  'BMSBatteryCurrent']
    >>> regs = [getattr(HoldingRegisters, attr) for attr in selection]
    >>> len(regs)
    10
    >>> groups = group_registers(regs)
    >>> len(groups)
    2
    >>> modbus = PySolarmanV5('192.168.100.102', 2999999999)
    >>>
    >>> for group in groups:
    ...     res = modbus.read_holding_registers(group.start_address, group.len)
    ...     map_response(res, group)
    ...     for reg in group:
    ...         if hasattr(reg, 'suffix'):
    ...             suffix = reg.suffix
    ...         else:
    ...             suffix = ''
    ...         string = '[{:>35s}]: {} {}'.format(reg.description.title(), reg.format(), suffix)
    ...         print(string, flush=True)
    ...
    [                Bms_Charged_Voltage]: 56.0 V
    [             Bms_Discharged_Voltage]: 0.0 V
    [           Bms_Charge_Current_Limit]: 400 A
    [        Bms_Discharge_Current_Limit]: 400 A
    [                    Bms_Battery_Soc]: 82 %
    [                Bms_Battery_Voltage]: 52.91 V
    [                Bms_Battery_Current]: -87 A
    [               Battery_Charge_Today]: 29.9 kWh
    [            Battery_Discharge_Today]: 18.2 kWh
    [               Battery_Charge_Total]: 4555.3 kWh
    >>>

