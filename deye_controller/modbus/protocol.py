"""
MODBUS Registers for DEYE 12K Inverters
"""
from abc import abstractmethod
from textwrap import wrap
import enum
import struct
from typing import List, Union
from .utils import to_bytes, to_unsigned_bytes, to_signed, signed_to_int, to_inv_time
import datetime
from .enums import *


class InverterType(int, enum.Enum):

    Inverter = 2
    Hybrid = 3
    Microinverter = 4
    Hybrid3Phase = 5
    Unknown = 0

    @classmethod
    def _missing_(cls, value):
        return InverterType.Unknown


class Register(object):

    """ Base register of 2 bytes """
    def __init__(self, address, length, description=''):
        self.address = address
        self.len = length
        self.description = description
        self.value = None
        self.suffix = ''

    @abstractmethod
    def format(self):
        pass

    def format_custom(self, scaling: float, prefix: str = '') -> float:
        """
        Custom format

        :param scaling: Scaling applied to the register value
        :param prefix: Extra prefix (will be added to the suffix permanently on first use)
        :return:
        """
        self.suffix = prefix + self.suffix

        return round(self.format() / scaling, 3)


class IntType(Register):

    def __init__(self, address, name, suffix='', signed=False):
        super(IntType, self).__init__(address, 1, name)
        self.suffix = suffix
        self.signed = signed

    def format(self) -> int:
        if self.signed:
            return to_signed(self.value)
        else:
            return self.value


class FloatType(Register):

    def __init__(self, address, name, scale, suffix='', signed=False):
        super(FloatType, self).__init__(address, 1, name)
        self.scale = scale
        self.suffix = suffix
        self.signed = signed

    def format(self) -> float:
        if self.signed:
            return round(to_signed(self.value) / self.scale, 2)
        else:
            return round(self.value / self.scale, 2)


class BoolType(Register):

    def __init__(self, address, name):
        super(BoolType, self).__init__(address, 1, name)

    def format(self) -> str:
        return 'Active' if self.value == 1 else 'Inactive'


class LongType(Register):
    def __init__(self, address, name, scale, suffix=''):
        super(LongType, self).__init__(address, 2, name)
        self.scale = scale
        self.suffix = suffix

    def format(self):
        v = to_bytes(self.value[::-1])
        calculated = int.from_bytes(v, byteorder='big')
        if self.scale == 1:
            return calculated
        else:
            return round(calculated / self.scale, 2)


class LongUnsignedType(Register):

    """
    All marked as Wh_low / Wh_high word
    """
    def __init__(self, address, name, scale, suffix=''):
        super(LongUnsignedType, self).__init__(address, 2, name)
        self.scale = scale
        self.suffix = suffix

    def format(self):
        v = to_unsigned_bytes(self.value[::-1])
        calculated = int.from_bytes(v, byteorder='big')
        if self.scale == 1:
            return calculated
        else:
            return round(calculated / self.scale, 2)


class DeviceType(Register):

    def __init__(self):
        super(DeviceType, self).__init__(0, 1, 'device_type')

    def format(self) -> str:
        return InverterType(self.value).name


class DeviceSerialNumber(Register):
    
    def __init__(self):
        super(DeviceSerialNumber, self).__init__(3, 5, 'inverter_serial')
        self.value = [0, 0, 0, 0, 0]

    def format(self) -> str:
        as_seq = [struct.pack('>h', x).decode() for x in self.value]
        return ''.join(as_seq)


class DeviceTime(Register):
    
    def __init__(self):
        super(DeviceTime, self).__init__(62, 3, 'inverter_time')
        self.value = [0, 0, 0]

    def format(self):
        as_bytes = to_bytes(self.value)
        try:
            return datetime.datetime(2000 + as_bytes[0], as_bytes[1], as_bytes[2], as_bytes[3],
                                     as_bytes[4], as_bytes[5])
        except:
            return datetime.datetime(1970, 1, 1, 0, 0)


