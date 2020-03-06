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

from .ip import IPv4Socket, IPv6Socket
from .models import ICMPRequest, ICMPReply
from .exceptions import *
from .utils import random_byte_message

import socket
from struct import pack, unpack
from time import time


#   Echo Request and Echo Reply messages -- RFC 792 / 4443
#
#      0                   1                   2                   3
#      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#     |     Type      |     Code      |           Checksum            |
#     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#     |           Identifier          |        Sequence Number        |
#     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#     |     Data ...
#     +-+-+-+-+-
#
#   ICMPv4 Error message -- RFC 792
#
#      0                   1                   2                   3
#      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#     |     Type      |     Code      |           Checksum            |
#     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#     |                 Unused / Depends on the error                 |
#     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#     |      Internet Header + 64 bits of Original Data Datagram      |
#     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
#   ICMPv6 Error message -- RFC 4443
#
#      0                   1                   2                   3
#      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#     |     Type      |     Code      |           Checksum            |
#     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#     |                 Unused / Depends on the error                 |
#     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#     |      Original packet without exceed the minimum IPv6 MTU      |
#     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


class ICMPConfig:
    IP_PROTOCOL          = -1
    IP_SOCKET            = None

    ICMP_HEADER_OFFSET   = -1
    ICMP_CODE_OFFSET     = ICMP_HEADER_OFFSET + 1
    ICMP_CHECKSUM_OFFSET = ICMP_HEADER_OFFSET + 2
    ICMP_ID_OFFSET       = ICMP_HEADER_OFFSET + 4
    ICMP_SEQUENCE_OFFSET = ICMP_HEADER_OFFSET + 6
    ICMP_PAYLOAD_OFFSET  = ICMP_HEADER_OFFSET + 8

    ICMP_ECHO_REQUEST    = -1
    ICMP_ECHO_REPLY      = -1


class ICMPv4Config(ICMPConfig):
    IP_PROTOCOL          = 1
    IP_SOCKET            = IPv4Socket
    IP_TTL_OFFSET        = 8

    ICMP_HEADER_OFFSET   = 20
    ICMP_CODE_OFFSET     = ICMP_HEADER_OFFSET + 1
    ICMP_CHECKSUM_OFFSET = ICMP_HEADER_OFFSET + 2
    ICMP_ID_OFFSET       = ICMP_HEADER_OFFSET + 4
    ICMP_SEQUENCE_OFFSET = ICMP_HEADER_OFFSET + 6
    ICMP_PAYLOAD_OFFSET  = ICMP_HEADER_OFFSET + 8

    ICMP_ECHO_REQUEST    = 8
    ICMP_ECHO_REPLY      = 0


class ICMPv6Config(ICMPConfig):
    IP_PROTOCOL          = 58
    IP_SOCKET            = IPv6Socket
    IP_TTL_OFFSET        = -1

    ICMP_HEADER_OFFSET   = 0
    ICMP_CODE_OFFSET     = ICMP_HEADER_OFFSET + 1
    ICMP_CHECKSUM_OFFSET = ICMP_HEADER_OFFSET + 2
    ICMP_ID_OFFSET       = ICMP_HEADER_OFFSET + 4
    ICMP_SEQUENCE_OFFSET = ICMP_HEADER_OFFSET + 6
    ICMP_PAYLOAD_OFFSET  = ICMP_HEADER_OFFSET + 8

    ICMP_ECHO_REQUEST    = 128
    ICMP_ECHO_REPLY      = 129


