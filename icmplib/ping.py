'''
    icmplib
    ~~~~~~~

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2019 Valentin BELYN.
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

from .sockets import ICMPv4Socket, ICMPv6Socket
from .models import ICMPRequest, Host
from .exceptions import *
from .utils import PID, is_ipv6_address

from threading import Thread
from time import sleep


class PingThread(Thread):
    def __init__(self, **options):
        super().__init__()

        self._options = options
        self._host = None

    def run(self):
        self._host = ping(**self._options)

    @property
    def host(self):
        return self._host


def ping(address, count=4, interval=1, id=PID, **kwargs):
    '''
    Send ICMP ECHO_REQUEST packets to a network host.

    :type address: str
    :param address: The IP address of the gateway or host to which
        the message should be sent.

    :type count: int
    :param count: (Optional) The number of ping to perform.

    :type interval: int or float
    :param interval: (Optional) The interval in seconds between sending
        each packet.

    :type id: int
    :param id: (Optional) The identifier of the request. Used to match
        the reply with the request. In practice, a unique identifier is
        used for every ping process.
    
    :param kwargs: Pass to ICMPRequest

    :rtype: Host
    :returns: A Host object containing statistics about the desired
        destination.

    :raises SocketPermissionError: If the permissions are insufficient
        to create a socket.

    Usage::

        >>> from icmplib import ping
        >>> host = ping('1.1.1.1')
        >>> host.avg_rtt
        13.2
        >>> host.is_alive
        True

    See the Host class for details.

    '''
    if is_ipv6_address(address):
        socket = ICMPv6Socket()

    else:
        socket = ICMPv4Socket()

    transmitted_packets = 0
    received_packets = 0

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
            transmitted_packets += 1

            reply = socket.receive()
            reply.raise_for_status()
            received_packets += 1

            round_trip_time = (reply.time - request.time) * 1000
            avg_rtt += round_trip_time
            min_rtt  = min(round_trip_time, min_rtt)
            max_rtt  = max(round_trip_time, max_rtt)

            if reply.ttl is not None:
                ttl = reply.ttl

            if sequence < count - 1:
                sleep(interval)

        except ICMPLibError:
            pass

    if received_packets:
        avg_rtt /= received_packets

    else:
        min_rtt = 0.0

    host = Host(
        address=address,
        min_rtt=min_rtt,
        avg_rtt=avg_rtt,
        max_rtt=max_rtt,
        transmitted_packets=transmitted_packets,
        received_packets=received_packets,
        ttl=ttl)

    return host


def multiping(addresses, count=2, interval=1, id=PID, max_threads=10,
              **kwargs):
    '''
    Send ICMP ECHO_REQUEST packets to multiple network hosts.

    :type addresses: list of str
    :param addresses: The IP addresses of the gateways or hosts to
        which messages should be sent.

    :type count: int
    :param count: (Optional) The number of ping to perform per address.

    :type interval: int or float
    :param interval: (Optional) The interval in seconds between sending
        each packet.

    :type id: int
    :param id: (Optional) The identifier of the requests. This
        identifier will be incremented by one for each destination.

    :type max_threads: int
    :param max_threads: (Optional) The number of threads allowed to
        speed up processing.

    :param kwargs: Pass to ICMPRequest

    :rtype: list of Host
    :returns: A list of Host objects containing statistics about the
        desired destinations. The list is sorted in the same order as
        the addresses passed in parameters.

    :raises SocketPermissionError: If the permissions are insufficient
        to create a socket.

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

    See the Host class for details.

    '''
    hosts = []
    inactive_threads = []
    active_threads = []

    for i, address in enumerate(addresses):
        thread = PingThread(
            address=address,
            count=count,
            interval=interval,
            id=PID + i,
            **kwargs)

        inactive_threads.append(thread)

    while inactive_threads:
        thread = inactive_threads.pop(0)
        thread.start()
        active_threads.append(thread)

        if (inactive_threads and
            len(active_threads) < max_threads):
            sleep(0.05)
            continue

        while active_threads:
            thread = active_threads.pop(0)
            thread.join()
            hosts.append(thread.host)

    return hosts