class SellTimePoint(Register):
    """ Sell Time point - as defined for register 148.
        Note: These registers are chained:
            - interval 1 -> 148 - 149
            - interval 2 -> 149 - 150
            - interval 3 -> 150 - 151
            - interval 4 -> 152 - 153
            - interval 5 -> 153 - 148

        The values in the registers below these are for the intervals defined here
    """

    def __init__(self, address, name):
        super(SellTimePoint, self).__init__(address, 1, name)

    def format(self):
        v = self.value / 100
        h = str(int(v // 1)).zfill(2)
        m = str(int((v % 1) * 100)).zfill(2)
        return f'{h}:{m}'


class ChargeTimePoint(Register):
    """ GEN / GRID charge as defined for register 172 """
    def __init__(self, address, name):
        super(ChargeTimePoint, self).__init__(address, 1, name)

    def format(self):
        """
        Bit 0 - Grid charge enabled / disabled
        Bit 1 - Generator charge enabled / disabled
        :return:
        :rtype:
        """
        #return '{:02b}'.format(self.value)
        return ChargeGridGen(self.value)


class TimeOfUseSell(Register):
    def __init__(self):
        super(TimeOfUseSell, self).__init__(146, 1, 'sell_time_of_use')

    def format(self) -> List[str]:
        return [f'TimeOfUse - {x}' for x in TimeOfUse.from_int(self.value)]


class GridFrequency(Register):
    """
    Grid frequency. Can be 50 or 60 Hz
    """
    def __init__(self):
        super(GridFrequency, self).__init__(183, 1, 'grid_freq_selection')
        self.suffix = 'Hz'

    def format(self) -> int:
        """  """
        return 50 if self.value == 0 else 60


class RunState(Register):

    def __init__(self):
        super(RunState, self).__init__(500, 1, 'inverter_state')

    def format(self):
        return InverterState(self.value)


class InverterControlMode(Register):

    def __init__(self):
        super(InverterControlMode, self).__init__(98, 1, 'control_mode')

    def format(self):
        return ControlMode(self.value)


class BatteryControl(Register):
    
    def __init__(self):
        super(BatteryControl, self).__init__(111, 1, 'battery_control_mode')

    def format(self):
        return BatteryControlMode(self.value)
    
    
class BMSBatteryTemp(Register):
    
    def __init__(self):
        super(BMSBatteryTemp, self).__init__(217, 1, 'bms_battery_temp')
        self.suffix = '°C'
    def format(self):
        return round((self.value - 1000) / 10, 2)


class BMSLiProto(Register):
    """ Selected protcol when the control mode is set to Lithium """
    def __init__(self):
        super(BMSLiProto, self).__init__(223, 1, 'bms_type')

    def format(self):
        return BMSMode(self.value)


class MicroinverterExportCutoff(Register):

    def __init__(self):
        super(MicroinverterExportCutoff, self).__init__(178, 1, 'export_to_grid_cutoff')

    def format(self):
        bits = wrap('{:016b}'.format(self.value), 2)
        enabled = TwoBitState(int(bits[-1], base=2))
        gen_peak_shaving = TwoBitState(int(bits[-2], base=2))
        grid_peak_shaving = TwoBitState(int(bits[-3], base=2))
        on_grid_always_on = TwoBitState(int(bits[-4], base=2))
        external_relay = TwoBitState(int(bits[-5], base=2))
        report_loss_of_lithium = TwoBitState(int(bits[-6], base=2))
        return {'enabled': enabled,
                'generator_peak_shaving': gen_peak_shaving,
                'grid_peak_shaving': grid_peak_shaving,
                'on_grid_always_on': on_grid_always_on,
                'external_relay': external_relay,
                'report_loss_of_lithium': report_loss_of_lithium
                }


class TempWithOffset(FloatType):

    def __init__(self, address, name, scale=10, offset=1000):
        super().__init__(address, name, scale, suffix='°C')
        self.offset = offset

    def format(self) -> float:
        return round(super().format() - self.offset / self.scale, 2)


class ACRelayStatus(Register):
    
    def __init__(self):
        super().__init__(552, 1, 'ac_relays')

    def format(self):
        as_bits = [int(x) for x in f'{self.value:016b}'[::-1]]
        inverter_relay = BitOnOff(as_bits[0])
        grid_relay = BitOnOff(as_bits[2])
        gen_relay = BitOnOff(as_bits[3])
        grid_power_relay = BitOnOff(as_bits[4])  # No idea what is this - grid give power to relay
        dry_contact_1 = BitOnOff(as_bits[7])
        dry_contact_2 = BitOnOff(as_bits[8])

        return {
            'Inverter':  inverter_relay,
            'Grid': grid_relay,
            'Generator': gen_relay,
            'GridPower': grid_power_relay,
            'DryContact-1': dry_contact_1,
            'DryContact-2': dry_contact_2,
        }


class WarningOne(Register):
    def __init__(self):
        super().__init__(553, 1, 'warn_1')

    def format(self):
        as_bits = [int(x) for x in f'{self.value:016b}'[::-1]]
        fan_warn = BitOnOff(as_bits[1])
        wrong_phase = BitOnOff(as_bits[2])

        return {
            'Fan-Warning': fan_warn,
            'Wrong-Phase': wrong_phase
        }


class WarningTwo(Register):
    def __init__(self):
        super().__init__(554, 1, 'warn_2')

    def format(self):
        as_bits = [int(x) for x in f'{self.value:016b}'[::-1]]
        bms_comm = BitOnOff(as_bits[14])
        parallel_com = BitOnOff(as_bits[15])

        return {
            'BMS-COMM-Lost': bms_comm,
            'Parallel-COMM-Lost': parallel_com
        }


class GenPortUse(Register):

    def __init__(self):
        super().__init__(133, 1, 'gen_port_use')

    def format(self):
        return str(GenPortMode(self.value))


class InverterWorkMode(Register):
    def __init__(self):
        super().__init__(142, 1, 'work_mode')

    def format(self):
        return str(WorkMode(self.value))


class HoldingRegisters:

    DeviceType = DeviceType()
    CommProtocol = IntType(1, 'modbus_address')
    SerialNumber = DeviceSerialNumber()
    RatedPower = IntType(8, 'rated_power')
    """ START OF WRITABLE Registers """
    DeviceTime = DeviceTime()  # RW 62
    """ Not defined here """
    CommAddress = IntType(74, 'comm_address')
    SwitchOnOff = BoolType(80, 'switch_on_off')
    ''' Switch On / Off the inverter '''
    ControlMode = InverterControlMode()
    BattEqualization = FloatType(99, 'batt_equalization_v', 100, suffix='V')
    BattAbsorbtion = FloatType(100, 'batt_absorbtion_v', 100, suffix='V')
    BattFloat = FloatType(101, 'batt_float_v', 100, suffix='V')
    BattCapacity = IntType(102, 'batt_capacity', suffix='Ah')
    BattEmptyVoltage = FloatType(103, 'batt_empty_v', 100, suffix='V')
    ZeroExportPower = IntType(104, 'zero_export_power', suffix='W')
    TEMPCO = IntType(107, 'TEMPCO', suffix='mV/*C')
    MaxAmpCharge = IntType(108, 'max_charge_amps', suffix='A')
    MaxAmpDischarge = IntType(109, 'max_discharge_amps', suffix='A')
    BatteryControl = BatteryControl()
    BattWakeUp = BoolType(112, 'battery_wake_up')
    BattResistance = IntType(113, 'battery_resistance', suffix='mOhm')
    BattChargingEff = FloatType(114, 'battery_charging_eff', 10, suffix='%')
    BattShutDownCapacity = IntType(115, 'battery_shutdown_capacity', suffix='%')
    BattRestartCapacity = IntType(116, 'battery_recovery_capacity', suffix='%')
    BattLowCapacity = IntType(117, 'battery_low_capacity', suffix='%')
    BattShutDownVoltage = FloatType(118, 'battery_shutdown_voltage', 100, suffix='V')
    BattRestartVoltage = FloatType(119, 'battery_restart_voltage', 100, suffix='V')
    BattLowVoltage = FloatType(120, 'battery_low_voltage', 100, suffix='V')

    """ Generator settings """
    GeneratorWorkingTime = FloatType(121, 'gen_max_working_time', 10, suffix='h')
    GeneratorCoolingTime = FloatType(122, 'gen_cooling_time', 10, suffix='h')
    GeneratorStartVoltage = FloatType(123, 'gen_charge_start_voltage', 100, suffix='V')
    GeneratorStartCapacity = FloatType(124, 'gen_charge_start_soc', 100, suffix='%')
    GeneratorChargeCurrent = IntType(125, 'gen_charge_current', suffix='A')

    """ Generator settings up to register 125 """
    GridChargeStartVolts = FloatType(126, 'grid_charge_start_voltage', 100, suffix='V')
    GridChargeStartCapacity = IntType(127, 'grid_charge_start_soc', suffix='%')
    GridChargeCurrent = IntType(128, 'grid_charge_current', suffix='A')

    """ Smart Load control - need more info  """
    GeneratorPortSetup = GenPortUse()
    """ Smart Load """
    IverterWorkMode = InverterWorkMode()
    GridExportLimit = IntType(143, 'grid_max_output_pwr', suffix='W')
    SolarSell = BoolType(145, 'solar_sell')
    SellTimeOfUse = TimeOfUseSell()
    SellTimePoint1 = SellTimePoint(148, 'sell_point_t1')
    SellTimePoint2 = SellTimePoint(149, 'sell_point_t2')
    SellTimePoint3 = SellTimePoint(150, 'sell_point_t3')
    SellTimePoint4 = SellTimePoint(151, 'sell_point_t4')
    SellTimePoint5 = SellTimePoint(152, 'sell_point_t5')
    SellTimePoint6 = SellTimePoint(153, 'sell_point_t6')

    SellModeKWPoint1 = IntType(154, 'sell_point_t1_watts', suffix='W')
    SellModeKWPoint2 = IntType(155, 'sell_point_t2_watts', suffix='W')
    SellModeKWPoint3 = IntType(156, 'sell_point_t3_watts', suffix='W')
    SellModeKWPoint4 = IntType(157, 'sell_point_t4_watts', suffix='W')
    SellModeKWPoint5 = IntType(158, 'sell_point_t5_watts', suffix='W')
    SellModeKWPoint6 = IntType(159, 'sell_point_t6_watts', suffix='W')

    SellModeBattVolt1 = FloatType(160, 'sell_point_t1_volts', 100, suffix='V')
    SellModeBattVolt2 = FloatType(161, 'sell_point_t2_volts', 100, suffix='V')
    SellModeBattVolt3 = FloatType(162, 'sell_point_t3_volts', 100, suffix='V')
    SellModeBattVolt4 = FloatType(163, 'sell_point_t4_volts', 100, suffix='V')
    SellModeBattVolt5 = FloatType(164, 'sell_point_t5_volts', 100, suffix='V')
    SellModeBattVolt6 = FloatType(165, 'sell_point_t6_volts', 100, suffix='V')

    SellModeBattCapacity1 = IntType(166, 'sell_point_t1_soc', suffix='%')
    SellModeBattCapacity2 = IntType(167, 'sell_point_t2_soc', suffix='%')
    SellModeBattCapacity3 = IntType(168, 'sell_point_t3_soc', suffix='%')
    SellModeBattCapacity4 = IntType(169, 'sell_point_t4_soc', suffix='%')
    SellModeBattCapacity5 = IntType(170, 'sell_point_t5_soc', suffix='%')
    SellModeBattCapacity6 = IntType(171, 'sell_point_t6_soc', suffix='%')

    ChargeModePoint1 = ChargeTimePoint(172, 'charge_point_t1')
    ChargeModePoint2 = ChargeTimePoint(173, 'charge_point_t2')
    ChargeModePoint3 = ChargeTimePoint(174, 'charge_point_t3')
    ChargeModePoint4 = ChargeTimePoint(175, 'charge_point_t4')
    ChargeModePoint5 = ChargeTimePoint(176, 'charge_point_t5')
    ChargeModePoint6 = ChargeTimePoint(177, 'charge_point_t6')

    """ Skipped some registers. Needs research """
    InverterGridExportCutoff = MicroinverterExportCutoff()

    GridFrequency = GridFrequency()
    GridHighVoltage = FloatType(185, 'grid_high_voltage', 10, suffix='V')
    GridLowVoltage = FloatType(186, 'grid_low_voltage', 10, suffix='V')
    GridHighFreq = FloatType(187, 'grid_high_frequency', 100, suffix='Hz')
    GridLowFreq = FloatType(188, 'grid_low_frequency', 100, suffix='Hz')
    GeneratorConnected = BoolType(189, 'generator_to_grid')

    GeneratorPeakShavingPower = IntType(190, 'gen_peak_shaving_pwr', suffix='W')
    GridPeakShavingPower = IntType(191, 'grid_peak_shaving_pwr', suffix='W')
    SmartLoadOpenDelay = IntType(192, 'smart_load_open_delay', suffix='Minutes')

    OutputPF = FloatType(193, 'output_power_factor', 10, suffix='%')

    """ BMS settings """
    BMSChargedVoltage = FloatType(210, 'bms_charged_voltage', 100, suffix='V')
    BMSDischargedVoltage = FloatType(211, 'bms_discharged_voltage', 100, suffix='V')
    BMSChargingCurrentLimit = IntType(212, 'bms_charge_current_limit', suffix='A')
    BMSDischargeCurrentLimit = IntType(213, 'bms_discharge_current_limit', suffix='A')
    BMSBatteryCapacity = IntType(214, 'bms_battery_SOC', suffix='%')
    BMSBatteryVoltage = FloatType(215, 'bms_battery_voltage', 100, suffix='V')
    BMSBatteryCurrent = IntType(216, 'bms_battery_current', signed=True, suffix='A')
    BMSBatteryTemp = BMSBatteryTemp()
    BMSMaxChargingCurrent = IntType(218, 'bms_max_charge_current', suffix='A')
    BMSMaxDischargeCurrent = IntType(219, 'bms_max_discharge_current', suffix='A')
    BMSBatteryAlarm = BoolType(220, 'bms_battery_alarm')
    BMSBatteryFaultLocation = IntType(221, 'bms_battery_fault_location')
    BMSBatterySymbol = IntType(222, 'bms_battery_symbol_2')
    BMSType = BMSLiProto()  # 0 - PYLON / SOLAX ... needs enumeration
    BMSBatterySOH = IntType(224, 'bms_battery_soh', signed=True)  # Seems as it's not reported should be -1 all the time

    """ Other """
    MaxSolarSellPower = IntType(340, 'max_solar_sell_pwr', suffix='W')


    """ END OF WRITABLE  
        The rest till 500 are for California regulations  
    """
    RunState = RunState()
    PowerToday = FloatType(501, 'active_power_today', 10, suffix='kWh')
    ReactivePowerToday = FloatType(502, 'reactive_power_today', 10, suffix='kVarh')
    GridConnectedToday = FloatType(503, 'grid_connection_today', 60, suffix='minutes')

    BatteryChargeToday = FloatType(514, 'battery_charge_today', 10, suffix='kWh')
    BatteryDischargeToday = FloatType(515, 'battery_discharge_today', 10, suffix='kWh')
    BatteryChargeTotal = LongUnsignedType(516, 'battery_charge_total', 10, suffix='kWh')
    BatteryDischargeTotal = LongUnsignedType(518, 'battery_discharge_total', 10, suffix='kWh')

    TodayBuyGrid = FloatType(520, 'today_bought_from_grid', 10, suffix='kWh')
    TodaySoldGrid = FloatType(521, 'today_sold_to_grid', 10, suffix='kWh')
    TotalBuyGrid = LongUnsignedType(522, 'total_bought_from_grid', 10, suffix='kWh')
    TotalSellGrid = LongUnsignedType(524, 'total_sold_to_grid', 10, suffix='kWh')
    TodayToLoad = FloatType(526, 'today_to_load', 10, suffix='kWh')
    TotalToLoad = LongUnsignedType(527, 'total_to_load', 10, suffix='kWh')
    TodayFromPV = FloatType(529, 'today_from_pv', 10, suffix='kWh')
    TodayFromPVString1 = FloatType(530, 'today_from_pv_s1', 10, suffix='kWh')
    TodayFromPVString2 = FloatType(531, 'today_from_pv_s2', 10, suffix='kWh')
    TodayFromPVString3 = FloatType(532, 'today_from_pv_s3', 10, suffix='kWh')
    TodayFromPVString4 = FloatType(533, 'today_from_pv_s4', 10, suffix='kWh')
    TotalFromPV = LongUnsignedType(534, 'total_from_pv', 10, suffix='kWh')
    TodayFromGenerator = FloatType(536, 'today_from_generator', 10, suffix='kWh')
    TotalFromGenerator = LongUnsignedType(537, 'total_from_generator', 10, suffix='kWh')
    TodayGeneratorWorkTime = FloatType(539, 'generator_worktime_today', 10, suffix='hours')

    DCTransformerTemp = TempWithOffset(540, 'dc_transformer_temp')
    HeatsinkTemp = TempWithOffset(541, 'heatsink_temp')

    LoadAnnualConsumption = LongUnsignedType(545, 'load_annual_consumption', 10, suffix='kWh')

    ACRelays = ACRelayStatus()
    """ WARNINGS """
    Warning_1 = WarningOne()
    Warning_2 = WarningTwo()
    BatteryTemp = FloatType(586, 'battery_temperature', 100, suffix='°C')
    BatteryVoltage = FloatType(587, 'battery_voltage', 100, suffix='V')
    BatterySOC = FloatType(588, 'battery_soc', 1, suffix='%')
    BatteryOutPower = IntType(590, 'battery_out_power', suffix='W', signed=True)
    BatteryOutCurrent = FloatType(591, 'battery_out_current', 100, suffix='A', signed=True)
    BatteryCorrectedAH = IntType(592, 'battery_corrected_ah', 'Ah')

    """ GRID """
    GRIDPhaseAVolt = FloatType(598, 'grid_phase_A_volt', 10, suffix='V')
    GRIDPhaseBVolt = FloatType(599, 'grid_phase_B_volt', 10, suffix='V')
    GRIDPhaseCVolt = FloatType(600, 'grid_phase_C_volt', 10, suffix='V')
    GRIDPhaseABVolt = FloatType(601, 'grid_phase_AB_volt', 10, suffix='V')
    GRIDPhaseBCVolt = FloatType(602, 'grid_phase_BC_volt', 10, suffix='V')
    GRIDPhaseCAVolt = FloatType(603, 'grid_phase_CA_volt', 10, suffix='V')

    GRIDPhaseAPowerIn = IntType(604, 'grid_phase_A_in_power', suffix='W', signed=True)
    GRIDPhaseBPowerIn = IntType(605, 'grid_phase_B_in_power', suffix='W', signed=True)
    GRIDPhaseCPowerIn = IntType(606, 'grid_phase_C_in_power', suffix='W', signed=True)
    GRIDActivePowerIn = IntType(607, 'grid_active_side_side_in_power', suffix='W', signed=True)
    GRIDActiveApparentPower = IntType(608, 'grid_active_side_side_apparent_power', suffix='W', signed=True)

    """ The total consumption of the inverter from the grid is the sum of the above 3 values """
    GRIDFrequency = FloatType(609, 'grid_in_frequency', 100, suffix='Hz')
    GRIDPhaseACurrentIn = FloatType(610, 'grid_phase_A_in_current', 100, suffix='A', signed=True)
    GRIDPhaseBCurrentIn = FloatType(611, 'grid_phase_B_in_current', 100, suffix='A', signed=True)
    GRIDPhaseCCurrentIn = FloatType(612, 'grid_phase_C_in_current', 100, suffix='A', signed=True)
    """ OUT OF GRID Parameters """
    GRIDPhaseACurrentOutG = FloatType(613, 'grid_phase_A_out_of_grid_current', 100, suffix='A', signed=True)
    GRIDPhaseBCurrentOutG = FloatType(614, 'grid_phase_B_out_of_grid_current', 100, suffix='A', signed=True)
    GRIDPhaseCCurrentOutG = FloatType(615, 'grid_phase_C_out_of_grid_current', 100, suffix='A', signed=True)
    GRIDPhaseAPowerOutG = IntType(616, 'grid_phase_A_out_of_grid_power', suffix='W', signed=True)
    GRIDPhaseBPowerOutG = IntType(617, 'grid_phase_B_out_of_grid_power', suffix='W', signed=True)
    GRIDPhaseCPowerOutG = IntType(618, 'grid_phase_C_out_of_grid_power', suffix='W', signed=True)
    GRIDTotalPowerOutG = IntType(619, 'grid_total_out_of_grid_power', suffix='W', signed=True)
    GRIDTotalAppPowerOutG = IntType(620, 'grid_total_out_of_grid_apparent_power', suffix='W', signed=True)
    """ END OF OUT OF GRID Parameters """
    """ OUTPUT Parameters """
    GRIDPhaseAPower = IntType(622, 'grid_phase_A__power', suffix='W', signed=True)
    GRIDPhaseBPower = IntType(623, 'grid_phase_B__power', suffix='W', signed=True)
    GRIDPhaseCPower = IntType(624, 'grid_phase_C__power', suffix='W', signed=True)
    GRIDTotalPower = IntType(625, 'grid_total_power', suffix='W', signed=True)
    GRIDPhaseAVoltOut = FloatType(627, 'grid_phase_A_volt_out', 10, suffix='V')
    GRIDPhaseBVoltOut = FloatType(628, 'grid_phase_B_volt_out', 10, suffix='V')
    GRIDPhaseCVoltOut = FloatType(629, 'grid_phase_C_volt_out', 10, suffix='V')

    InverterPhaseACurrentOut = FloatType(630, 'inverter_phase_A_out_current', 100, suffix='A', signed=True)
    InverterPhaseBCurrentOut = FloatType(631, 'inverter_phase_B_out_current', 100, suffix='A', signed=True)
    InverterPhaseCCurrentOut = FloatType(632, 'inverter_phase_C_out_current', 100, suffix='A', signed=True)
    InverterPhaseAPowerOut = IntType(633, 'inverter_phase_A_out_power', suffix='W', signed=True)
    InverterPhaseBPowerOut = IntType(634, 'inverter_phase_B_out_power', suffix='W', signed=True)
    InverterPhaseCPowerOut = IntType(635, 'inverter_phase_C_out_power', suffix='W', signed=True)
    InverterTotalPowerOut = IntType(636, 'inverter_total_out_power', suffix='W', signed=True)
    InverterTotalApparentPowerOut = IntType(637, 'inverter_total_apparent_out_power', suffix='W', signed=True)
    InverterFrequency = FloatType(638, 'inverter_out_frequency', 100, suffix='Hz')

    """ Load """
    UPSPhaseAPower = IntType(640, 'ups_phase_A_power', suffix='W')
    UPSPhaseBPower = IntType(641, 'ups_phase_B_power', suffix='W')
    UPSPhaseCPower = IntType(642, 'ups_phase_C_power', suffix='W')
    UPSTotalPower = IntType(643, 'ups_total_power', suffix='W')
    LoadPhaseAVolt = FloatType(644, 'load_phase_A_volt', 10, suffix='V')
    LoadPhaseBVolt = FloatType(645, 'load_phase_B_volt', 10, suffix='V')
    LoadPhaseCVolt = FloatType(646, 'load_phase_C_volt', 10, suffix='V')
    LoadPhaseACurrent = FloatType(647, 'load_phase_A_current', 100, suffix='A', signed=True)
    LoadPhaseBCurrent = FloatType(648, 'load_phase_B_current', 100, suffix='A', signed=True)
    LoadPhaseCCurrent = FloatType(649, 'load_phase_C_current', 100, suffix='A', signed=True)

    LoadPhaseAPower = IntType(650, 'load_phase_A_power', suffix='W', signed=True)
    LoadPhaseBPower = IntType(651, 'load_phase_B_power', suffix='W', signed=True)
    LoadPhaseCPower = IntType(652, 'load_phase_C_power', suffix='W', signed=True)
    LoadTotalPower = IntType(653, 'load_total_power', suffix='W', signed=True)
    """ GENERATOR skipped """

    GeneratorPhaseAVoltage = FloatType(661, 'gen_phase_A_volt', 10, suffix='V')
    GeneratorPhaseBVoltage = FloatType(662, 'gen_phase_B_volt', 10, suffix='V')
    GeneratorPhaseCVoltage = FloatType(663, 'gen_phase_C_volt', 10, suffix='V')
    GeneratorPhaseAPower = IntType(664, 'gen_phase_A_power', suffix='W', signed=True)
    GeneratorPhaseBPower = IntType(665, 'gen_phase_B_power', suffix='W', signed=True)
    GeneratorPhaseCPower = IntType(666, 'gen_phase_C_power', suffix='W', signed=True)
    GeneratorTotalPower = IntType(667, 'gen_total_power', suffix='W', signed=True)

    """ PV Inputs """
    PV1InPower = IntType(672, 'pv1_in_power', suffix='W')
    PV2InPower = IntType(673, 'pv2_in_power', suffix='W')
    PV3InPower = IntType(674, 'pv3_in_power', suffix='W')
    PV4InPower = IntType(675, 'pv4_in_power', suffix='W')
    PV1Voltage = FloatType(676, 'pv1_volt', 10, suffix='V')
    PV1Current = FloatType(677, 'pv1_current', 10, suffix='A')
    PV2Voltage = FloatType(678, 'pv2_volt', 10, suffix='V')
    PV2Current = FloatType(679, 'pv2_current', 10, suffix='A')
    PV3Voltage = FloatType(680, 'pv3_volt', 10, suffix='V')
    PV3Current = FloatType(681, 'pv3_current', 10, suffix='A')
    PV4Voltage = FloatType(682, 'pv4_volt', 10, suffix='V')
    PV4Current = FloatType(683, 'pv4_current', 10, suffix='A')

    @staticmethod
    def as_list() -> List[Register]:
        """ Method for easy iteration over the registers defined here  """
        return [getattr(HoldingRegisters, x) for x in HoldingRegisters.__dict__ if not x.startswith('_')
                and not x.startswith('as_')]


BatteryOnlyRegisters: List[Register] = [

        HoldingRegisters.ControlMode, HoldingRegisters.BatteryControl, HoldingRegisters.BattResistance,
        HoldingRegisters.BattChargingEff, HoldingRegisters.BattShutDownCapacity, HoldingRegisters.BattRestartCapacity,
        HoldingRegisters.BattLowCapacity, HoldingRegisters.BattShutDownVoltage, HoldingRegisters.BattRestartVoltage,
        HoldingRegisters.BattLowVoltage,
        HoldingRegisters.BatteryChargeToday, HoldingRegisters.BatteryDischargeToday,
        HoldingRegisters.BatteryTemp, HoldingRegisters.BatteryVoltage,
        HoldingRegisters.BatteryOutPower, HoldingRegisters.BatteryOutCurrent, HoldingRegisters.BatteryCorrectedAH,
        HoldingRegisters.BatterySOC,
        HoldingRegisters.BMSType, HoldingRegisters.BMSBatteryCapacity, HoldingRegisters.BMSBatterySOH,
        HoldingRegisters.BMSBatteryTemp, HoldingRegisters.BMSBatteryVoltage
]

TotalPowerOnly: List[Register] = [
        HoldingRegisters.GRIDActivePowerIn, HoldingRegisters.GRIDActiveApparentPower,
        HoldingRegisters.GRIDTotalPower, HoldingRegisters.BatteryOutPower, HoldingRegisters.LoadTotalPower,
        HoldingRegisters.InverterTotalPowerOut,
        HoldingRegisters.PV1InPower, HoldingRegisters.PV2InPower
]


class WritableRegister(object):
    """ Register which supports writing
        The value must be set via the `set()` method and then sent to the
        inverter by calling `to_modbus()`

    """
    def __init__(self, address, length=1):
        self.address = address
        self.len = length
        self.value = None
        self.modbus_value = None

    @abstractmethod
    def set(self, x: object):
        pass

    @property
    def to_modbus(self) -> int:
        if self.modbus_value:
            return self.modbus_value
        else:
            return 0


class IntWritable(WritableRegister):

    def __init__(self, address, signed=False, low_limit=None, high_limit=None):
        super(IntWritable, self).__init__(address)
        self._signed = signed
        self._low = low_limit
        self._high = high_limit

    def set(self, x: int):
        if self._low and x < self._low:
            raise ValueError(f'Value < {self._low} not allowed')
        if self._high and x > self._high:
            raise ValueError(f'Value > {self._high} not allowed')
        self.value = x
        if self._signed is True:
            if not -32768 <= x <= 32767:
                raise ValueError('Value out of range -32768..32767')
            self.modbus_value = signed_to_int(x)
        else:
            if not 0 <= x <= 65535:
                raise ValueError('Value out of range 0..65535')
            self.modbus_value = x


class FloatWritable(WritableRegister):
    """
    For registers which accept float values. The modbus value is calculated
        when a value is added via the set() method
    """

    def __init__(self, address, signed=False, scale=100, low_limit=None, high_limit=None):
        super(FloatWritable, self).__init__(address)
        self._signed = signed
        self._low = low_limit
        self._high = high_limit
        self._scale = scale

    def set(self, x: float):
        """ Convert a float to Deye modbus compatible format """
        if self._low and x < self._low:
            raise ValueError(f'Value < {self._low} not allowed')
        if self._high and x > self._high:
            raise ValueError(f'Value > {self._high} not allowed')

        self.value = x
        if self._signed is True:
            if not -327.68 <= x <= 327.67:
                raise ValueError('Signed integer must be be in the range -327.68..327.67')
            self.modbus_value = signed_to_int(int(round(x, 2) * self._scale))
        else:
            self.modbus_value = int(round(x, 2) * self._scale)


class TimeWritable(WritableRegister):
    """ Register to which hour:minutes can be written
        Part of the Sell programmer of the inverter
    """

    def __init__(self, address):
        super(TimeWritable, self).__init__(address)

    def set(self, x: Union[str, datetime.datetime]):
        if isinstance(x, datetime.datetime):
            self.modbus_value = int(x.strftime('%H%M'))
            self.value = x

        elif isinstance(x, str):
            try:
                _x = datetime.datetime.now()
                _x_h, _x_m = x.split(':')
                _x = _x.replace(hour=int(_x_h), minute=int(_x_m))
                self.modbus_value = int(_x.strftime('%H%M'))
                self.value = _x
            except:
                raise ValueError(f'Invalid value [{x}]. Strings must be <hour>:<minute> formatted')


class GridGenWritable(WritableRegister):

    def __init__(self, address):
        super(GridGenWritable, self).__init__(address)

    def set(self, x: ChargeGridGen):
        self.modbus_value = x.value
        self.value = x


class DeviceTimeWriteable(WritableRegister):
    """
    Adjustments of the system time of the inverter
    """
    def __init__(self):
        super(DeviceTimeWriteable, self).__init__(62, 3)

    def set(self, x: datetime.datetime):
        """ Set the time of the inverter """
        as_ints = [int(u) for u in x.strftime('%y %m %d %H %M %S').split(' ')]
        self.modbus_value = to_inv_time(as_ints)
        self.value = x


class BoolWritable(WritableRegister):

    """
    Bool type for holding registers accepting only this type
    """
    def __init__(self, address):
        super(BoolWritable, self).__init__(address)

    def set(self, x: bool):
        """
        Bool type: False - Off/Disabled, True On/Enabled
        :param x:
        :return:
        """
        if not isinstance(x, bool):
            raise ValueError
        self.modbus_value = int(x)
        self.value = x


class GenPortUseWritable(WritableRegister):
    """
    Generator port settings.

    Example:
        >>> from deye_controller.modbus.protocol import GenPortUseWritable
        >>> from deye_controller.modbus.enums import GenPortMode
        >>> v = GenPortUseWritable()
        >>> v.set(GenPortMode.MicroInverter)
        or directly as int
        >>> v.set(2)

        when used from the WritableRegisters class

        >>> from deye_controller.modbus.protocol import GenPortMode
        >>> from deye_controller.modbus.protocol import WritableRegisters
        >>> wr = WritableRegisters()
        >>> wr.GenPortUse.set(GenPortMode.MicroInverter)
    """

    def __init__(self):
        super().__init__(133)

    def set(self, x: Union[int, GenPortMode]):
        if not isinstance(x, GenPortMode):
            if x > GenPortMode.MicroInverter \
                    or x < GenPortMode.GenInput:
                raise ValueError('Invalid value. Must be between 0 and 2')
            self.modbus_value = x
            self.value = GenPortMode(x)
        else:
            self.modbus_value = x.value
            self.value = x


class WritableRegisters:

    DeviceTime = DeviceTimeWriteable()

    ActivePowerRegulation = FloatWritable(address=77, signed=False, low_limit=0, high_limit=120, scale=10)
    ReactivePowerRegulation = FloatWritable(address=78, signed=False, low_limit=0, high_limit=120, scale=10)
    ApparentPowerRegulation = FloatWritable(address=79, signed=False, low_limit=0, high_limit=120, scale=10)

    SwitchOnOff = BoolWritable(address=80)

    BatterControlMode = IntWritable(address=98, low_limit=0, high_limit=1)
    """" 0 - Lead battery | 1 - Lithium """
    EqualizationV = FloatWritable(address=99, low_limit=38, high_limit=61, scale=100)
    AbsorbtionV = FloatWritable(address=100, low_limit=38, high_limit=61, scale=100)
    FloatV = FloatWritable(address=101, low_limit=38, high_limit=61, scale=100)
    BatteryCapacity = IntWritable(address=102, low_limit=0, high_limit=2000)
    BatteryEmptyV = FloatWritable(address=103, low_limit=38, high_limit=61, scale=100)
    ZeroExportPower = IntWritable(address=104, low_limit=20, high_limit=12000)
    """ 20 is set as default on the inverter | high - unknown, limited to max power """
    EqualizatonDaysCycle = IntWritable(address=105, low_limit=0, high_limit=90)
    EqualizationTime = IntWritable(address=106, low_limit=0, high_limit=20)
    """ Resolution 30 minutes -> 20 = 10 hours """
    TEMPCO_mV = IntWritable(address=107, low_limit=0, high_limit=50)

    """ Charge / Discharge """
    MaxChargeAmps = IntWritable(address=108, low_limit=0, high_limit=185)
    MaxDischargeAmps = IntWritable(address=109, low_limit=0, high_limit=185)

    BatteryControl = IntWritable(address=111, low_limit=0, high_limit=2)
    """ See enums.BatteryControlMode """

    BattChargingEfficiency = IntWritable(address=114, low_limit=0, high_limit=100)
    BattCapacityShutDown = IntWritable(address=115, low_limit=0, high_limit=100)
    BattCapacityRestart = IntWritable(address=116, low_limit=0, high_limit=100)
    BattCapacityLow = IntWritable(address=117, low_limit=0, high_limit=100)

    BatteryVoltsShutDown = FloatWritable(address=118, low_limit=38, high_limit=63, scale=100)
    BatteryVoltsRestart = FloatWritable(address=119, low_limit=38, high_limit=63, scale=100)
    BatteryVoltsLow = FloatWritable(address=120, low_limit=38, high_limit=63, scale=100)
    """ Generator Settings """
    GeneratorMaxWorkTime = FloatWritable(address=121, low_limit=0, high_limit=23, scale=10)
    GeneratorCoolingTime = FloatWritable(address=122, low_limit=0, high_limit=23, scale=10)
    GeneratorStartVoltage = FloatWritable(address=123, low_limit=0, high_limit=63, scale=100)
    GeneratorStartCapacity = FloatWritable(address=124, low_limit=0, high_limit=63, scale=100)
    GeneratorChargeCurrent = IntWritable(address=125, low_limit=0, high_limit=185)

    GridChargeStartVoltage = FloatWritable(address=126, low_limit=38, high_limit=61, scale=100)
    GridChargeStartCapacity = IntWritable(address=127, low_limit=0, high_limit=100)
    """ High limit - 63 in the MODBUS documentation """
    GridChargeBattCurrent = IntWritable(address=128, low_limit=0, high_limit=185)

    """ Smart load options """
    GenPortUse = GenPortUseWritable()
    SmartLoadOffVoltage = FloatWritable(address=134, low_limit=38, high_limit=63, scale=100)
    SmartLoadOffCapacity = IntWritable(address=135, low_limit=0, high_limit=100)
    SmartLoadOnVoltage = FloatWritable(address=136, low_limit=38, high_limit=63, scale=100)
    SmartLoadOnCapacity = IntWritable(address=137, low_limit=0, high_limit=100)

    InverterWorkMode = IntWritable(address=142, low_limit=0, high_limit=2)
    GridExportLimit = IntWritable(address=143, low_limit=0, high_limit=15000)
    SolarSell = BoolWritable(address=145)

    SellModeT1 = TimeWritable(148)
    SellModeT2 = TimeWritable(149)
    SellModeT3 = TimeWritable(150)
    SellModeT4 = TimeWritable(151)
    SellModeT5 = TimeWritable(152)
    SellModeT6 = TimeWritable(153)

    SellModeWatts1 = IntWritable(154, low_limit=0)
    SellModeWatts2 = IntWritable(155, low_limit=0)
    SellModeWatts3 = IntWritable(156, low_limit=0)
    SellModeWatts4 = IntWritable(157, low_limit=0)
    SellModeWatts5 = IntWritable(158, low_limit=0)
    SellModeWatts6 = IntWritable(159, low_limit=0)

    """ Not applicable in Lithium mode """
    SellModeVolts1 = FloatWritable(160, low_limit=0, high_limit=63, scale=100)
    SellModeVolts2 = FloatWritable(161, low_limit=0, high_limit=63, scale=100)
    SellModeVolts3 = FloatWritable(162, low_limit=0, high_limit=63, scale=100)
    SellModeVolts4 = FloatWritable(163, low_limit=0, high_limit=63, scale=100)
    SellModeVolts5 = FloatWritable(164, low_limit=0, high_limit=63, scale=100)
    SellModeVolts6 = FloatWritable(165, low_limit=0, high_limit=63, scale=100)

    SellModeSOC1 = IntWritable(166, low_limit=0, high_limit=100)
    SellModeSOC2 = IntWritable(167, low_limit=0, high_limit=100)
    SellModeSOC3 = IntWritable(168, low_limit=0, high_limit=100)
    SellModeSOC4 = IntWritable(169, low_limit=0, high_limit=100)
    SellModeSOC5 = IntWritable(170, low_limit=0, high_limit=100)
    SellModeSOC6 = IntWritable(171, low_limit=0, high_limit=100)

    """ Grid / Generator selection """
    ChargeGridGen1 = GridGenWritable(172)
    ChargeGridGen2 = GridGenWritable(173)
    ChargeGridGen3 = GridGenWritable(174)
    ChargeGridGen4 = GridGenWritable(175)
    ChargeGridGen5 = GridGenWritable(176)
    ChargeGridGen6 = GridGenWritable(177)


    """ Other """
    RestoreConnectionTime = IntWritable(180, low_limit=10, high_limit=300)
    """ In seconds ?!? """
    GridFrequency = IntWritable(183, low_limit=0, high_limit=1)
    """ 0 - 50Hz | 1 - 60Hz """
    GridType = IntWritable(184, low_limit=0, high_limit=2)
    """ 0 - 3_phase | 1 - 1_phase | 2 - split """
    GridHighVoltage = FloatWritable(185, low_limit=180, high_limit=270, scale=10)
    GridLowVoltage = FloatWritable(186, low_limit=180, high_limit=270, scale=10)
    GridFrequencyHigh = FloatWritable(187, low_limit=45, high_limit=65, scale=100)
    GridFrequencyLow = FloatWritable(188, low_limit=45, high_limit=65, scale=100)

    GridPeakShavingPower = IntWritable(191, low_limit=0, high_limit=16000)
    """ Watts """
