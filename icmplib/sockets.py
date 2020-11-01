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

import socket

from struct import pack, unpack
from time import time

from .models import ICMPRequest, ICMPReply
from .exceptions import *
from .utils import *


class ICMPSocket:
    _ICMP_HEADER_OFFSET   = -1
    _ICMP_CODE_OFFSET     = _ICMP_HEADER_OFFSET + 1
    _ICMP_CHECKSUM_OFFSET = _ICMP_HEADER_OFFSET + 2
    _ICMP_ID_OFFSET       = _ICMP_HEADER_OFFSET + 4
    _ICMP_SEQUENCE_OFFSET = _ICMP_HEADER_OFFSET + 6
    _ICMP_PAYLOAD_OFFSET  = _ICMP_HEADER_OFFSET + 8

    _ICMP_ECHO_REQUEST    = -1
    _ICMP_ECHO_REPLY      = -1

    def __init__(self, address=None, privileged=True):
        self._socket = None
        self._address = address

        # The Linux kernel allows unprivileged users to use datagram
        # sockets (SOCK_DGRAM) to send ICMP requests. This feature is
        # now supported by the majority of Unix systems.
        # Windows is not compatible.
        self._privileged = privileged or PLATFORM_WINDOWS

        try:
            self._socket = self._create_socket(
                socket.SOCK_RAW
                if self._privileged else
                socket.SOCK_DGRAM)

            if address:
                self._socket.bind((address, 0))

        except OSError as err:
            if err.errno == 1:
                raise SocketPermissionError

            if err.errno == 49:
                raise SocketAddressError(address)

            raise ICMPSocketError(str(err))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def _create_socket(self, type):
        raise NotImplementedError

    def _set_ttl(self, ttl):
        raise NotImplementedError

    def _set_traffic_class(self, traffic_class):
        raise NotImplementedError

    def _checksum(self, data):
        sum = 0
        data += b'\x00'

        for i in range(0, len(data) - 1, 2):
            sum += (data[i] << 8) + data[i + 1]
            sum  = (sum & 0xffff) + (sum >> 16)

        sum = ~sum & 0xffff

        return sum

    def _create_packet(self, id, sequence, payload):
        checksum = 0

        # Temporary ICMP header to compute the checksum
        header = pack('!2B3H', self._ICMP_ECHO_REQUEST, 0, checksum,
            id, sequence)

        checksum = self._checksum(header + payload)

        # Definitive ICMP header
        header = pack('!2B3H', self._ICMP_ECHO_REQUEST, 0, checksum,
            id, sequence)

        return header + payload

    def _parse_reply(self, packet, source, time):
        if len(packet) < self._ICMP_CHECKSUM_OFFSET:
            return None

        type, code = unpack('!2B', packet[
            self._ICMP_HEADER_OFFSET:
            self._ICMP_CHECKSUM_OFFSET])

        if type != self._ICMP_ECHO_REPLY:
            packet = packet[self._ICMP_PAYLOAD_OFFSET:]

        if len(packet) < self._ICMP_PAYLOAD_OFFSET:
            return None

        id, sequence = unpack('!2H', packet[
            self._ICMP_ID_OFFSET:
            self._ICMP_PAYLOAD_OFFSET])

        bytes_received = len(packet) - self._ICMP_HEADER_OFFSET

        return ICMPReply(
            source=source,
            id=id,
            sequence=sequence,
            type=type,
            code=code,
            bytes_received=bytes_received,
            time=time)

    def send(self, request):
        if not self._socket:
            raise SocketUnavailableError

        payload = request.payload or \
            random_byte_message(request.payload_size)

        packet = self._create_packet(
            id=request.id,
            sequence=request.sequence,
            payload=payload)

        try:
            self._set_ttl(request.ttl)
            self._set_traffic_class(request.traffic_class)

            request._time = time()
            self._socket.sendto(packet, (request.destination, 0))

            # On Linux, the ICMP request identifier is replaced by the
            # kernel with a random port number when a datagram socket
            # is used (SOCK_DGRAM). So, we update the request created
            # by the user to take this new identifier into account.
            if not self._privileged and PLATFORM_LINUX:
                request._id = self._socket.getsockname()[1]

        except PermissionError:
            raise SocketBroadcastError

        except OSError as err:
            raise ICMPSocketError(str(err))

    def receive(self, request=None, timeout=2):
        if not self._socket:
            raise SocketUnavailableError

        self._socket.settimeout(timeout)
        time_limit = time() + timeout

        try:
            while True:
                response = self._socket.recvfrom(1024)
                current_time = time()

                packet = response[0]
                source = response[1][0]

                if current_time > time_limit:
                    raise socket.timeout

                # On Linux, the IP header is missing when a datagram
                # socket is used (SOCK_DGRAM). To keep the same
                # behavior on all operating systems including macOS
                # which has this header, we add a padding of the size
                # of the missing IP header.
                if not self._privileged and PLATFORM_LINUX:
                    padding = b'\x00' * self._ICMP_HEADER_OFFSET
                    packet = padding + packet

                reply = self._parse_reply(
                    packet=packet,
                    source=source,
                    time=current_time)

                if (reply and not request or
                    reply and request.id == reply.id and
                    request.sequence == reply.sequence):
                    return reply

        except socket.timeout:
            raise TimeoutExceeded(timeout)

        except OSError as err:
            raise ICMPSocketError(str(err))

    def close(self):
        if self._socket:
            self._socket.close()
            self._socket = None

    @property
    def address(self):
        return self._address

    @property
    def is_privileged(self):
        return self._privileged

    @property
    def is_closed(self):
        return self._socket is None


