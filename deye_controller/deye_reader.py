from pysolarmanv5 import PySolarmanV5, V5FrameError
from .modbus.protocol import HoldingRegisters, BatteryOnlyRegisters, TotalPowerOnly
from .logger_scan import solar_scan
from argparse import ArgumentParser
from .utils import group_registers, map_response
import json


def read_inverter(address: str, logger_serial: int, batt_only=False, power_only=False, combo=False,
                  as_json=False, to_file=None):
    inv = PySolarmanV5(address, int(logger_serial), port=8899, mb_slave_id=1, verbose=False, socket_timeout=10,
                       error_correction=True)
    iterator = []
    js = {'logger': logger_serial,
          'serial': 0,
          'data': []
          }
    if batt_only:
        iterator = [HoldingRegisters.SerialNumber] + BatteryOnlyRegisters
    elif power_only:
        iterator = [HoldingRegisters.SerialNumber] + TotalPowerOnly
    elif combo:
        iterator = [HoldingRegisters.SerialNumber] + BatteryOnlyRegisters
        for reg in TotalPowerOnly:
            if reg not in iterator:
                iterator.append(reg)

    else:
        iterator = HoldingRegisters.as_list()
    reg_groups = group_registers(iterator)
    for group in reg_groups:
        res = inv.read_holding_registers(group.start_address, group.len)

        map_response(res, group)
        for reg in group:
            if hasattr(reg, 'suffix'):
                suffix = reg.suffix
            else:
                suffix = ''
            if as_json:
                if reg == HoldingRegisters.SerialNumber:
                    js['serial'] = reg.format()
                else:
                    js['data'].append({reg.description: {'addr': reg.address, 'value': reg.format(), 'unit': suffix}})
            else:
                string = '[{:>35s}]: {} {}'.format(reg.description.title(), reg.format(), suffix)
                print(string, flush=True)

    if as_json:
        if to_file:
            try:
                with open(to_file, 'w') as f:
                    f.write(json.dumps(js, indent=2, default=str))
                print(f'Data saved to: {to_file}')
            except Exception as e:
                print(f'Error occurred during the write to <{to_file}>. Error: {e}')
                print(json.dumps(js, indent=2, default=str))
        else:
            print(json.dumps(js, indent=2, default=str))

    try:
        inv.disconnect()
    except:
        pass


def _read_registers(address: str, logger_serial: int, start: int, length: int):
    inv = PySolarmanV5(address, int(logger_serial), port=8899, mb_slave_id=1, verbose=False, socket_timeout=10)
    try:
        res = inv.read_holding_registers(start, length)
        print(res)
    except (V5FrameError, TimeoutError):
        print('Read failed! Try again.')

    try:
        inv.disconnect()
    except:
        pass


def _write_register(address: str, logger: int, reg_address: int, val: int):
    inv = PySolarmanV5(address, int(logger), port=8899, mb_slave_id=1, verbose=False, socket_timeout=10)
    try:
        res = inv.write_multiple_holding_registers(reg_address, [val])
        print(f'Wrote: {res}')
    except (V5FrameError, TimeoutError):
        print('Write failed! Try again later.')

    try:
        inv.disconnect()
    except:
        pass


def read_from_inverter():
    parser = ArgumentParser('deye-read')
    parser.add_argument('--battery', help='Read only battery related parameters', action='store_true')
    parser.add_argument('--power', help='Read only total power related parameters', action='store_true')
    parser.add_argument('--combo', help='Read only power/battery related parameters', action='store_true')
    parser.add_argument('--json', help='Show the data as JSON', action='store_true')
    parser.add_argument('--out', help='Write the JSON output to this file', required=False, type=str, default=False)
    parser.add_argument('address', help='Datalogger IP address')
    parser.add_argument('serial', help='Datalogger serial', type=int)
    opts = parser.parse_args()
    read_inverter(opts.address, opts.serial, batt_only=opts.battery, power_only=opts.power, combo=opts.combo,
                  as_json=opts.json, to_file=opts.out)


def test_register():
    parser = ArgumentParser('deye-regtest')
    parser.add_argument('address', help='Datalogger IP address')
    parser.add_argument('serial', help='Datalogger serial', type=int)
    parser.add_argument('start', type=int, help='Start register', default=1)
    parser.add_argument('count', type=int, help='Number of register to be read', default=1)

    opt = parser.parse_args()
    _read_registers(opt.address, opt.serial, opt.start, opt.count)


def test_write():
    parser = ArgumentParser('deye-regwrite')
    parser.add_argument('address', help='Datalogger IP address')
    parser.add_argument('serial', help='Datalogger serial', type=int)
    parser.add_argument('register', type=int, help='Register address')
    parser.add_argument('value', type=int, help='Value to write')

    opts = parser.parse_args()

    _write_register(opts.address, opts.serial, opts.register, opts.value)


def scan_for_loggers():
    parser = ArgumentParser('deye-scan', epilog='Scan the network for compatible dataloggers')
    parser.add_argument('broadcast', help='Network broadcast address')
    opts = parser.parse_args()

    res = solar_scan(opts.broadcast)
    for logger in res:
        print(f'{logger}')
