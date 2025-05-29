import socket



def is_host_reachable(address: str, port: int) -> bool:
    """
    Check if connection can be established with the remote endpoint

    :param address: IP address
    :param port: Destination port
    :return: True if the host can be reached
    """

    try:
        c = socket.create_connection((address, port), timeout=.5)  # 500ms should be enough
        c.close()
        return True
    except:
        return False