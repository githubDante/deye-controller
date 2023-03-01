import socket
from typing import List


class SolarmanDataLogger:

    def __init__(self, address, mac, serial):
        self.address = address
        self.mac = mac
        self.serial = serial

    def __format__(self, format_spec):
        return f'''
        LoggerSN:   {self.serial}
        IP:         {self.address}
        MAC:        {self.mac}
        '''


def solar_scan(broadcast_address: str) -> List[SolarmanDataLogger]:
    """
    Scan the network for available loggers.

    This functon is copied directly from pysolarmanv5 examples

    :param broadcast_address: Broadcast address for the current network
    :return:
    :rtype:
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(1.0)

    request = "WIFIKIT-214028-READ"
    address = (broadcast_address, 48899)

    sock.sendto(request.encode(), address)
    results = []
    while True:
        try:
            data = sock.recv(1024)
        except socket.timeout:
            break
        keys = dict.fromkeys(['ipaddress', 'mac', 'serial'])
        values = data.decode().split(",")
        results.append(SolarmanDataLogger(*values))

    return results
