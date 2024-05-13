"""
MODBUS Registers for DEYE single phase inverters
"""
from typing import List
from .protocol import (LongType, LongUnsignedType, BoolType, DeviceTime, DeviceType,
                       DeviceSerialNumber, IntType, FloatType, RunState, Register,
                       LongUnsignedHoleType, TempWithOffset)


class DeviceTimeSingle(DeviceTime):

    def __init__(self):
        super().__init__()
        self.address = 22


class OffsetValue(FloatType):
    def __init__(self, address, name, scale=10, offset=1000, suffix=''):
        super().__init__(address, name, scale, suffix=suffix)
        self.offset = offset


class RunStateSingle(RunState):

    def __init__(self):
        super().__init__()
        self.address = 59


class HoldingRegistersSingleCommon:

    DeviceType = DeviceType()
    CommProtocol = IntType(1, 'modbus_address')
    SerialNumber = DeviceSerialNumber()
    RatedPower = IntType(8, 'rated_power')

    DeviceTime = DeviceTimeSingle()  # Address 22 + 3
    MinimumInsulationImpedance = FloatType(25, 'minimum_insulation_impedance', 10, suffix='kOhm')
    DCUpperLimit_V = FloatType(26, 'dc_voltage_upper_limit', 10, suffix='V')

    GridUpperLimit_A = FloatType(31, 'grid_current_upper_limit', 10, suffix='A')

    StartingUpperLimit_V = FloatType(32, 'starting_voltage_upper_limit', 10, suffix='V')
    StartingLowerLimit_V = FloatType(33, 'starting_voltage_lower_limit', 10, suffix='V')

    InternalTempUpperLimit = FloatType(36, 'internal_temp_upper_limit', 10, suffix='°C')

    PFRegulation = OffsetValue(39, 'power_factor_regulation', scale=1000, offset=1000)
    ActivePowerRegulation = FloatType(40, 'active_power_regulation', scale=10, suffix='%')
    ReactivePowerRegulation = FloatType(41, 'reactive_power_regulation', scale=10, suffix='%')
    ApparentPowerRegulation = FloatType(42, 'apparent_power_regulation', scale=10, suffix='%')
    SwitchOnOff = BoolType(43, 'switch_on_off')
    """ Factory reset skipped """

    SelfCheck = BoolType(45, 'self_check_enabled')
    IslandProtect = BoolType(46, 'island_protection_enabled')

    """ Some skipped for now """

    RunState = RunStateSingle()  # 59
    DailyActivePower = FloatType(60, 'daily_active_power', scale=10, suffix='kWh')
    DailyReactivePower = FloatType(61, 'daily_reactive_power', scale=10, suffix='kWh')
    DailyGridWorkingTime = IntType(62, 'daily_grid_working_time', suffix='s')

    TotalActivePower = LongType(63, 'total_active_power', scale=10, suffix='kWh')
    """ #63 - probably Micro only """

    """ 91 """
    ACRadiatorTemp = TempWithOffset(91, 'ac_radiator_temperature', scale=10)
    PowerFactor = FloatType(93, 'power_factor', scale=1)
    """ Probably wrong value - needs research """
    AmbientTemp = FloatType(95, 'ambient_temperature', scale=10, suffix='°C')
    PVPowerHistory = LongUnsignedType(96, 'pv_power_history', scale=10, suffix='kWh')

    # TODO: 100 through 106 - handling for Warning and Fault messages
    CorrectedAH = IntType(107, 'corrected_Ah', suffix='Ah')
    DailyPVPower = FloatType(108, 'daily_pv_power', scale=10, suffix='kWh')

    """ Debug & MI data up to #150 """


class HoldingRegistersSingleMicro(HoldingRegistersSingleCommon):
    """ Single phase + Micro Inverter specific """

    GridUpperLimit_V = FloatType(27, 'grid_voltage_upper_limit', 10, suffix='V')
    GridLowerLimit_V = FloatType(28, 'grid_voltage_lower_limit', 10, suffix='V')
    GridUpperLimit_F = FloatType(29, 'grid_frequency_upper_limit', 100, suffix='Hz')
    GridLowerLimit_F = FloatType(30, 'grid_frequency_lower_limit', 100, suffix='Hz')

    OverFreqDeratePoint = FloatType(34, 'over_frequency_derate_point', 100, suffix='Hz')
    OverFreqDerateRate = IntType(35, 'over_frequency_derate_rate', suffix='%')

    DailyPowerComponent1 = FloatType(65, 'daily_power_component_1', scale=10, suffix='kWh')
    DailyPowerComponent2 = FloatType(66, 'daily_power_component_2', scale=10, suffix='kWh')
    DailyPowerComponent3 = FloatType(67, 'daily_power_component_3', scale=10, suffix='kWh')
    DailyPowerComponent4 = FloatType(68, 'daily_power_component_4', scale=10, suffix='kWh')
    TotalPowerComponent1 = LongUnsignedType(69, 'total_power_component_1', scale=10, suffix='kWh')
    TotalPowerComponent2 = LongUnsignedType(71, 'total_power_component_2', scale=10, suffix='kWh')
    """ #73 not used """
    TotalPowerComponent3 = LongUnsignedType(74, 'total_power_component_3', scale=10, suffix='kWh')
    TotalPowerComponent4 = LongUnsignedType(77, 'total_power_component_4', scale=10, suffix='kWh')
    GridFrequency = FloatType(79, 'grid_frequency', scale=100, suffix='Hz')

    DCTransformerTemp = FloatType(90, 'dc_transformer_temperature', scale=10, suffix='°C')

    DCVoltage_1 = FloatType(109, 'dc_voltage_1', scale=10, suffix='V')
    DCCurrent_1 = FloatType(110, 'dc_current_1', scale=10, suffix='A')
    DCVoltage_2 = FloatType(111, 'dc_voltage_2', scale=10, suffix='V')
    DCCurrent_2 = FloatType(112, 'dc_current_2', scale=10, suffix='A')
    DCVoltage_3 = FloatType(113, 'dc_voltage_3', scale=10, suffix='V')
    DCCurrent_3 = FloatType(114, 'dc_current_3', scale=10, suffix='A')
    DCVoltage_4 = FloatType(115, 'dc_voltage_4', scale=10, suffix='V')
    DCCurrent_4 = FloatType(116, 'dc_current_4', scale=10, suffix='A')

    @staticmethod
    def as_list() -> List[Register]:
        """ Method for easy iteration over the registers defined here  """
        return [getattr(HoldingRegistersSingleMicro, x) for x in
                HoldingRegistersSingleMicro.__dict__ if not x.startswith('_')
                and not x.startswith('as_')]