#   Echo Request and Echo Reply messages -- RFC 792
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


class ICMPv4Socket(ICMPSocket):
    _ICMP_HEADER_OFFSET   = 20
    _ICMP_CODE_OFFSET     = _ICMP_HEADER_OFFSET + 1
    _ICMP_CHECKSUM_OFFSET = _ICMP_HEADER_OFFSET + 2
    _ICMP_ID_OFFSET       = _ICMP_HEADER_OFFSET + 4
    _ICMP_SEQUENCE_OFFSET = _ICMP_HEADER_OFFSET + 6
    _ICMP_PAYLOAD_OFFSET  = _ICMP_HEADER_OFFSET + 8

    _ICMP_ECHO_REQUEST    = 8
    _ICMP_ECHO_REPLY      = 0

    def _create_socket(self, type):
        return socket.socket(
            family=socket.AF_INET,
            type=type,
            proto=socket.IPPROTO_ICMP)

    def _set_ttl(self, ttl):
        self._socket.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_TTL,
            ttl)

    def _set_traffic_class(self, traffic_class):
        if PLATFORM_WINDOWS:
            return

        self._socket.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_TOS,
            traffic_class)

    @property
    def broadcast(self):
        return self._socket.getsockopt(
            socket.SOL_SOCKET,
            socket.SO_BROADCAST) > 0

    @broadcast.setter
    def broadcast(self, allow):
        self._socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_BROADCAST,
            allow)


#   Echo Request and Echo Reply messages -- RFC 4443
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

# Windows IPv6 compatibility
if PLATFORM_WINDOWS:
    socket.IPPROTO_IPV6 = 41


class ICMPv6Socket(ICMPSocket):
    _ICMP_HEADER_OFFSET   = 0
    _ICMP_CODE_OFFSET     = _ICMP_HEADER_OFFSET + 1
    _ICMP_CHECKSUM_OFFSET = _ICMP_HEADER_OFFSET + 2
    _ICMP_ID_OFFSET       = _ICMP_HEADER_OFFSET + 4
    _ICMP_SEQUENCE_OFFSET = _ICMP_HEADER_OFFSET + 6
    _ICMP_PAYLOAD_OFFSET  = _ICMP_HEADER_OFFSET + 8

    _ICMP_ECHO_REQUEST    = 128
    _ICMP_ECHO_REPLY      = 129

    def _create_socket(self, type):
        return socket.socket(
            family=socket.AF_INET6,
            type=type,
            proto=socket.IPPROTO_ICMPV6)

    def _set_ttl(self, ttl):
        self._socket.setsockopt(
            socket.IPPROTO_IPV6,
            socket.IPV6_MULTICAST_HOPS,
            ttl)

    def _set_traffic_class(self, traffic_class):
        if PLATFORM_WINDOWS:
            return

        self._socket.setsockopt(
            socket.IPPROTO_IPV6,
            socket.IPV6_TCLASS,
            traffic_class)