class ICMPSocket:
    '''
    Base class for ICMP sockets.

    :type config: ICMPConfig
    :param config: The ICMP socket configuration used to create and
        read ICMP packets.

    :raises SocketPermissionError: If the permissions are insufficient
        to create the socket.

    '''
    def __init__(self, config):
        self._config = config
        self._last_request = None

        try:
            self._socket = config.IP_SOCKET(
                config.IP_PROTOCOL)

        except OSError:
            raise SocketPermissionError

    def __del__(self):
        '''
        Call the close() method.

        '''
        self.close()

    def _create_header(self, type, code, checksum, id, sequence):
        '''
        Create the ICMP header of a packet.

        '''
        # ICMP type:   8 bits (B)
        # ICMP code:   8 bits (B)
        # Checksum:   16 bits (H)
        # Identifier: 16 bits (H)
        # Sequence:   16 bits (H)
        return pack('!BBHHH', type, code, checksum, id, sequence)

    def _checksum(self, data):
        '''
        Calculate the checksum of a packet.

        '''
        end = len(data) - 1
        sum = 0

        for i in range(0, end, 2):
            sum += (data[i] << 8) + data[i + 1]
            sum  = (sum >> 16) + (sum & 0xffff)

        sum = ~sum & 0xffff

        return sum

    def _create_packet(self, id, sequence, payload):
        '''
        Create a packet.

        '''
        type = self._config.ICMP_ECHO_REQUEST

        # Temporary header to calculate the checksum
        header = self._create_header(type, 0, 0, id, sequence)
        checksum = self._checksum(header + payload)

        # Definitive header
        header = self._create_header(type, 0, checksum, id, sequence)

        return header + payload

    def _read_reply(self, packet, source, reply_time):
        '''
        Read a reply from bytes and return an ICMPReply object.

        '''
        received_bytes = (
            len(packet)
            - self._config.ICMP_HEADER_OFFSET)

        if self._config.IP_TTL_OFFSET > 0:
            ttl = packet[self._config.IP_TTL_OFFSET]
        else:
            ttl = None

        type, code = unpack('!BB', packet[
            self._config.ICMP_HEADER_OFFSET:
            self._config.ICMP_CHECKSUM_OFFSET])

        if type != self._config.ICMP_ECHO_REPLY:
            packet = packet[self._config.ICMP_PAYLOAD_OFFSET:]

        id, sequence = unpack('!HH', packet[
            self._config.ICMP_ID_OFFSET:
            self._config.ICMP_PAYLOAD_OFFSET
        ])

        reply = ICMPReply(
            source=source,
            id=id,
            sequence=sequence,
            type=type,
            code=code,
            received_bytes=received_bytes,
            time=reply_time,
            ttl=ttl)

        return reply

    def send(self, request):
        '''
        Send a request to a host.

        This operation is non-blocking. Use the receive() method to get
        the reply.

        :type request: ICMPRequest
        :param request: The ICMP request you have created.

        :raises SocketBroadcastError: If a broadcast address is used
            and the corresponding option is not enabled on the socket
            (ICMPv4 only).
        :raises ICMPSocketError: If another error occurs while sending.

        '''
        if request.payload is None:
            payload = random_byte_message(request.payload_size)
        else:
            payload = request.payload

        packet = self._create_packet(
            id=request.id,
            sequence=request.sequence,
            payload=payload)

        self._socket.ttl = request.ttl

        request.time = time()

        try:
            self._socket.send(
                packet=packet,
                address=request.destination,
                port=0)

            self._last_request = request

        except PermissionError:
            raise SocketBroadcastError

        except OSError as err:
            raise ICMPSocketError(str(err))

    def receive(self):
        '''
        Receive a reply from a host.

        This method can be called multiple times if you expect several
        responses (as with a broadcast address).

        :raises TimeoutExceeded: If no response is received before the
            timeout defined in the request.
            This exception is also useful for stopping a possible loop
            in case of multiple responses.
        :raises ICMPSocketError: If another error occurs while
            receiving.

        :rtype: ICMPReply
        :returns: An ICMPReply object containing the reply of the
            desired destination.

        See the ICMPReply class for details.

        '''
        if not self._last_request:
            raise TimeoutExceeded(0)

        request = self._last_request

        current_time = time()
        self._socket.timeout = request.timeout
        timeout = current_time + request.timeout

        try:
            while True:
                packet, address, port = self._socket.receive()
                reply_time = time()

                if reply_time > timeout:
                    raise socket.timeout

                reply = self._read_reply(
                    packet=packet,
                    source=address,
                    reply_time=reply_time)

                if (request.id == reply.id and
                    request.sequence == reply.sequence):
                    return reply

        except socket.timeout:
            raise TimeoutExceeded(request.timeout)

        except OSError as err:
            raise ICMPSocketError(str(err))

    def close(self):
        '''
        Close the socket. It cannot be used after this call.

        '''
        self._socket.close()


class ICMPv4Socket(ICMPSocket):
    '''
    Socket for sending and receiving ICMPv4 packets.

    :raises SocketPermissionError: If the permissions are insufficient
        to create the socket.

    '''
    def __init__(self):
        super().__init__(ICMPv4Config)

    @property
    def broadcast(self):
        '''
        Indicate whether broadcast support is enabled on the socket.
        Return a boolean.

        .. note::
           To enable broadcast support:
           icmp_socket.broadcast = True

        '''
        return self._socket.broadcast

    @broadcast.setter
    def broadcast(self, allow):
        self._socket.broadcast = allow


class ICMPv6Socket(ICMPSocket):
    '''
    Socket for sending and receiving ICMPv6 packets.

    :raises SocketPermissionError: If the permissions are insufficient
        to create the socket.

    '''
    def __init__(self):
        super().__init__(ICMPv6Config)
