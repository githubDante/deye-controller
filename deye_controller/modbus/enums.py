import enum


class InverterState(int, enum.Enum):

    StandBy     = 0
    SelfCheck   = 1
    Normal      = 2
    Alarm       = 3
    Fault       = 4

    @classmethod
    def _missing_(cls, value):
        return InverterState.Fault

    def __format__(self, format_spec):
        return self.name


class ControlMode(int, enum.Enum):

    LeadBattery = 0
    LithiumBattery = 1

    @classmethod
    def _missing_(cls, value):
        return ControlMode.LeadBattery

    def __format__(self, format_spec):
        return self.name


class BatteryControlMode(int, enum.Enum):

    ByVoltage = 0
    ByCapacity = 1
    NoBattery = 2
    Error = 99

    @classmethod
    def _missing_(cls, value: int):
        return BatteryControlMode.Error

    def __format__(self, format_spec):
        return self.name


class BMSMode(int, enum.Enum):

    PYLONTech_CAN   = 0
    SACRED_SUN_FOXX = 1
    KOK             = 2
    Keith           = 3
    TopPay          = 4
    PYLONTech_485   = 5
    VISIONGroup_CAN = 13
    WattSonic       = 14

    def __format__(self, format_spec):
        return self.name

    @classmethod
    def _missing_(cls, value):
        print(f'Unknown CAN/MODBUS protocol: {value}')
        return BMSMode.PYLONTech_CAN


class TimeOfUse(int, enum.Enum):
    """ Time of Use settings on the inverter screen """
    ENABLED = 1
    MONDAY = 2
    TUESDAY = 4
    WEDNESDAY = 8
    THURSDAY = 16
    FRIDAY = 32
    SATURDAY = 64
    SUNDAY = 128

    @staticmethod
    def from_int(val: int):
        """ List representation of the settings which are enabled """
        r = []
        for u in [TimeOfUse.ENABLED, TimeOfUse.MONDAY, TimeOfUse.TUESDAY, TimeOfUse.WEDNESDAY,
                  TimeOfUse.THURSDAY, TimeOfUse.FRIDAY, TimeOfUse.SATURDAY, TimeOfUse.SUNDAY]:
            if val & u == 0:
                continue
            r.append(u)
        return r

    def __format__(self, format_spec):
        return self.name


class ChargeGridGen(int, enum.Enum):
    """ Grid / Generator charge states """
    GridGenDisabled     = 0  # Only from PV
    GridEnabled         = 1
    GenEnabled          = 2
    GridGenEnabled      = 3

    @classmethod
    def _missing_(cls, value: object):
        return ChargeGridGen.GridGenDisabled

    def __format__(self, format_spec):
        return self.name


class TwoBitState(int, enum.Enum):
    """
    States as described for register 178
    00 / 01 (binary) - means not defined / not used
    10 (binary) - disabled
    11 (binary) - enabled   
    """
    Undefined_1 = 0
    Undefined_2 = 1
    Disabled = 2
    Enabled = 3

    @classmethod
    def _missing_(cls, value: object):
        return TwoBitState.Undefined_1

    def __format__(self, format_spec):
        return self.name


class PowerOnOffState(int, enum.Enum):
    PoweredOff = 0
    PoweredOn = 1

    @classmethod
    def _missing_(cls, value: object):
        return PowerOnOffState.PoweredOff

    def __format__(self, format_spec):
        return self.name


class BitOnOff(int, enum.Enum):
    """
    AC Relays (552)
    """

    Off = 0
    On = 1

    @classmethod
    def _missing_(cls, value: object):
        return BitOnOff.Off

    def __format__(self, format_spec):
        return self.name


class GenPortMode(int, enum.Enum):
    """
    Register 133
    """
    GenInput = 0
    SmartLoad = 1
    MicroInverter = 2

    @classmethod
    def _missing_(cls, value: object):
        return GenPortMode.GenInput

    def __format__(self, format_spec):
        return self.name

    def __str__(self):
        return self.name


class WorkMode(int, enum.Enum):
    """
    Register 142 - GH #16
    """

    SellingFirst = 0
    ZeroExportToLoad = 1
    ZeroExportToCT = 2
    Unknown = -1

    def __str__(self):
        return self.name

    @classmethod
    def _missing_(cls, value):
        return WorkMode.Unknown



class DeyeHybridFaultInfo(int, enum.Enum):
    """
    Fault Information Definitions
    """

    Normal = 0
    F1 = 1
    F02 = F1 << 1
    F03 = F1 << 2
    F04 = F1 << 3
    F05 = F1 << 4
    F06 = F1 << 5
    F07 = F1 << 6
    F08 = F1 << 7
    F09 = F1 << 8
    F10 = F1 << 9
    F11 = F1 << 10
    F12 = F1 << 11
    F13 = F1 << 12
    F14 = F1 << 13
    F15 = F1 << 14
    F16 = F1 << 15
    F17 = F1 << 16
    F18 = F1 << 17
    F19 = F1 << 18
    F20 = F1 << 19
    F21 = F1 << 20
    F22 = F1 << 21
    F23 = F1 << 22
    F24 = F1 << 23
    F25 = F1 << 24
    F26 = F1 << 25
    F27 = F1 << 26
    F28 = F1 << 27
    F29 = F1 << 28

    F35 = F1 << 34
    F41 = F1 << 40
    F42 = F1 << 41

    F46 = F1 << 45
    F47 = F1 << 46
    F48 = F1 << 47
    F49 = F1 << 48

    F56 = F1 << 55
    F58 = F1 << 57

    F62 = F1 << 61
    F63 = F1 << 62
    F64 = F1 << 63

    F99 = F1 << 65  # Outside the register range

    @classmethod
    def _missing_(cls, value):
        return DeyeHybridFaultInfo.F99



fault_map_hybrid = {
    DeyeHybridFaultInfo.Normal: 'OK/No Error',
    DeyeHybridFaultInfo.F07: 'DC/DC soft start fault',
    DeyeHybridFaultInfo.F10: 'Auxiliary power supply failure',
    DeyeHybridFaultInfo.F13: 'Inverter work mode changed',
    DeyeHybridFaultInfo.F18: 'AC side over current fault',
    DeyeHybridFaultInfo.F20: 'DC side over current fault',
    DeyeHybridFaultInfo.F22: 'Tz_EmergS Stop_Fault',
    DeyeHybridFaultInfo.F23: 'AC/PV Leakage current fault',
    DeyeHybridFaultInfo.F24: 'PV isolation resistance is too low',
    DeyeHybridFaultInfo.F26: 'DC busbar is unbalanced',
    DeyeHybridFaultInfo.F29: 'Parallel CANBus Fault',
    DeyeHybridFaultInfo.F35: 'No AC grid',
    DeyeHybridFaultInfo.F41: 'Parallel system Stopped',
    DeyeHybridFaultInfo.F42: 'AC line low voltage',
    DeyeHybridFaultInfo.F46: 'Backup battery fault.',
    DeyeHybridFaultInfo.F47: 'Grid frequency out of range (High)',
    DeyeHybridFaultInfo.F48: 'Grid frequency out of range (Low)',
    DeyeHybridFaultInfo.F49: 'Backup battery fault.',
    DeyeHybridFaultInfo.F56: 'Battery voltage low',
    DeyeHybridFaultInfo.F58: 'BMS communication fault',
    DeyeHybridFaultInfo.F62: 'DRM Fault',
    DeyeHybridFaultInfo.F63: 'ARC Fault',
    DeyeHybridFaultInfo.F64: 'Heat sink temperature is too high',

    DeyeHybridFaultInfo.F99: 'UNKNOWN'
}