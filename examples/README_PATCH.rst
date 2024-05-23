* Monkey patching

Value(s) can be assigned directly to the register/group of registers after a call to monkey_patch()

.. code-block:: python

  >>> from deye_controller.utils.monkey_patch import monkey_patch
  >>> from deye_controller import HoldingRegisters
  >>> from pysolarmanv5 import PySolarmanV5
  >>> monkey_patch()
  >>> batt_soc = HoldingRegisters.BatterySOC
  >>> sol = PySolarmanV5('192.168.1.121', 2712345678, auto_reconnect=True, verbose=True)
  >>> sol.read_holding_registers(batt_soc)
  >>> batt_soc.format()
  80.0
..


* Reading a register group after patching

.. code-block:: python

  >>> from pysolarmanv5 import PySolarmanV5
  >>> from deye_controller import BatteryOnlyRegisters, TotalPowerOnly, HoldingRegisters
  >>> from deye_controller.utils import group_registers, map_response, monkey_patch

  >>> monkey_patch()
  >>> selection = ['BatteryChargeToday', 'BatteryDischargeToday', 'BatteryChargeTotal',
  'BMSChargedVoltage', 'BMSDischargedVoltage', 'BMSChargingCurrentLimit',
  'BMSDischargeCurrentLimit', 'BMSBatteryCapacity', 'BMSBatteryVoltage',
  'BMSBatteryCurrent']
  >>> regs = [getattr(HoldingRegisters, attr) for attr in selection]
  >>> len(regs)
  10
  >>> sol = PySolarmanV5('192.168.1.121', 2712345678, auto_reconnect=True)
  >>> groups = group_registers(regs)
  >>> len(groups)
  2
  >>> sol.read_holding_registers(groups[0])
  >>> for reg in groups[0]:
    print(reg.description.title(), reg.format())

  Bms_Charged_Voltage 56.0
  Bms_Discharged_Voltage 0.0
  Bms_Charge_Current_Limit 400
  Bms_Discharge_Current_Limit 400
  Bms_Battery_Soc 79
  Bms_Battery_Voltage 52.45
  Bms_Battery_Current -39
