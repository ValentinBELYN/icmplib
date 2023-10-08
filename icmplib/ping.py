'''
    icmplib
    ~~~~~~~

    Easily forge ICMP packets and make your own ping and traceroute.

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2023 Valentin BELYN.
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
from time import sleep

from .sockets import ICMPv4Socket, ICMPv6Socket, AsyncSocket
from .models import ICMPRequest, Host
from .exceptions import ICMPLibError
from .utils import *


def ping(address, count=4, interval=1, timeout=2, id=None, source=None,
        family=None, privileged=True, **kwargs):
    '''
    Send ICMP Echo Request packets to a network host.

    :type address: str
    :param address: The IP address, hostname or FQDN of the host to
        which messages should be sent. For deterministic behavior,
        prefer to use an IP address.

    :type count: int, optional
    :param count: The number of ping to perform. Default to 4.

    :type interval: int or float, optional
    :param interval: The interval in seconds between sending each packet.
        Default to 1.

    :type timeout: int or float, optional
    :param timeout: The maximum waiting time for receiving a reply in
        seconds. Default to 2.

    :type id: int, optional
    :param id: The identifier of ICMP requests. Used to match the
        responses with requests. In practice, a unique identifier should
        be used for every ping process. On Linux, this identifier is
        ignored when the `privileged` parameter is disabled. The library
        handles this identifier itself by default.

    :type source: str, optional
    :param source: The IP address from which you want to send packets.
        By default, the interface is automatically chosen according to
        the specified destination.

    :type family: int, optional
    :param family: The address family if a hostname or FQDN is specified.
        Can be set to `4` for IPv4 or `6` for IPv6 addresses. By default,
        this function searches for IPv4 addresses first before searching
        for IPv6 addresses.

    :type privileged: bool, optional
    :param privileged: When this option is enabled, this library fully
        manages the exchanges and the structure of ICMP packets.
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
        Provides a defined level of service to packets by setting the DS
        Field (formerly TOS) or the Traffic Class field of IP headers.
        Packets are delivered with the minimum priority by default
        (Best-effort delivery).
        Intermediate routers must be able to support this feature.
        Only available on Unix systems. Ignored on Windows.

    :rtype: Host
    :returns: A `Host` object containing statistics about the desired
        destination.

    :raises NameLookupError: If you pass a hostname or FQDN in
        parameters and it does not exist or cannot be resolved.
    :raises SocketPermissionError: If the privileges are insufficient to
        create the socket.
    :raises SocketAddressError: If the source address cannot be assigned
        to the socket.
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
    if is_hostname(address):
        address = resolve(address, family)[0]

    if is_ipv6_address(address):
        _Socket = ICMPv6Socket
    else:
        _Socket = ICMPv4Socket

    id = id or unique_identifier()
    packets_sent = 0
    rtts = []

    with _Socket(source, privileged) as sock:
        for sequence in range(count):
            if sequence > 0:
                sleep(interval)

            request = ICMPRequest(
                destination=address,
                id=id,
                sequence=sequence,
                **kwargs)

            try:
                sock.send(request)
                packets_sent += 1

                reply = sock.receive(request, timeout)
                reply.raise_for_status()

                rtt = (reply.time - request.time) * 1000
                rtts.append(rtt)

            except ICMPLibError:
                pass

    return Host(address, packets_sent, rtts)


async def async_ping(address, count=4, interval=1, timeout=2, id=None,
        source=None, family=None, privileged=True, **kwargs):
    '''
    Send ICMP Echo Request packets to a network host.

    This function is non-blocking.

    :type address: str
    :param address: The IP address, hostname or FQDN of the host to
        which messages should be sent. For deterministic behavior,
        prefer to use an IP address.

    :type count: int, optional
    :param count: The number of ping to perform. Default to 4.

    :type interval: int or float, optional
    :param interval: The interval in seconds between sending each packet.
        Default to 1.

    :type timeout: int or float, optional
    :param timeout: The maximum waiting time for receiving a reply in
        seconds. Default to 2.

    :type id: int, optional
    :param id: The identifier of ICMP requests. Used to match the
        responses with requests. In practice, a unique identifier should
        be used for every ping process. On Linux, this identifier is
        ignored when the `privileged` parameter is disabled. The library
        handles this identifier itself by default.

    :type source: str, optional
    :param source: The IP address from which you want to send packets.
        By default, the interface is automatically chosen according to
        the specified destination.

    :type family: int, optional
    :param family: The address family if a hostname or FQDN is specified.
        Can be set to `4` for IPv4 or `6` for IPv6 addresses. By default,
        this function searches for IPv4 addresses first before searching
        for IPv6 addresses.

    :type privileged: bool, optional
    :param privileged: When this option is enabled, this library fully
        manages the exchanges and the structure of ICMP packets.
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
        Provides a defined level of service to packets by setting the DS
        Field (formerly TOS) or the Traffic Class field of IP headers.
        Packets are delivered with the minimum priority by default
        (Best-effort delivery).
        Intermediate routers must be able to support this feature.
        Only available on Unix systems. Ignored on Windows.

    :rtype: Host
    :returns: A `Host` object containing statistics about the desired
        destination.

    :raises NameLookupError: If you pass a hostname or FQDN in
        parameters and it does not exist or cannot be resolved.
    :raises SocketPermissionError: If the privileges are insufficient to
        create the socket.
    :raises SocketAddressError: If the source address cannot be assigned
        to the socket.
    :raises ICMPSocketError: If another error occurs. See the
        `ICMPv4Socket` or `ICMPv6Socket` class for details.

    Usage::

        >>> import asyncio
        >>> from icmplib import async_ping
        >>> host = asyncio.run(async_ping('1.1.1.1'))
        >>> host.avg_rtt
        13.2
        >>> host.is_alive
        True

    See the `Host` class for details.

    '''
    if is_hostname(address):
        address = (await async_resolve(address, family))[0]

    if is_ipv6_address(address):
        _Socket = ICMPv6Socket
    else:
        _Socket = ICMPv4Socket

    id = id or unique_identifier()
    packets_sent = 0
    rtts = []

    with AsyncSocket(_Socket(source, privileged)) as sock:
        for sequence in range(count):
            if sequence > 0:
                await asyncio.sleep(interval)

            request = ICMPRequest(
                destination=address,
                id=id,
                sequence=sequence,
                **kwargs)

            try:
                sock.send(request)
                packets_sent += 1

                reply = await sock.receive(request, timeout)
                reply.raise_for_status()

                rtt = (reply.time - request.time) * 1000
                rtts.append(rtt)

            except ICMPLibError:
                pass

    return Host(address, packets_sent, rtts)
