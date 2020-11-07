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

from .exceptions import *


class ICMPRequest:
    '''
    A user-created object that represents an ICMP Echo Request.

    :type destination: str
    :param destination: The IP address of the host to which the message
        should be sent.

    :type id: int
    :param id: The identifier of the request. Used to match the reply
        with the request. In practice, a unique identifier is used for
        every ping process. On Linux, this identifier is automatically
        replaced if the request is sent from an unprivileged socket.

    :type sequence: int
    :param sequence: The sequence number. Used to match the reply with
        the request. Typically, the sequence number is incremented for
        each packet sent during the process.

    :type payload: bytes, optional
    :param payload: The payload content in bytes. A random payload is
        used by default.

    :type payload_size: int, optional
    :param payload_size: The payload size. Ignored when the `payload`
        parameter is set. Default to 56.

    :type ttl: int, optional
    :param ttl: The time to live of the packet in terms of hops.
        Default to 64.

    :type traffic_class: int, optional
    :param traffic_class: The traffic class of the packet.
        Provides a defined level of service to the packet by setting
        the DS Field (formerly TOS) or the Traffic Class field of the
        IP header. Packets are delivered with the minimum priority by
        default (Best-effort delivery).
        Intermediate routers must be able to support this feature.
        Only available on Unix systems. Ignored on Windows.

    '''
    def __init__(self, destination, id, sequence, payload=None,
            payload_size=56, ttl=64, traffic_class=0):

        if payload:
            payload_size = len(payload)

        self._destination = destination
        self._id = id & 0xffff
        self._sequence = sequence & 0xffff
        self._payload = payload
        self._payload_size = payload_size
        self._ttl = ttl
        self._traffic_class = traffic_class
        self._time = 0

    def __repr__(self):
        return f'<ICMPRequest [{self._destination}]>'

    @property
    def destination(self):
        '''
        The IP address of the host to which the message should be sent.

        '''
        return self._destination

    @property
    def id(self):
        '''
        The identifier of the request.
        Used to match the reply with the request.

        '''
        return self._id

    @property
    def sequence(self):
        '''
        The sequence number.
        Used to match the reply with the request.

        '''
        return self._sequence

    @property
    def payload(self):
        '''
        The payload content in bytes.
        Return `None` if the payload is random.

        '''
        return self._payload

    @property
    def payload_size(self):
        '''
        The payload size.

        '''
        return self._payload_size

    @property
    def ttl(self):
        '''
        The time to live of the packet in terms of hops.

        '''
        return self._ttl

    @property
    def traffic_class(self):
        '''
        The traffic class of the packet.

        '''
        return self._traffic_class

    @property
    def time(self):
        '''
        The timestamp of the ICMP request.

        Initialized to zero when creating the request and replaced by
        the `send` method of `ICMPv4Socket` or `ICMPv6Socket` with the
        time of sending.

        '''
        return self._time


class ICMPReply:
    '''
    A class that represents an ICMP reply. Generated from an ICMP
    socket (`ICMPv4Socket` or `ICMPv6Socket`).

    :type source: str
    :param source: The IP address of the gateway or host that composes
        the ICMP message.

    :type id: int
    :param id: The identifier of the reply. Used to match the reply
        with the request.

    :type sequence: int
    :param sequence: The sequence number. Used to match the reply with
        the request.

    :type type: int
    :param type: The type of ICMP message.

    :type code: int
    :param code: The ICMP error code.

    :type bytes_received: int
    :param bytes_received: The number of bytes received.

    :type time: float
    :param time: The timestamp of the ICMP reply.

    '''
    def __init__(self, source, id, sequence, type, code,
            bytes_received, time):

        self._source = source
        self._id = id
        self._sequence = sequence
        self._type = type
        self._code = code
        self._bytes_received = bytes_received
        self._time = time

    def __repr__(self):
        return f'<ICMPReply [{self._source}]>'

    def raise_for_status(self):
        '''
        Throw an exception if the reply is not an ICMP Echo Reply.
        Otherwise, do nothing.

        :raises DestinationUnreachable: If the destination is
            unreachable for some reason.
        :raises TimeExceeded: If the time to live field of the ICMP
            request has reached zero.
        :raises ICMPError: Raised for any other type and ICMP error
            code, except ICMP Echo Reply messages.

        '''
        if ':' in self._source:
            echo_reply_type = 129

            errors = {
                1: ICMPv6DestinationUnreachable,
                3: ICMPv6TimeExceeded
            }

        else:
            echo_reply_type = 0

            errors = {
                3: ICMPv4DestinationUnreachable,
               11: ICMPv4TimeExceeded
            }

        if self._type in errors:
            raise errors[self._type](self)

        if self._type != echo_reply_type:
            message = f'Error type: {self._type}, ' \
                      f'code: {self._code}'

            raise ICMPError(message, self)

    @property
    def source(self):
        '''
        The IP address of the gateway or host that composes the ICMP
        message.

        '''
        return self._source

    @property
    def id(self):
        '''
        The identifier of the reply.
        Used to match the reply with the request.

        '''
        return self._id

    @property
    def sequence(self):
        '''
        The sequence number.
        Used to match the reply with the request.

        '''
        return self._sequence

    @property
    def type(self):
        '''
        The type of ICMP message.

        '''
        return self._type

    @property
    def code(self):
        '''
        The ICMP error code.

        '''
        return self._code

    @property
    def bytes_received(self):
        '''
        The number of bytes received.

        '''
        return self._bytes_received

    @property
    def time(self):
        '''
        The timestamp of the ICMP reply.

        '''
        return self._time


