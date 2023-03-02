from pysolarmanv5 import PySolarmanV5, V5FrameError
from .modbus.protocol import (HoldingRegisters, WriteableRegisters, Register, WritableRegister,
                            SellTimePoint, IntType, FloatType
                              )
from typing import Dict


class SellProg:

    """ Combined elements of an inverter program """

    def __init__(self, index: int, time: int, power: int, voltage: int, capacity: int):
        self.index = index
        self.time = SellTimePoint(148 + self.index, '')
        self.power = IntType(154 + self.index, '', suffix='W')
        self.voltage = FloatType(160 + self.index, '', 100, suffix='V')
        self.soc = IntType(166 + self.index, '', suffix='%')

        self.time.value = time
        self.power.value = power
        self.voltage.value = voltage
        self.soc.value = capacity

    def set_time(self, new_t: str):
        """ Set the start time for this program """
        writable = [WriteableRegisters.SellModeT1, WriteableRegisters.SellModeT2, WriteableRegisters.SellModeT3,
                    WriteableRegisters.SellModeT4, WriteableRegisters.SellModeT5, WriteableRegisters.SellModeT6]
        reg = [x for x in writable if self.time.address == x.address][0]
        reg.set(new_t)
        self.time.value = reg.modbus_value

    def set_power(self, watts: int):
        """ Set the MAX power for this program """
        writable = [WriteableRegisters.SellModeWatts1, WriteableRegisters.SellModeWatts2,
                    WriteableRegisters.SellModeWatts3, WriteableRegisters.SellModeWatts4,
                    WriteableRegisters.SellModeWatts5, WriteableRegisters.SellModeWatts6
                    ]
        reg = [x for x in writable if self.power.address == x.address][0]
        reg.set(watts)
        self.power.value = reg.modbus_value

    def set_soc(self, soc_pct: int):
        """ Set the SOC value for this program """
        writable = [WriteableRegisters.SellModeSOC1, WriteableRegisters.SellModeSOC2, WriteableRegisters.SellModeSOC3,
                    WriteableRegisters.SellModeSOC4, WriteableRegisters.SellModeSOC5, WriteableRegisters.SellModeSOC6]
        reg = [x for x in writable if self.soc.address == x.address][0]
        reg.set(soc_pct)
        self.soc.value = reg.modbus_value

    def __repr__(self):
        return f'<DEYE-Prog{self.index}> {self.time.format()} - P: {self.power.format()} / SOC: {self.soc.format()}'

    def __format__(self, format_spec):
        return f'''DEYE Program <{self.index}>    
            Start time:     {self.time.format()}
            MaxPower:       {self.power.format()} {self.power.suffix}
            SOC:            {self.soc.format()} {self.soc.suffix}
        ---
        '''


class SellProgrammer:
    """
    SellMode programmer

    Example:
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
        >>> prog.upload_settings()  # In order to upload the settigs to the inverter
    """

    def __init__(self, ip_address: str, serial: int):
        self.prog_start = 148  # Sell settings initial address (inclusive)
        self.prog_end = 172  # Last sell settings address (exclusive)
        self.reg_qty = self.prog_end - self.prog_start
        self.programs: Dict[int, SellProg] = {}
        self.ip_addr = ip_address
        self.logger = serial
        self.modbus = PySolarmanV5(self.ip_addr, self.logger, port=8899, mb_slave_id=1,
                                   verbose=False, socket_timeout=10)
        self.load_settings()

    def load_settings(self):
        """
        Loader of the current inverter settings

        :return:
        :rtype:
        """
        reg_values = self.modbus.read_holding_registers(self.prog_start, self.reg_qty)
        for i in range(6):
            self.programs[i] = SellProg(i, *reg_values[i::6])

    def upload_settings(self):
        """

        :return:
        :rtype:
        """
        """ Register sequence: time, power, voltage, capacity """
        values_t = []
        values_p = []
        values_v = []
        values_c = []
        for i in range(6):
            p = self.programs.get(i)
            values_t.append(p.time.value)
            values_p.append(p.power.value)
            values_v.append(p.voltage.value)
            values_c.append(p.soc.value)

        values = values_t + values_p + values_v + values_c
        ret_values = self.modbus.write_multiple_holding_registers(self.prog_start, values)
        """ It's possible to check the values returned after write """

    def update_program(self, index: int, start_t: str = None, soc: int = None, power: int = None):
        """
        SellTime program update

        :param index: Index of the program [0..5]
        :param start_t: Start time of the program
        :param soc: State of charge (in percents)
        :param power: Discharge rate per hour (in watts)
        :return:
        """
        program = self.programs.get(index)
        if program:
            if start_t:
                self._set_time_with_check(index, start_t)
            if soc:
                program.set_soc(soc)
            if power:
                program.set_power(power)

    def _set_time_with_check(self, index, t: str):
        next_idx = index + 1
        prev_idx = index - 1
        if index == 5:
            next_idx = 0
        if index == 0:
            prev_idx = 5

        p = self.programs.get(index)
        old_t = p.time.value
        p.set_time(t)

        if self.programs[prev_idx].time.value >= p.time.value and prev_idx != 5:
            print('Invalid time spec '
                  f'The time of the program must be '
                  f'greater than the previous one: {self.programs[prev_idx].time.format()}')
            p.time.value = old_t
        elif self.programs[next_idx].time.value <= p.time.value and next_idx != 0:
            print('Invalid time spec '
                  f'The time of the program must be '
                  f'lower than the next one: {self.programs[next_idx].time.format()}')
            p.time.value = old_t

        else:
            print('Program updated')

    def show_as_screen(self):
        """
        Terminal screen similar to the display of the inverter
        :return:
        :rtype:
        """
        header = '_' * 37
        header += '\n|  {:^12s} | {:^8s} | {:^5s}% |'.format('Time', 'Pwr', 'SOC')
        print(header)
        for i in range(6):
            p1 = self.programs.get(i)
            if i == 5:
                p2 = self.programs.get(0)
            else:
                p2 = self.programs.get(i+1)
            table = '| {:>5s} | {:>5s} | {:>8} | {:>5}% |'.format(p1.time.format(), p2.time.format(),
                                                                   p1.power.format(), p1.soc.format())
            print(table)
        print('-' * 37)
