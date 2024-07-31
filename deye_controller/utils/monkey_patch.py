"""
PyslormanV5 monkey patching
"""
from typing import Union, Optional, List
from pysolarmanv5 import PySolarmanV5, PySolarmanV5Async
from umodbus.client.serial import rtu
from deye_controller.modbus.protocol import Register
from deye_controller.utils import RegistersGroup, map_response


def __patched_read_holding(self: PySolarmanV5, register: Union[Register, RegistersGroup, int],
                           quantity=1) -> Optional[List[int]]:

        """Read holding registers from modbus slave (Modbus function code 3)

        :param register: deye-controller Register/RegistersGroup or Modbus start address
        :type register:  Register, RegistersGroup or int
        :param quantity: Number of registers to query. Will be skipped if the register is not an integer
        :type quantity: int

        :return: List containing register values or modifies the register instances directly
        :rtype: list[int] | None
        """

        if isinstance(register, Register) or isinstance(register, RegistersGroup):
            quantity = register.len
            if isinstance(register, Register):
                start_address = register.address
            else:
                start_address = register.start_address

        else:
            quantity = quantity
            start_address = register

        mb_request_frame = rtu.read_holding_registers(
            self.mb_slave_id, start_address, quantity
        )
        modbus_values = self._get_modbus_response(mb_request_frame)
        if isinstance(register, RegistersGroup):
            map_response(modbus_values, register)
        elif isinstance(register, Register):
            register.value = modbus_values[0] if register.len == 1 else modbus_values
        else:
            return modbus_values


async def __patched_async_read_holding(self: PySolarmanV5Async, register: Union[Register, RegistersGroup, int],
                                     quantity=1) -> Optional[List[int]]:
    """Read holding registers from modbus slave (Modbus function code 3)

    :param register: deye-controller Register/RegistersGroup or Modbus start address
    :type register: Register, RegistersGroup or int
    :param quantity: Number of registers to query. Will be skipped if the register is not an integer
    :type quantity: int

    :return: List containing register values or modifies the register instances directly
    :rtype: list[int] | None

    """
    if isinstance(register, Register) or isinstance(register, RegistersGroup):
        quantity = register.len
        if isinstance(register, Register):
            start_address = register.address
        else:
            start_address = register.start_address

    else:
        quantity = quantity
        start_address = register

    mb_request_frame = rtu.read_holding_registers(
        self.mb_slave_id, start_address, quantity
    )
    modbus_values = await self._get_modbus_response(mb_request_frame)
    if isinstance(register, RegistersGroup):
        map_response(modbus_values, register)
    elif isinstance(register, Register):
        register.value = modbus_values[0] if register.len == 1 else modbus_values
    else:
        return modbus_values


def monkey_patch():
    PySolarmanV5.read_holding_registers = __patched_read_holding
    PySolarmanV5Async.read_holding_registers = __patched_async_read_holding