class HoldingRegistersSingleHybrid(HoldingRegistersSingleCommon):
    """ Single phase + Hybrid Inverter specific """

    MonthlyPVPower = IntType(65, 'monthly_pv_power', suffix='kWh')
    MonthlyLoadPower = IntType(66, 'monthly_load_power', suffix='kWh')
    MonthlyGridPower = IntType(67, 'monthly_grid_power', suffix='kWh')
    YearlyPVPower = LongUnsignedType(68, 'yearly_pv_power', scale=10, suffix='kWh')
    DailyBatteryCharge = FloatType(70, 'daily_battery_charge', scale=10, suffix='kWh')
    DailyBatteryDischarge = FloatType(71, 'daily_battery_discharge', scale=10, suffix='kWh')
    TotalBatteryCharge = LongUnsignedType(72, 'total_battery_charge', 10, suffix='kWh')
    TotalBatteryDischarge = LongUnsignedType(74, 'total_battery_discharge', 10, suffix='kWh')

    DailyGridBought = FloatType(76, 'daily_bought_from_grid', 10, suffix='kWh')
    DailyGridSold = FloatType(77, 'daily_sold_to_grid', 10, suffix='kWh')

    TotalGridInPower = LongUnsignedHoleType(78, 'total_grid_in_power', scale=10, suffix='kWh')
    TotalGridOutPower = LongUnsignedType(81, 'total_grid_out_power', scale=10, suffix='kWh')

    GeneratorDailyTime = FloatType(83, 'gen_daily_operating_time', scale=10, suffix='hours')
    TotalLoadPower = LongUnsignedType(85, 'total_load_power', scale=10, suffix='kWh')
    AnnualLoadPower = LongUnsignedType(87, 'annual_load_power', scale=10, suffix='kWh')
    AnnualGridOutPower = LongUnsignedType(98, 'annual_grid_out_power', scale=10, suffix='kWh')


    @staticmethod
    def as_list() -> List[Register]:
        """ Method for easy iteration over the registers defined here  """
        return [getattr(HoldingRegistersSingleHybrid, x) for x in
                HoldingRegistersSingleHybrid.__dict__ if not x.startswith('_')
                and not x.startswith('as_')]


class HoldingRegistersSingleString(HoldingRegistersSingleCommon):
    """ String inverter specific """

    TotalReactivePower = LongType(65, 'total_reactive_power', scale=10, suffix='kVarh')
    TotalWorkTime = LongType(67, 'total_work_time', scale=10, suffix='hours')
    InverterEfficiency = FloatType(69, 'inverter_efficiency', scale=10, suffix='%')
    GridVoltageAB = FloatType(70, 'grid_voltage_ab', scale=10, suffix='V')
    GridVoltageBC = FloatType(71, 'grid_voltage_bc', scale=10, suffix='V')
    GridVoltageAC = FloatType(72, 'grid_voltage_ac', scale=10, suffix='V')
    GridVoltageA = FloatType(73, 'grid_voltage_a', scale=10, suffix='V')
    GridVoltageB = FloatType(74, 'grid_voltage_b', scale=10, suffix='V')
    GridVoltageC = FloatType(75, 'grid_voltage_c', scale=10, suffix='V')
    GridCurrentA = FloatType(76, 'grid_current_a', scale=10, suffix='A')
    GridCurrentB = FloatType(77, 'grid_current_b', scale=10, suffix='A')
    GridCurrentC = FloatType(78, 'grid_current_b', scale=10, suffix='A')

    CurrentPower = LongUnsignedType(80, 'current_power', scale=10, suffix='W')
    InputActivePower = LongUnsignedType(82, 'input_active_power', scale=10, suffix='W')
    OutputApparentPower = LongUnsignedType(84, 'output_apparent_power', scale=10, suffix='W')
    OutputActivePower = LongUnsignedType(86, 'output_active_power', scale=10, suffix='W')
    OutputReactivePower = LongUnsignedType(88, 'output_reactive_power', scale=10, suffix='W')

    RCDLeakCurrent = FloatType(98, 'RCD_leak_current', scale=100, suffix='A')
    PowerLimiter = FloatType(99, 'power_limiter', scale=1, suffix='W')

    @staticmethod
    def as_list() -> List[Register]:
        """ Method for easy iteration over the registers defined here  """
        return [getattr(HoldingRegistersSingleString, x) for x in
                HoldingRegistersSingleString.__dict__ if not x.startswith('_')
                and not x.startswith('as_')]
