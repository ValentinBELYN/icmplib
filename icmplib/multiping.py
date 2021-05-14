'''
    icmplib
    ~~~~~~~

    A powerful library for forging ICMP packets and performing ping
    and traceroute.

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2021 Valentin BELYN.
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


def multiping(addresses, count=2, interval=0.01, timeout=2,
        source=None, privileged=True, **kwargs):
    '''
    Send ICMP Echo Request packets to several network hosts.

    This function relies on a single thread to send multiple packets
    simultaneously. If you mix IPv4 and IPv6 addresses, up to two
    threads are used.

    :type addresses: list[str]
    :param addresses: The IP addresses of the hosts to which messages
        should be sent. Hostnames and FQDNs are not allowed. You can
        easily retrieve their IP address by calling the built-in
        `resolve` function.

    :type count: int, optional
    :param count: The number of ping to perform per address.
        Default to 2.

    :type interval: int or float, optional
    :param interval: The interval in seconds between sending each
        packet. Default to 0.01.

    :type timeout: int or float, optional
    :param timeout: The maximum waiting time for receiving all
        responses in seconds. Default to 2.

    :type source: str, optional
    :param source: The IP address from which you want to send packets.
        By default, the interface is automatically chosen according to
        the specified destinations. This parameter should not be used
        if you are passing both IPv4 and IPv6 addresses to this
        function.

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
        Provides a defined level of service to packets by setting the
        DS Field (formerly TOS) or the Traffic Class field of IP
        headers. Packets are delivered with the minimum priority by
        default (Best-effort delivery).
        Intermediate routers must be able to support this feature.
        Only available on Unix systems. Ignored on Windows.

    :rtype: list[Host]
    :returns: A list of `Host` objects containing statistics about the
        desired destinations. The list is sorted in the same order as
        the addresses passed in parameters.

    :raises SocketPermissionError: If the privileges are insufficient
        to create the socket.
    :raises SocketAddressError: If the source address cannot be
        assigned to the socket.
    :raises ICMPSocketError: If another error occurs. See the
        `ICMPv4Socket` or `ICMPv6Socket` class for details.

    Usage::

        >>> from icmplib import multiping
        >>> hosts = multiping(['10.0.0.5', '127.0.0.1', '::1'])

        >>> for host in hosts:
        ...     if host.is_alive:
        ...         print(f'{host.address} is alive!')
        ...
        ...     else:
        ...         print(f'{host.address} is dead!')
        ...
        10.0.0.5 is dead!
        127.0.0.1 is alive!
        ::1 is alive!

    See the `Host` class for details.

    '''
    raise NotImplementedError