class Host:
    '''
    A class that represents a host. It simplifies the use of the
    results from the `ping`, `multiping` and `traceroute` functions.

    :type address: str
    :param address: The IP address of the gateway or host that
        responded to the request.

    :type min_rtt: float
    :param min_rtt: The minimum round-trip time in milliseconds.

    :type avg_rtt: float
    :param avg_rtt: The average round-trip time in milliseconds.

    :type max_rtt: float
    :param max_rtt: The maximum round-trip time in milliseconds.

    :type packets_sent: int
    :param packets_sent: The number of packets transmitted to the
        destination host.

    :type packets_received: int
    :param packets_received: The number of packets sent by the remote
        host and received by the current host.

    '''
    def __init__(self, address, min_rtt, avg_rtt, max_rtt,
            packets_sent, packets_received):

        self._address = address
        self._min_rtt = round(min_rtt, 3)
        self._avg_rtt = round(avg_rtt, 3)
        self._max_rtt = round(max_rtt, 3)
        self._packets_sent = packets_sent
        self._packets_received = packets_received

    def __repr__(self):
        return f'<Host [{self._address}]>'

    @property
    def address(self):
        '''
        The IP address of the gateway or host that responded to the
        request.

        '''
        return self._address

    @property
    def min_rtt(self):
        '''
        The minimum round-trip time in milliseconds.

        '''
        return self._min_rtt

    @property
    def avg_rtt(self):
        '''
        The average round-trip time in milliseconds.

        '''
        return self._avg_rtt

    @property
    def max_rtt(self):
        '''
        The maximum round-trip time in milliseconds.

        '''
        return self._max_rtt

    @property
    def packets_sent(self):
        '''
        The number of packets transmitted to the destination host.

        '''
        return self._packets_sent

    @property
    def packets_received(self):
        '''
        The number of packets sent by the remote host and received by
        the current host.

        '''
        return self._packets_received

    @property
    def packet_loss(self):
        '''
        Packet loss occurs when packets fail to reach their destination.
        Return a `float` between 0 and 1 (all packets are lost).

        '''
        if not self._packets_sent:
            return 0.0

        packet_loss = 1 - self._packets_received / self._packets_sent

        return round(packet_loss, 3)

    @property
    def is_alive(self):
        '''
        Indicate whether the host is reachable.
        Return a `boolean`.

        '''
        return self._packets_received > 0


class Hop(Host):
    '''
    A class that represents a hop. It extends the `Host` class and adds
    some features for the `traceroute` function.

    :type address: str
    :param address: The IP address of the gateway or host that
        responded to the request.

    :type min_rtt: float
    :param min_rtt: The minimum round-trip time in milliseconds.

    :type avg_rtt: float
    :param avg_rtt: The average round-trip time in milliseconds.

    :type max_rtt: float
    :param max_rtt: The maximum round-trip time in milliseconds.

    :type packets_sent: int
    :param packets_sent: The number of packets transmitted to the
        destination host.

    :type packets_received: int
    :param packets_received: The number of packets sent by the remote
        host and received by the current host.

    :type distance: int
    :param distance: The distance, in terms of hops, that separates the
        remote host from the current machine.

    '''
    def __init__(self, address, min_rtt, avg_rtt, max_rtt,
            packets_sent, packets_received, distance):

        super().__init__(address, min_rtt, avg_rtt, max_rtt,
            packets_sent, packets_received)

        self._distance = distance

    def __repr__(self):
        return f'<Hop {self._distance} [{self._address}]>'

    @property
    def distance(self):
        '''
        The distance, in terms of hops, that separates the remote host
        from the current machine.

        '''
        return self._distance
