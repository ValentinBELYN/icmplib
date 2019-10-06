'''
    icmplib
    ~~~~~~~

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2019 Valentin BELYN.
    :license: GNU GPLv3, see LICENSE for details.

    ~~~~~~~

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from .utils import is_ipv6_address
from .exceptions import *


class ICMPRequest:
    '''
    A user-created class that represents an ICMP ECHO_REQUEST.

    :type destination: str
    :param destination: The IP address of the gateway or host to which
        the message should be sent.

    :type id: int
    :param id: The identifier of the request. Used to match the reply
        with the request. In practice, a unique identifier is used for
        every ping process.

    :type sequence: int
    :param sequence: The sequence number. Used to match the reply with
        the request. Typically, the sequence number is incremented for
        each packet sent during the process.

    :type payload_size: int
    :param payload_size: (Optional) The payload size in bytes.

    :type timeout: int or float
    :param timeout: (Optional) The maximum waiting time for receiving
        the reply in seconds.

    :type ttl: int
    :param ttl: (Optional) The time to live of the packet in seconds.

    '''
    def __init__(self, destination, id, sequence, payload_size=56,
            timeout=2, ttl=64):

        id &= 0xffff
        sequence &= 0xffff

        self._destination = destination
        self._id = id
        self._sequence = sequence
        self._payload_size = payload_size
        self._timeout = timeout
        self._ttl = ttl
        self._time = 0

    def __repr__(self):
        return f'<ICMPRequest [{self._destination}]>'

    @property
    def destination(self):
        '''
        The IP address of the gateway or host to which the message
        should be sent.

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
    def payload_size(self):
        '''
        The payload size.

        '''
        return self._payload_size

    @property
    def timeout(self):
        '''
        The maximum waiting time for receiving the reply in seconds.

        '''
        return self._timeout

    @property
    def ttl(self):
        '''
        The time to live of the packet in seconds.

        '''
        return self._ttl

    @property
    def time(self):
        '''
        The timestamp of the ICMP request.
        Initialized to zero when creating the request and replaced by
        ICMPv4Socket or ICMPv6Socket with the time of sending.

        '''
        return self._time

    @time.setter
    def time(self, time):
        self._time = time


class ICMPReply:
    '''
    A class that represents an ICMP reply. Generated from an ICMPSocket
    object (ICMPv4Socket or ICMPv6Socket).

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
    :param type: The type of message.

    :type code: int
    :param code: The error code.

    :type received_bytes: int
    :param received_bytes: The number of bytes received.

    :type time: float
    :param time: The timestamp of the ICMP reply.

    '''
    def __init__(self, source, id, sequence, type, code,
            received_bytes, time):

        self._source = source
        self._id = id
        self._sequence = sequence
        self._type = type
        self._code = code
        self._received_bytes = received_bytes
        self._time = time

    def __repr__(self):
        return f'<ICMPReply [{self._source}]>'

    def raise_for_status(self):
        '''
        Throw an exception if the reply is not an ICMP ECHO_REPLY.
        Otherwise, do nothing.

        :raises ICMPv4DestinationUnreachable: If the ICMPv4 reply is
            type 3.
        :raises ICMPv4TimeExceeded: If the ICMPv4 reply is type 11.
        :raises ICMPv6DestinationUnreachable: If the ICMPv6 reply is
            type 1.
        :raises ICMPv6TimeExceeded: If the ICMPv6 reply is type 3.
        :raises ICMPError: If the reply is of another type and is not
            an ICMP ECHO_REPLY.

        '''
        ipv4_errors = {
            3:  ICMPv4DestinationUnreachable,
            11: ICMPv4TimeExceeded
        }

        ipv6_errors = {
            1:  ICMPv6DestinationUnreachable,
            3:  ICMPv6TimeExceeded
        }

        if is_ipv6_address(self._source):
            expected_type = 129
            errors = ipv6_errors

        else:
            expected_type = 0
            errors = ipv4_errors

        if self._type in errors:
            raise errors[self._type](self)

        if self._type != expected_type:
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
    def type(self):
        '''
        The type of message.

        '''
        return self._type

    @property
    def code(self):
        '''
        The error code.

        '''
        return self._code

    @property
    def received_bytes(self):
        '''
        The number of bytes received.

        '''
        return self._received_bytes

    @property
    def time(self):
        '''
        The timestamp of the ICMP reply.

        '''
        return self._time


class Host:
    '''
    A class that represents a host. Simplifies the exploitation of
    results from ping and traceroute functions.

    :type address: str
    :param address: The IP address of the gateway or host that
        responded to the request.

    :type min_rtt: float
    :param min_rtt: The minimum round-trip time.

    :type avg_rtt: float
    :param avg_rtt: The average round-trip time.

    :type max_rtt: float
    :param max_rtt: The maximum round-trip time.

    :type transmitted_packets: int
    :param transmitted_packets: The number of packets transmitted to
        the destination host.

    :type received_packets: int
    :param received_packets: The number of packets sent by the remote
        host and received by the current host.

    '''
    def __init__(self, address, min_rtt, avg_rtt, max_rtt,
            transmitted_packets, received_packets):

        self._address = address
        self._min_rtt = min_rtt
        self._avg_rtt = avg_rtt
        self._max_rtt = max_rtt
        self._transmitted_packets = transmitted_packets
        self._received_packets = received_packets

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
        The minimum round-trip time.

        '''
        return self._min_rtt

    @property
    def avg_rtt(self):
        '''
        The average round-trip time.

        '''
        return self._avg_rtt

    @property
    def max_rtt(self):
        '''
        The maximum round-trip time.

        '''
        return self._max_rtt

    @property
    def transmitted_packets(self):
        '''
        The number of packets transmitted to the destination host.

        '''
        return self._transmitted_packets

    @property
    def received_packets(self):
        '''
        The number of packets sent by the remote host and received by
        the current host.

        '''
        return self._received_packets

    @property
    def packet_loss(self):
        '''
        Packet loss occurs when packets fail to reach their destination.
        Return a float between 0 and 1 (all packets are lost).

        '''
        if not self._transmitted_packets:
            return 0.0

        return (1 - self._received_packets
                  / self._transmitted_packets)

    @property
    def is_alive(self):
        '''
        Return True if the host is reachable, False otherwise.

        '''
        return self.packet_loss < 1


class Hop(Host):
    '''
    A class that represents a hop. It extends the Host class and adds
    some features for traceroute.

    :type address: str
    :param address: The IP address of the gateway or host that
        responded to the request.

    :type min_rtt: float
    :param min_rtt: The minimum round-trip time.

    :type avg_rtt: float
    :param avg_rtt: The average round-trip time.

    :type max_rtt: float
    :param max_rtt: The maximum round-trip time.

    :type transmitted_packets: int
    :param transmitted_packets: The number of packets transmitted to
        the destination host.

    :type received_packets: int
    :param received_packets: The number of packets sent by the remote
        host and received by the current host.

    :type distance: int
    :param distance: The distance (in terms of hops) that separates the
        remote host from the current machine.

    '''
    def __init__(self, address, min_rtt, avg_rtt, max_rtt,
            transmitted_packets, received_packets, distance):

        super().__init__(address, min_rtt, avg_rtt, max_rtt,
            transmitted_packets, received_packets)

        self._distance = distance

    def __repr__(self):
        return f'<Hop {self._distance} [{self._address}]>'

    @property
    def distance(self):
        '''
        The distance (in terms of hops) that separates the remote host
        from the current machine.

        '''
        return self._distance
