'''
    icmplib
    ~~~~~~~

    The power to forge ICMP packets and do ping and traceroute.

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2022 Valentin BELYN.
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

from .ping import async_ping


async def async_multiping(addresses, count=2, interval=0.5, timeout=2,
        concurrent_tasks=50, source=None, family=None, privileged=True,
        **kwargs):
    '''
    Send ICMP Echo Request packets to several network hosts.

    This function is non-blocking.

    :type addresses: list[str]
    :param addresses: The IP addresses of the hosts to which messages
        should be sent. Hostnames and FQDNs are allowed but not
        recommended. You can easily retrieve their IP address by calling
        the built-in `async_resolve` function.

    :type count: int, optional
    :param count: The number of ping to perform per address.
        Default to 2.

    :type interval: int or float, optional
    :param interval: The interval in seconds between sending each packet.
        Default to 0.5.

    :type timeout: int or float, optional
    :param timeout: The maximum waiting time for receiving a reply in
        seconds. Default to 2.

    :type concurrent_tasks: int, optional
    :param concurrent_tasks: The maximum number of concurrent tasks to
        speed up processing. This value cannot exceed the maximum number
        of file descriptors configured on the operating system.
        Default to 50.

    :type source: str, optional
    :param source: The IP address from which you want to send packets.
        By default, the interface is automatically chosen according to
        the specified destinations. This parameter should not be used if
        you are passing both IPv4 and IPv6 addresses to this function.

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

    :rtype: list[Host]
    :returns: A list of `Host` objects containing statistics about the
        desired destinations. The list is sorted in the same order as
        the addresses passed in parameters.

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
        >>> from icmplib import async_multiping
        >>> hosts = asyncio.run(async_multiping(['10.0.0.5', '::1']))

        >>> for host in hosts:
        ...     if host.is_alive:
        ...         print(f'{host.address} is up!')
        ...     else:
        ...         print(f'{host.address} is down!')

        10.0.0.5 is down!
        ::1 is up!

    See the `Host` class for details.

    '''
    loop = asyncio.get_running_loop()
    tasks = []
    tasks_pending = set()

    for address in addresses:
        if len(tasks_pending) >= concurrent_tasks:
            _, tasks_pending = await asyncio.wait(
                tasks_pending,
                return_when=asyncio.FIRST_COMPLETED)

        task = loop.create_task(
            async_ping(
                address=address,
                count=count,
                interval=interval,
                timeout=timeout,
                source=source,
                family=family,
                privileged=privileged,
                **kwargs))

        tasks.append(task)
        tasks_pending.add(task)

    await asyncio.wait(tasks_pending)

    return [task.result() for task in tasks]


def multiping(addresses, count=2, interval=0.5, timeout=2,
        concurrent_tasks=50, source=None, family=None, privileged=True,
        **kwargs):
    '''
    Send ICMP Echo Request packets to several network hosts.

    :type addresses: list[str]
    :param addresses: The IP addresses of the hosts to which messages
        should be sent. Hostnames and FQDNs are allowed but not
        recommended. You can easily retrieve their IP address by calling
        the built-in `resolve` function.

    :type count: int, optional
    :param count: The number of ping to perform per address.
        Default to 2.

    :type interval: int or float, optional
    :param interval: The interval in seconds between sending each packet.
        Default to 0.5.

    :type timeout: int or float, optional
    :param timeout: The maximum waiting time for receiving a reply in
        seconds. Default to 2.

    :type concurrent_tasks: int, optional
    :param concurrent_tasks: The maximum number of concurrent tasks to
        speed up processing. This value cannot exceed the maximum number
        of file descriptors configured on the operating system.
        Default to 50.

    :type source: str, optional
    :param source: The IP address from which you want to send packets.
        By default, the interface is automatically chosen according to
        the specified destinations. This parameter should not be used if
        you are passing both IPv4 and IPv6 addresses to this function.

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

    :rtype: list[Host]
    :returns: A list of `Host` objects containing statistics about the
        desired destinations. The list is sorted in the same order as
        the addresses passed in parameters.

    :raises NameLookupError: If you pass a hostname or FQDN in
        parameters and it does not exist or cannot be resolved.
    :raises SocketPermissionError: If the privileges are insufficient to
        create the socket.
    :raises SocketAddressError: If the source address cannot be assigned
        to the socket.
    :raises ICMPSocketError: If another error occurs. See the
        `ICMPv4Socket` or `ICMPv6Socket` class for details.

    Usage::

        >>> from icmplib import multiping
        >>> hosts = multiping(['10.0.0.5', '127.0.0.1', '::1'])

        >>> for host in hosts:
        ...     if host.is_alive:
        ...         print(f'{host.address} is up!')
        ...     else:
        ...         print(f'{host.address} is down!')

        10.0.0.5 is down!
        127.0.0.1 is up!
        ::1 is up!

    See the `Host` class for details.

    '''
    return asyncio.run(
        async_multiping(
            addresses=addresses,
            count=count,
            interval=interval,
            timeout=timeout,
            concurrent_tasks=concurrent_tasks,
            source=source,
            family=family,
            privileged=privileged,
            **kwargs))
