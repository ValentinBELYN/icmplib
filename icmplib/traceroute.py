'''
    icmplib
    ~~~~~~~

    A powerful library for forging ICMP packets and performing ping
    and traceroute.

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


def traceroute(address, count=2, interval=0.05, timeout=2, id=PID,
        first_hop=1, max_hops=30, source=None, fast=False, **kwargs):
    '''
    Determine the route to a destination host.

    The Internet is a large and complex aggregation of network hardware,
    connected together by gateways. Tracking the route one's packets
    follow can be difficult. This function uses the IP protocol time to
    live field and attempts to elicit an ICMP Time Exceeded response
    from each gateway along the path to some host.

    This function requires root privileges to run.

    :type address: str
    :param address: The IP address, hostname or FQDN of the host to
        reach. For deterministic behavior, prefer to use an IP address.

    :type count: int, optional
    :param count: The number of ping to perform per hop. Default to 2.

    :type interval: int or float, optional
    :param interval: The interval in seconds between sending each
        packet. Default to 0.05.

    :type timeout: int or float, optional
    :param timeout: The maximum waiting time for receiving a reply in
        seconds. Default to 2.

    :type id: int, optional
    :param id: The identifier of ICMP requests. Used to match the
        responses with requests. In practice, a unique identifier
        should be used for every traceroute process. By default, the
        identifier corresponds to the PID.

    :type first_hop: int, optional
    :param first_hop: The initial time to live value used in outgoing
        probe packets. Default to 1.

    :type max_hops: int, optional
    :param max_hops: The maximum time to live (max number of hops) used
        in outgoing probe packets. Default to 30.

    :type source: str, optional
    :param source: The IP address from which you want to send packets.
        By default, the interface is automatically chosen according to
        the specified destination.

    :type fast: bool, optional
    :param fast: When this option is enabled and an intermediate router
        has been reached, skip to the next hop rather than perform
        additional requests. The `count` parameter then becomes the
        maximum number of requests in the event of no response.
        Default to False.

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

    :rtype: list of Hop
    :returns: A list of `Hop` objects representing the route to the
        desired destination. The list is sorted in ascending order
        according to the distance, in terms of hops, that separates the
        remote host from the current machine. Gateways that do not
        respond to requests are not added to this list.

    :raises NameLookupError: If you pass a hostname or FQDN in
        parameters and it does not exist or cannot be resolved.
    :raises SocketPermissionError: If the privileges are insufficient
        to create the socket.
    :raises SocketAddressError: If the source address cannot be
        assigned to the socket.
    :raises ICMPSocketError: If another error occurs. See the
        `ICMPv4Socket` or `ICMPv6Socket` class for details.

    Usage::

        >>> from icmplib import traceroute
        >>> hops = traceroute('1.1.1.1')
        >>> last_distance = 0

        >>> for hop in hops:
        ...     if last_distance + 1 != hop.distance:
        ...         print('Some gateways are not responding')
        ...
        ...     print(f'{hop.distance} {hop.address} {hop.avg_rtt} ms')
        ...
        ...     last_distance = hop.distance
        ...
        1       10.0.0.1            5.196 ms
        2       194.149.169.49      7.552 ms
        3       194.149.166.54      12.21 ms
        *       Some gateways are not responding
        5       212.73.205.22       22.15 ms
        6       1.1.1.1             13.59 ms

    See the `Hop` class for details.

    '''
    address = resolve(address)

    if is_ipv6_address(address):
        sock = ICMPv6Socket(source)

    else:
        sock = ICMPv4Socket(source)

    ttl = first_hop
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
                ttl=ttl,
                **kwargs)

            try:
                sock.send(request)
                packets_sent += 1

                reply = sock.receive(request, timeout)
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

            if fast:
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

    sock.close()

    return hops
