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
    ENABLED = 1 << 0
    MONDAY = 1 << 1
    TUESDAY = 1 << 2
    WEDNESDAY = 1 << 3
    THURSDAY = 1 << 4
    FRIDAY = 1 << 5
    SATURDAY = 1 << 6
    SUNDAY = 1 << 7


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
