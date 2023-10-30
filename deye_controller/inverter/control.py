from pysolarmanv5 import PySolarmanV5
from typing import Union, List
from deye_controller import HoldingRegisters, WritableRegisters, SellProgrammer
from deye_controller.utils import group_registers, map_response, RegistersGroup
import copy


class DeyeController:
    def __init__(self, address: str, serial: int):
        self.programmer = SellProgrammer(address, serial)
        self.modbus: PySolarmanV5 = self.programmer.modbus
        self._bms_regs = [
            copy.copy(getattr(HoldingRegisters, x))
            for x in HoldingRegisters.__dict__.keys()
            if "bms" in x.lower()
        ]
        self._grid_regs = [
            copy.copy(getattr(HoldingRegisters, x))
            for x in HoldingRegisters.__dict__.keys()
            if "grid" in x.lower()
        ]
        self._amps_regs = [
            copy.copy(getattr(HoldingRegisters, x))
            for x in HoldingRegisters.__dict__.keys()
            if "amp" in x.lower()
        ]
        self._power_regs = [
            copy.copy(getattr(HoldingRegisters, x))
            for x in HoldingRegisters.__dict__.keys()
            if "power" in x.lower()
        ]

        self._warnings = [
            copy.copy(getattr(HoldingRegisters, x))
            for x in HoldingRegisters.__dict__.keys()
            if "warning" in x.lower()
        ]

    def reload_programmer(self) -> None:
        """
        Reload the settings of the programmer from the inverter

        :return:
        """

        self.programmer.load_settings()

    def selected_sell_prog_days(self):
        reg = HoldingRegisters.SellTimeOfUse
        reg.value = self.modbus.read_holding_registers(reg.address, reg.len)[0]
        print(reg.format())

    def show_bms(self):
        """
        Shows BMS related settings

        :return:
        """

        groups = group_registers(self._bms_regs)
        for group in groups:
            res = self.modbus.read_holding_registers(group.start_address, group.len)
            map_response(res, group)
        self._display_group(groups, header="BMS Registers")

    def show_grid(self):
        """
        Displays grid related settings

        :return:
        """

        groups = group_registers(self._grid_regs)
        for group in groups:
            res = self.modbus.read_holding_registers(group.start_address, group.len)
            map_response(res, group)
        self._display_group(groups, header="Grid Registers")

    def show_amps(self):
        groups = group_registers(self._amps_regs)
        for group in groups:
            res = self.modbus.read_holding_registers(group.start_address, group.len)
            map_response(res, group)
        self._display_group(groups, header="AMP Registers")

    def set_amps(
        self, charge: Union[None, int] = None, discharge: Union[None, int] = None
    ):
        """
        Set battery charge / discharge amps

        !!! WARNING !!! Use only currents supported by your BMS

        :param charge:
        :param discharge:
        :return:
        """
        start = None
        vals = []
        if charge:
            ch = copy.copy(WritableRegisters.MaxChargeAmps)
            ch.set(charge)
            start = ch.address
            vals.append(ch.to_modbus)
        if discharge:
            disch = copy.copy(WritableRegisters.MaxDischargeAmps)
            disch.set(discharge)
            start = disch.address if start is None else start
            vals.append(disch.to_modbus)
        if start:
            self.modbus.write_multiple_holding_registers(start, vals)

    def show_power(self):
        groups = group_registers(self._grid_regs)
        for group in groups:
            res = self.modbus.read_holding_registers(group.start_address, group.len)
            map_response(res, group)
        self._display_group(groups, header="Power Related Registers")

    def current_flow(self) -> None:
        batt_flow = HoldingRegisters.BatteryOutPower
        grid_flow = [
            HoldingRegisters.GRIDPhaseAPower,
            HoldingRegisters.GRIDPhaseBPower,
            HoldingRegisters.GRIDPhaseCPower,
        ]
        load_flow = [
            HoldingRegisters.LoadPhaseAPower,
            HoldingRegisters.LoadPhaseBPower,
            HoldingRegisters.LoadPhaseCPower,
        ]

        pv_flow = [HoldingRegisters.PV1InPower, HoldingRegisters.PV2InPower]

        batt_flow.value = self.modbus.read_holding_registers(
            batt_flow.address, batt_flow.len
        )[0]
        grid = self.modbus.read_holding_registers(
            grid_flow[0].address, grid_flow[0].len * 3
        )
        load = self.modbus.read_holding_registers(
            load_flow[0].address, load_flow[0].len * 3
        )
        pv = self.modbus.read_holding_registers(pv_flow[0].address, pv_flow[0].len * 2)

        for i in range(3):
            grid_flow[i].value = grid[i]
            load_flow[i].value = load[i]
            if i < 2:
                pv_flow[i].value = pv[i]

        grid_tot = sum([x.format() for x in grid_flow])
        load_tot = sum([x.format() for x in load_flow])
        pv_tot = sum([x.format() for x in pv_flow])

        bp = "From" if batt_flow.format() >= 0 else "To"
        lp = "From" if load_tot >= 0 else "To"
        gp = "From" if load_tot >= 0 else "To"

        print(
            f" - {bp} BATT: {abs(batt_flow.format())}\n - {gp} GRID: {abs(grid_tot)}\n - {lp} LOAD: {load_tot}"
            f"\n - From PV: {pv_tot}"
        )

    def get_warnings(self) -> None:
        """
        Get the current inverter warnings
        """

        warn = self.modbus.read_holding_registers(
            self._warnings[0].address, self._warnings[0].len * 2
        )
        self._warnings[0].value = warn[0]
        self._warnings[1].value = warn[1]

        print(
            f"Warnings 1: {self._warnings[0].format()})\n"
            f"Warnings 2: {self._warnings[1].format()}\n"
        )

    def write_register(self, start_address: int, values: Union[int, List[int]]) -> None:
        """
        Write value to a register / group of registers

        :param start_address: Start address
        :param values: Register values
        :return:
        """
        if not isinstance(values, list):
            values = [values]
        self.modbus.write_multiple_holding_registers(start_address, values)

    def export_limit(self, max_power: int):
        """
        Limit the grid export of the inverter

        :param max_power: power in W/h
        :return:
        """

        reg = copy.copy(WritableRegisters.GridExportLimit)
        reg.set(max_power)
        self.modbus.write_multiple_holding_registers(reg.address, [reg.to_modbus])

    def _display_group(self, groups: List[RegistersGroup], header="Registers"):
        table = 80 * "=" + "\n"
        table += "|{:^78}|\n".format(header)
        table += 80 * "=" + "\n"

        for group in groups:
            for reg in group:
                table += "|{:>50} - {:^6} {:<4}\n".format(
                    reg.description.title(), str(reg.format()), reg.suffix
                )
        print(table)
