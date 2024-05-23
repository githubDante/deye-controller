from typing import Union, List
from deye_controller.modbus.protocol import Register


class RegistersGroup:

    def __init__(self, reg: Union[Register]):
        self.start_address = reg.address
        self.len = reg.len
        self._regs = [reg]

    @property
    def next_address(self) -> int:
        return self._regs[-1].address + self._regs[-1].len

    def add(self, register: Register):
        self._regs.append(register)
        self.len += register.len

    def __iter__(self):
        yield from self._regs


def map_response(response: List[int], group: RegistersGroup) -> None:
    """
    Map the values in the response to register values for the registers  in the group.

    This method consumes the response (or part of it).

    :param response: list of ints as received from the inverter
    :param group: A RegistersGroup
    :return:
    """

    for reg in group:
        if reg.len == 1:
            reg.value = response[0]
            response.pop(0)
        else:
            reg.value = response[:reg.len]
            [response.pop(0) for x in range(reg.len)]


def group_registers(regs: List[Register]) -> List[RegistersGroup]:
    """
    Group a list of random registers for faster reading from the inverter

    :param regs:
    :return:
    """
    s_regs = sorted(regs, key=lambda x: x.address)
    top = RegistersGroup(s_regs[0])
    groups = [top]
    for i in range(1, len(s_regs)):
        if s_regs[i].address == top.next_address:
            top.add(s_regs[i])
        else:
            top = RegistersGroup(s_regs[i])
            groups.append(top)

    return groups
