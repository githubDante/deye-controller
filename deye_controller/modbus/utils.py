import struct
from typing import Union, List


def to_bytes(val: Union[int, List[int]]):
    """
    Convert PDU integer or list with integers to bytes/

    It's needed for a bunch of Deye registers (SN, Time, etc.)

    :param val:
    :return:
    """
    if isinstance(val, List):
        return bytes.fromhex(''.join([struct.pack('>h', x).hex() for x in val]))
    elif isinstance(val, int):
        return struct.pack('>h', val)
    else:
        raise ValueError('Not int / List[int]: ', val)


def to_signed(val: int):
    """ Convert 2 bytes int to a signed integer """
    return struct.unpack('>h', struct.pack('>H', val))[0]


def signed_to_int(val: int):
    """ Convert signed integer to unsigned int (need when writing to the inverter) """
    return struct.unpack('>H', struct.pack('>h', val))[0]
