'''
    icmplib
    ~~~~~~~

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

from time import sleep

from .sockets import ICMPv4Socket, ICMPv6Socket
from .models import ICMPRequest, Hop
from .exceptions import *
from .utils import PID, resolve, is_ipv6_address


def traceroute(address, count=3, interval=0.05, timeout=2, id=PID,
        traffic_class=0, max_hops=30, fast_mode=False, **kwargs):
    '''
    Determine the route to a destination host.

    The Internet is a large and complex aggregation of network hardware,
    connected together by gateways. Tracking the route one's packets
    follow can be difficult. This function utilizes the IP protocol
    time to live field and attempts to elicit an ICMP TIME_EXCEEDED
    response from each gateway along the path to some host.

    :type address: str
    :param address: The destination IP address.

    :type count: int
    :param count: (Optional) The number of ping to perform per hop.

    :type interval: int or float
    :param interval: (Optional) The interval in seconds between sending
        each packet.

    :type timeout: int or float
    :param timeout: (Optional) The maximum waiting time for receiving
        a reply in seconds.

    :type id: int
    :param id: (Optional) The identifier of the request. Used to match
        the reply with the request. In practice, a unique identifier is
        used for every ping process.

    :type traffic_class: int
    :param traffic_class: (Optional) The traffic class of packets.
        Provides a defined level of service to packets by setting the
        DS Field (formerly TOS) or the Traffic Class field of IP
        headers. Packets are delivered with the minimum priority by
        default (Best-effort delivery).
        Intermediate routers must be able to support this feature.
        Only available on Unix systems. Ignored on Windows.

    :type max_hops: int
    :param max_hops: (Optional) The maximum time to live (max number of
        hops) used in outgoing probe packets.

    :type fast_mode: bool
    :param fast_mode: (Optional) When this option is enabled and an
        intermediate router has been reached, skip to the next hop
        rather than perform additional requests. The `count` parameter
        then becomes the maximum number of requests in case of no
        responses.

    :param **kwargs: (Optional) Advanced use: arguments passed to
        `ICMPRequest` objects.

    :rtype: list of Hop
    :returns: A list of `Hop` objects representing the route to the
        desired host. The list is sorted in ascending order according
        to the distance (in terms of hops) that separates the remote
        host from the current machine.

    :raises SocketPermissionError: If the permissions are insufficient
        to create a socket.

    Usage::

        >>> from icmplib import traceroute
        >>> hops = traceroute('1.1.1.1')
        >>> last_distance = 0

        >>> for hop in hops:
        ...     if last_distance + 1 != hop.distance:
        ...         print('Some routers are not responding')
        ...
        ...     print(f'{hop.distance} {hop.address} {hop.avg_rtt} ms')
        ...
        ...     last_distance = hop.distance
        ...
        1       10.0.0.1             5.196 ms
        2       194.149.169.49       7.552 ms
        3       194.149.166.54       12.21 ms
        *       Some routers are not responding
        5       212.73.205.22        22.15 ms
        6       1.1.1.1              13.59 ms

    See the `Hop` class for details.

    '''
    address = resolve(address)

    if is_ipv6_address(address):
        socket = ICMPv6Socket()

    else:
        socket = ICMPv4Socket()

    ttl = 1
    host_reached = False
    hops = []

    while not host_reached and ttl <= max_hops:
        hop_address = None
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
                timeout=timeout,
                ttl=ttl,
                traffic_class=traffic_class,
                **kwargs)

            try:
                socket.send(request)
                packets_sent += 1

                reply = socket.receive()
                reply.raise_for_status()
                host_reached = True

            except TimeExceeded:
                sleep(interval)

            except ICMPLibError:
                continue

            hop_address = reply.source
            packets_received += 1

            round_trip_time = (reply.time - request.time) * 1000
            avg_rtt += round_trip_time
            min_rtt = min(round_trip_time, min_rtt)
            max_rtt = max(round_trip_time, max_rtt)

            if fast_mode:
                break

        if packets_received:
            avg_rtt /= packets_received

            hop = Hop(
                address=hop_address,
                min_rtt=min_rtt,
                avg_rtt=avg_rtt,
                max_rtt=max_rtt,
                packets_sent=packets_sent,
                packets_received=packets_received,
                distance=ttl)

            hops.append(hop)

        ttl += 1

    socket.close()

    return hops
