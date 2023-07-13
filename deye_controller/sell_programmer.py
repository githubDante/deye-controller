from pysolarmanv5 import PySolarmanV5, V5FrameError
from .modbus.protocol import (HoldingRegisters, WritableRegisters, Register, WritableRegister,
                              SellTimePoint, IntType, FloatType, ChargeTimePoint
                              )
from .modbus.enums import ChargeGridGen
from typing import Dict


class SellProg:

    """ Combined elements of an inverter program """

    def __init__(self, index: int, time: int, power: int, voltage: int, capacity: int, grid_gen: int):
        """
        Holder for all elements of an inverter program

        :param index: Index of the program [0-6]
        :param time: Start time as string 'HH:MM'
        :param power: Max discharge power (charge seems unaffected by this)
        :param voltage: Min/Max battery voltage (if the control is by voltage)
        :param capacity: SOC percents
        :param grid_gen: Actual value of the Time Point X charge enable register (registers from 172 to 177)
        """

        self.index = index
        self.time = SellTimePoint(148 + self.index, '')
        self.power = IntType(154 + self.index, '', suffix='W')
        self.voltage = FloatType(160 + self.index, '', 100, suffix='V')
        self.soc = IntType(166 + self.index, '', suffix='%')
        self.grid_gen = ChargeTimePoint(172 + self.index, '')

        self.time.value = time
        self.power.value = power
        self.voltage.value = voltage
        self.soc.value = capacity
        self.grid_gen.value = grid_gen

    def set_time(self, new_t: str):
        """ Set the start time for this program """
        writable = [WritableRegisters.SellModeT1, WritableRegisters.SellModeT2, WritableRegisters.SellModeT3,
                    WritableRegisters.SellModeT4, WritableRegisters.SellModeT5, WritableRegisters.SellModeT6]
        reg = [x for x in writable if self.time.address == x.address][0]
        reg.set(new_t)
        self.time.value = reg.modbus_value

    def set_power(self, watts: int):
        """ Set the MAX power for this program """
        writable = [WritableRegisters.SellModeWatts1, WritableRegisters.SellModeWatts2,
                    WritableRegisters.SellModeWatts3, WritableRegisters.SellModeWatts4,
                    WritableRegisters.SellModeWatts5, WritableRegisters.SellModeWatts6
                    ]
        reg = [x for x in writable if self.power.address == x.address][0]
        reg.set(watts)
        self.power.value = reg.modbus_value

    def set_soc(self, soc_pct: int):
        """ Set the SOC value for this program """
        writable = [WritableRegisters.SellModeSOC1, WritableRegisters.SellModeSOC2, WritableRegisters.SellModeSOC3,
                    WritableRegisters.SellModeSOC4, WritableRegisters.SellModeSOC5, WritableRegisters.SellModeSOC6]
        reg = [x for x in writable if self.soc.address == x.address][0]
        reg.set(soc_pct)
        self.soc.value = reg.modbus_value

    def activate_grid_charge(self):
        """ Set the GRID charge flag """
        writable = [WritableRegisters.ChargeGridGen1, WritableRegisters.ChargeGridGen2,
                    WritableRegisters.ChargeGridGen3, WritableRegisters.ChargeGridGen4,
                    WritableRegisters.ChargeGridGen5, WritableRegisters.ChargeGridGen6]
        reg = [x for x in writable if self.grid_gen.address == x.address][0]

        if self.grid_gen.value == ChargeGridGen.GenEnabled:
            reg.set(ChargeGridGen.GridGenEnabled)
            self.grid_gen.value = reg.modbus_value
        elif self.grid_gen.value == ChargeGridGen.GridGenDisabled:
            reg.set(ChargeGridGen.GridEnabled)
            self.grid_gen.value = reg.modbus_value

    def deactivate_grid_charge(self):
        """ Unset the GRID charge flag """
        writable = [WritableRegisters.ChargeGridGen1, WritableRegisters.ChargeGridGen2,
                    WritableRegisters.ChargeGridGen3, WritableRegisters.ChargeGridGen4,
                    WritableRegisters.ChargeGridGen5, WritableRegisters.ChargeGridGen6]
        reg = [x for x in writable if self.grid_gen.address == x.address][0]
        if self.grid_gen.value == ChargeGridGen.GridEnabled:
            reg.set(ChargeGridGen.GridGenDisabled)
            self.grid_gen.value = reg.modbus_value
        elif self.grid_gen.value == ChargeGridGen.GridGenEnabled:
            reg.set(ChargeGridGen.GenEnabled)
            self.grid_gen.value = reg.modbus_value

    def activate_generator_charge(self):
        """ Set the GEN charge flag """
        writable = [WritableRegisters.ChargeGridGen1, WritableRegisters.ChargeGridGen2,
                    WritableRegisters.ChargeGridGen3, WritableRegisters.ChargeGridGen4,
                    WritableRegisters.ChargeGridGen5, WritableRegisters.ChargeGridGen6]
        reg = [x for x in writable if self.grid_gen.address == x.address][0]

        if self.grid_gen.value == ChargeGridGen.GridEnabled:
            reg.set(ChargeGridGen.GridGenEnabled)
            self.grid_gen.value = reg.modbus_value
        elif self.grid_gen.value == ChargeGridGen.GridGenDisabled:
            reg.set(ChargeGridGen.GenEnabled)
            self.grid_gen.value = reg.modbus_value

    def deactivate_generator_charge(self):
        """ Unset the GEN charge flag """
        writable = [WritableRegisters.ChargeGridGen1, WritableRegisters.ChargeGridGen2,
                    WritableRegisters.ChargeGridGen3, WritableRegisters.ChargeGridGen4,
                    WritableRegisters.ChargeGridGen5, WritableRegisters.ChargeGridGen6]
        reg = [x for x in writable if self.grid_gen.address == x.address][0]

        if self.grid_gen.value == ChargeGridGen.GenEnabled:
            reg.set(ChargeGridGen.GridGenDisabled)
            self.grid_gen.value = reg.modbus_value
        if self.grid_gen.value == ChargeGridGen.GridGenEnabled:
            reg.set(ChargeGridGen.GridEnabled)
            self.grid_gen.value = reg.modbus_value

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
    """

    def __init__(self, ip_address: str, serial: int):
        self.prog_start = 148  # Sell settings initial address (inclusive)
        self.prog_end = 178  # Last sell settings address (exclusive)
        self.reg_qty = self.prog_end - self.prog_start
        self.programs: Dict[int, SellProg] = {}
        self.ip_addr = ip_address
        self.logger = serial
        self.modbus = PySolarmanV5(self.ip_addr, self.logger, port=8899, mb_slave_id=1,
                                   verbose=False, socket_timeout=10)

        self.load_settings()

    def disconnect(self):
        try:
            self.modbus.disconnect()
        except:
            pass

    def load_settings(self):
        """
        Loader of the current inverter settings

        :return:
        :rtype:
        """
        reg_values = self.modbus.read_holding_registers(self.prog_start, self.reg_qty)
        for i in range(6):
            self.programs[i] = SellProg(i, *reg_values[i::6])

    def upload_settings(self) -> None:
        """
        Upload the settings back to the inverter
        """
        """ Register sequence: time, power, voltage, capacity """
        values_t = []
        values_p = []
        values_v = []
        values_c = []
        values_g = []

        for i in range(6):
            p = self.programs.get(i)
            values_t.append(p.time.value)  # Start time
            values_p.append(p.power.value)  # Power control
            values_v.append(p.voltage.value)  # Voltage control
            values_c.append(p.soc.value)  # Capacity
            values_g.append(p.grid_gen.value)  # Grid / Gen

        values = values_t + values_p + values_v + values_c + values_g
        ret_values = self.modbus.write_multiple_holding_registers(self.prog_start, values)
        """ It's possible to check the values returned after write """

    def update_program(self, index: int, start_t: str = None, soc: int = None, power: int = None,
                       grid_ch: bool = None, gen_ch: bool = None):
        """
        SellTime program update

        :param index: Index of the program [0..5]
        :param start_t: Start time of the program
        :param soc: State of charge (in percents)
        :param power: Discharge rate per hour (in watts)
        :param grid_ch: Set to True / False in order top change the Grid checkbox of the respective program
        :param gen_ch: Set to True / False in order top change the Gen checkbox of the respective program
        :return:
        """
        program = self.programs.get(index)
        if program:
            if start_t:
                program.set_time(start_t)
            if soc:
                program.set_soc(soc)
            if power:
                program.set_power(power)

            if grid_ch and grid_ch is True:
                program.activate_grid_charge()
            elif grid_ch is False:
                program.deactivate_grid_charge()

            if gen_ch and gen_ch is True:
                program.activate_generator_charge()
            elif gen_ch is False:
                program.deactivate_generator_charge()

    def show_as_screen(self):
        """
        Terminal screen similar to the display of the inverter
        :return:
        :rtype:
        """
        header = '_' * 52
        header += '\n| {:^5} | {:^5} |  {:^12s} | {:^8s} | {:^5s}% |'.format('Grid', 'Gen', 'Time', 'Pwr', 'SOC')
        print(header)
        for i in range(6):
            p1 = self.programs.get(i)
            if i == 5:
                p2 = self.programs.get(0)
            else:
                p2 = self.programs.get(i+1)
            f_grid = '✓' if p1.grid_gen.value in [ChargeGridGen.GridEnabled, ChargeGridGen.GridGenEnabled] else ''
            f_gen = '✓' if p1.grid_gen.value in [ChargeGridGen.GenEnabled, ChargeGridGen.GridGenEnabled] else ''
            """ Grid / Gen selection  """

            table = '| {:^5s} | {:^5s} | {:>5s} | {:>5s} | {:>8} | {:>5}% |'.format( f_grid, f_gen,
                                                                   p1.time.format(), p2.time.format(),
                                                                   p1.power.format(), p1.soc.format())
            print(table)
        print('-' * 52)
