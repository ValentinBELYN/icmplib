'''
    icmplib
    ~~~~~~~

    A powerful Python library for forging ICMP packets and performing
    ping and traceroute.

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2020 Valentin BELYN.
    :license: GNU LGPLv3, see the LICENSE for details.

    ~~~~~~~

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public License
    as published by the Free Software Foundation, either version 3 of
    the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this program.  If not, see
    <https://www.gnu.org/licenses/>.
'''
import asyncio
import random
from functools import partial
from ipaddress import AddressValueError, IPv6Address
from time import sleep

from .exceptions import *
from .models import Host, ICMPRequest
from .sockets import ICMPv4Socket, ICMPv6Socket
from .utils import *


def ping(address, count=4, interval=1, timeout=2, id=PID, source=None,
        privileged=True, **kwargs):
    '''
    Send ICMP Echo Request packets to a network host.

    :type address: str
    :param address: The IP address, hostname or FQDN of the host to
        which messages should be sent. For a deterministic behavior,
        prefer to use an IP address.

    :type count: int, optional
    :param count: The number of ping to perform. Default to 4.

    :type interval: int or float, optional
    :param interval: The interval in seconds between sending each
        packet. Default to 4.

    :type timeout: int or float, optional
    :param timeout: The maximum waiting time for receiving a reply in
        seconds. Default to 2.

    :type id: int, optional
    :param id: The identifier of ICMP requests. Used to match the
        responses with requests. In practice, a unique identifier
        should be used for every ping process. On Linux, this
        identifier is ignored when the `privileged` parameter is
        disabled.

    :type source: str, optional
    :param source: The IP address from which you want to send packets.
        By default, the interface is automatically chosen according to
        the specified destination.

    :type privileged: bool, optional
    :param privileged: When this option is enabled, this library fully
        manages the exchanges and the structure of the ICMP packets.
        Disable this option if you want to use this function without
        root privileges and let the kernel handle ICMP headers.
        Default to True.
        Only available on Unix systems. Ignored on Windows.

    Advanced (**kwags):

    :type payload: bytes, optional
    :param payload: The payload content in bytes. A random payload is
        used by default.

    :type payload_size: int, optional
    :param payload_size: The payload size. Ignored when the `payload`
        parameter is set. Default to 56.

    :type traffic_class: int, optional
    :param traffic_class: The traffic class of ICMP packets.
        Provides a defined level of service to packets by setting the
        DS Field (formerly TOS) or the Traffic Class field of IP
        headers. Packets are delivered with the minimum priority by
        default (Best-effort delivery).
        Intermediate routers must be able to support this feature.
        Only available on Unix systems. Ignored on Windows.

    :rtype: Host
    :returns: A `Host` object containing statistics about the desired
        destination.

    :raises NameLookupError: If you pass a hostname or FQDN in
        parameters and it does not exist or cannot be resolved.
    :raises SocketPermissionError: If the privileges are insufficient
        to create the socket.
    :raises SocketAddressError: If the source address cannot be
        assigned to the socket.
    :raises ICMPSocketError: If another error occurs. See the
        `ICMPv4Socket` or `ICMPv6Socket` class for details.

    Usage::

        >>> from icmplib import ping
        >>> host = ping('1.1.1.1')
        >>> host.avg_rtt
        13.2
        >>> host.is_alive
        True

    See the `Host` class for details.

    '''
    address = resolve(address)

    if is_ipv6_address(address):
        socket = ICMPv6Socket(
            address=source,
            privileged=privileged)

    else:
        socket = ICMPv4Socket(
            address=source,
            privileged=privileged)

    packets_sent = 0
    packets_received = 0

    min_rtt = float('inf')
    avg_rtt = 0.0
    max_rtt = 0.0

    for sequence in range(count):
        request = ICMPRequest(
            destination=address,
            id=id,
            sequence=sequence,
            **kwargs)

        try:
            socket.send(request)
            packets_sent += 1

            reply = socket.receive(request, timeout)
            reply.raise_for_status()
            packets_received += 1

            round_trip_time = (reply.time - request.time) * 1000
            avg_rtt += round_trip_time
            min_rtt = min(round_trip_time, min_rtt)
            max_rtt = max(round_trip_time, max_rtt)

            if sequence < count - 1:
                sleep(interval)

        except ICMPLibError:
            pass

    if packets_received:
        avg_rtt /= packets_received

    else:
        min_rtt = 0.0

    host = Host(
        address=address,
        min_rtt=min_rtt,
        avg_rtt=avg_rtt,
        max_rtt=max_rtt,
        packets_sent=packets_sent,
        packets_received=packets_received)

    socket.close()

    return host


async def aioping(address, count=4, interval=1, timeout=2, packet_id=0, source=None, privileged=True, **kwargs):
    """
    Send ICMP Echo Request packets to a network host.

    Same API as `ping`.
    Usage::
        >>> import asyncio
        >>> from icmplib import aioping
        >>> asyncio.run(aioping('1.1.1.1'))
        Or
        >>> async def my_func():
        >>>     host = await aioping('1.1.1.1')
        >>>     host.avg_rtt
        >>>     host.is_alive
        >>> asyncio.run(my_func())
        13.2
        True

    See the `Host` class for details.
    """
    address = resolve(address)

    try:
        IPv6Address(address)
        sock = ICMPv6Socket(address=source, privileged=privileged)
    except AddressValueError:
        sock = ICMPv4Socket(address=source, privileged=privileged)
    sock._socket.setblocking(False)  # Should probably be moved down to the Socket API?
    packets_sent = 0
    packets_received = 0

    min_rtt = float('inf')
    avg_rtt = 0.0
    max_rtt = 0.0
    packet_id = random.randint(0, 100000) if not packet_id else packet_id
    loop = asyncio.get_event_loop()
    for sequence in range(count):
        request = ICMPRequest(destination=address, id=packet_id, sequence=sequence, **kwargs)
        try:
            await loop.run_in_executor(None, partial(sock.send, request))
            packets_sent += 1
            reply = await loop.run_in_executor(None, partial(sock.receive, request, timeout))
            reply.raise_for_status()
            packets_received += 1

            round_trip_time = (reply.time - request.time) * 1000
            avg_rtt += round_trip_time
            min_rtt = min(round_trip_time, min_rtt)
            max_rtt = max(round_trip_time, max_rtt)

            if sequence < count - 1:
                await asyncio.sleep(interval)

        except ICMPLibError:
            pass

    if packets_received:
        avg_rtt /= packets_received

    else:
        min_rtt = 0.0

    host = Host(
        address=address,
        min_rtt=min_rtt,
        avg_rtt=avg_rtt,
        max_rtt=max_rtt,
        packets_sent=packets_sent,
        packets_received=packets_received,
    )

    sock.close()

    return host
