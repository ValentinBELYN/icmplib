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

import socket

from threading import Thread, Lock, Event
from struct import pack, unpack
from time import time

from .models import ICMPRequest, ICMPReply
from .exceptions import *
from .utils import *


class ICMPSocket:
    '''
    Base class for ICMP sockets.

    :type address: str, optional
    :param address: The IP address from which you want to listen and
        send packets. By default, the socket listens on all interfaces.

    :type privileged: bool, optional
    :param privileged: When this option is enabled, the socket fully
        manages the exchanges and the structure of the ICMP packets.
        Disable this option if you want to instantiate and use the
        socket without root privileges and let the kernel handle ICMP
        headers. Default to True.
        Only available on Unix systems. Ignored on Windows.

    :raises SocketPermissionError: If the privileges are insufficient
        to create the socket.
    :raises SocketAddressError: If the requested address cannot be
        assigned to the socket.
    :raises ICMPSocketError: If another error occurs while creating the
        socket.

    '''
    _ICMP_HEADER_OFFSET   = -1
    _ICMP_CODE_OFFSET     = _ICMP_HEADER_OFFSET + 1
    _ICMP_CHECKSUM_OFFSET = _ICMP_HEADER_OFFSET + 2
    _ICMP_ID_OFFSET       = _ICMP_HEADER_OFFSET + 4
    _ICMP_SEQUENCE_OFFSET = _ICMP_HEADER_OFFSET + 6
    _ICMP_PAYLOAD_OFFSET  = _ICMP_HEADER_OFFSET + 8

    _ICMP_ECHO_REQUEST    = -1
    _ICMP_ECHO_REPLY      = -1

    def __init__(self, address=None, privileged=True):
        self._sock = None
        self._address = address

        # The Linux kernel allows unprivileged users to use datagram
        # sockets (SOCK_DGRAM) to send ICMP requests. This feature is
        # now supported by the majority of Unix systems.
        # Windows is not compatible.
        self._privileged = privileged or PLATFORM_WINDOWS

        try:
            self._sock = self._create_socket(
                socket.SOCK_RAW if self._privileged else
                socket.SOCK_DGRAM)

            if address:
                self._sock.bind((address, 0))

        except OSError as err:
            if err.errno in (1, 10013):
                raise SocketPermissionError

            if err.errno in (-9, 49, 99, 10049, 11001):
                raise SocketAddressError(address)

            raise ICMPSocketError(str(err))

    def __enter__(self):
        '''
        Return this object.

        '''
        return self

    def __exit__(self, type, value, traceback):
        '''
        Call the `close` method.

        '''
        self.close()

    def __del__(self):
        '''
        Call the `close` method.

        '''
        self.close()

    def _create_socket(self, type):
        '''
        Create and return a new socket. Must be overridden.

        '''
        raise NotImplementedError

    def _set_ttl(self, ttl):
        '''
        Set the time to live of every IP packet originating from this
        socket. Must be overridden.

        '''
        raise NotImplementedError

    def _set_traffic_class(self, traffic_class):
        '''
        Set the DS Field (formerly TOS) or the Traffic Class field of
        every IP packet originating from this socket. Must be
        overridden.

        '''
        raise NotImplementedError

    def _checksum(self, data):
        '''
        Compute the checksum of an ICMP packet. Checksums are used to
        verify the integrity of packets.

        '''
        sum = 0
        data += b'\x00'

        for i in range(0, len(data) - 1, 2):
            sum += (data[i] << 8) + data[i + 1]
            sum  = (sum & 0xffff) + (sum >> 16)

        sum = ~sum & 0xffff

        return sum

    def _create_packet(self, id, sequence, payload):
        '''
        Build an ICMP packet from an identifier, a sequence number and
        a payload.

        This method returns the newly created ICMP header concatenated
        to the payload passed in parameters.

        '''
        checksum = 0

        # Temporary ICMP header to compute the checksum
        header = pack('!2B3H', self._ICMP_ECHO_REQUEST, 0, checksum,
            id, sequence)

        checksum = self._checksum(header + payload)

        # Definitive ICMP header
        header = pack('!2B3H', self._ICMP_ECHO_REQUEST, 0, checksum,
            id, sequence)

        return header + payload

    def _parse_reply(self, packet, source, current_time):
        '''
        Parse an ICMP reply from bytes.

        This method returns an `ICMPReply` object or `None` if the
        reply cannot be parsed.

        '''
        bytes_received = len(packet) - self._ICMP_HEADER_OFFSET

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

        return ICMPReply(
            source=source,
            id=id,
            sequence=sequence,
            type=type,
            code=code,
            bytes_received=bytes_received,
            time=current_time)

    def send(self, request):
        '''
        Send an ICMP request message over the network to a remote host.

        This operation is non-blocking. Use the `receive` method to get
        the reply.

        :type request: ICMPRequest
        :param request: The ICMP request you have created. If the
            socket is used in non-privileged mode on a Linux system,
            the identifier defined in the request will be replaced by
            the kernel.

        :raises SocketBroadcastError: If a broadcast address is used
            and the corresponding option is not enabled on the socket
            (ICMPv4 only).
        :raises SocketUnavailableError: If the socket is closed.
        :raises ICMPSocketError: If another error occurs while sending.

        '''
        if not self._sock:
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
            self._sock.sendto(packet, (request.destination, 0))

            # On Linux, the ICMP request identifier is replaced by the
            # kernel with a random port number when a datagram socket
            # is used (SOCK_DGRAM). So, we update the request created
            # by the user to take this new identifier into account.
            if not self._privileged and PLATFORM_LINUX:
                request._id = self._sock.getsockname()[1]

        except PermissionError:
            raise SocketBroadcastError

        except OSError as err:
            raise ICMPSocketError(str(err))

    def receive(self, request=None, timeout=2):
        '''
        Receive an ICMP reply message from the socket.

        This method can be called multiple times if you expect several
        responses as with a broadcast address.

        :type request: ICMPRequest, optional
        :param request: The ICMP request to use to match the response.
            By default, all ICMP packets arriving on the socket are
            returned.

        :type timeout: int or float, optional
        :param timeout: The maximum waiting time for receiving the
            response in seconds. Default to 2.

        :rtype: ICMPReply
        :returns: An `ICMPReply` object representing the response of
            the desired destination or an upstream gateway. See the
            `ICMPReply` class for details.

        :raises TimeoutExceeded: If no response is received before the
            timeout specified in parameters.
        :raises SocketUnavailableError: If the socket is closed.
        :raises ICMPSocketError: If another error occurs while
            receiving.

        '''
        if not self._sock:
            raise SocketUnavailableError

        self._sock.settimeout(timeout)
        time_limit = time() + timeout

        try:
            while True:
                response = self._sock.recvfrom(1024)
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
                    current_time=current_time)

                if (reply and not request or
                    reply and request.id == reply.id and
                    request.sequence == reply.sequence):
                    return reply

        except socket.timeout:
            raise TimeoutExceeded(timeout)

        except OSError as err:
            raise ICMPSocketError(str(err))

    def close(self):
        '''
        Close the socket. It cannot be used after this call.

        '''
        if self._sock:
            self._sock.close()
            self._sock = None

    @property
    def address(self):
        '''
        The IP address from which the socket listens and sends packets.
        Return `None` if the socket listens on all interfaces.

        '''
        return self._address

    @property
    def is_privileged(self):
        '''
        Indicate whether the socket is running in privileged mode.
        Return a `boolean`.

        '''
        return self._privileged

    @property
    def is_closed(self):
        '''
        Indicate whether the socket is closed.
        Return a `boolean`.

        '''
        return self._sock is None


#   Echo Request and Echo Reply messages                      RFC 792
#
#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |     Type      |     Code      |           Checksum            |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |           Identifier          |        Sequence Number        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |     Data ...
#   +-+-+-+-+-
#
#   ICMPv4 Error message                                      RFC 792
#
#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |     Type      |     Code      |           Checksum            |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                 Unused / Depends on the error                 |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |      Internet Header + 64 bits of Original Data Datagram      |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


class ICMPv4Socket(ICMPSocket):
    '''
    Class for sending and receiving ICMPv4 packets.

    :type address: str, optional
    :param address: The IP address from which you want to listen and
        send packets. By default, the socket listens on all interfaces.

    :type privileged: bool, optional
    :param privileged: When this option is enabled, the socket fully
        manages the exchanges and the structure of the ICMP packets.
        Disable this option if you want to instantiate and use the
        socket without root privileges and let the kernel handle ICMP
        headers. Default to True.
        Only available on Unix systems. Ignored on Windows.

    :raises SocketPermissionError: If the privileges are insufficient
        to create the socket.
    :raises SocketAddressError: If the requested address cannot be
        assigned to the socket.
    :raises ICMPSocketError: If another error occurs while creating the
        socket.

    '''
    _ICMP_HEADER_OFFSET   = 20
    _ICMP_CODE_OFFSET     = _ICMP_HEADER_OFFSET + 1
    _ICMP_CHECKSUM_OFFSET = _ICMP_HEADER_OFFSET + 2
    _ICMP_ID_OFFSET       = _ICMP_HEADER_OFFSET + 4
    _ICMP_SEQUENCE_OFFSET = _ICMP_HEADER_OFFSET + 6
    _ICMP_PAYLOAD_OFFSET  = _ICMP_HEADER_OFFSET + 8

    _ICMP_ECHO_REQUEST    = 8
    _ICMP_ECHO_REPLY      = 0

    def _create_socket(self, type):
        '''
        Create and return a new socket.

        '''
        return socket.socket(
            family=socket.AF_INET,
            type=type,
            proto=socket.IPPROTO_ICMP)

    def _set_ttl(self, ttl):
        '''
        Set the time to live of every IP packet originating from this
        socket.

        '''
        self._sock.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_TTL,
            ttl)

    def _set_traffic_class(self, traffic_class):
        '''
        Set the DS Field (formerly TOS) of every IP packet originating
        from this socket.

        Only available on Unix systems. Ignored on Windows.

        '''
        if PLATFORM_WINDOWS:
            return

        self._sock.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_TOS,
            traffic_class)

    @property
    def broadcast(self):
        '''
        Indicate whether broadcast support is enabled on the socket.
        Return a `boolean`.

        .. note::
           To enable broadcast support:
           icmp_socket.broadcast = True

        '''
        return self._sock.getsockopt(
            socket.SOL_SOCKET,
            socket.SO_BROADCAST) > 0

    @broadcast.setter
    def broadcast(self, allow):
        self._sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_BROADCAST,
            allow)


#   Echo Request and Echo Reply messages                     RFC 4443
#
#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |     Type      |     Code      |           Checksum            |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |           Identifier          |        Sequence Number        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |     Data ...
#   +-+-+-+-+-
#
#   ICMPv6 Error message                                     RFC 4443
#
#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |     Type      |     Code      |           Checksum            |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                 Unused / Depends on the error                 |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |      Original packet without exceed the minimum IPv6 MTU      |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Windows IPv6 compatibility
if PLATFORM_WINDOWS: socket.IPPROTO_IPV6 = 41


class ICMPv6Socket(ICMPSocket):
    '''
    Class for sending and receiving ICMPv6 packets.

    :type address: str, optional
    :param address: The IP address from which you want to listen and
        send packets. By default, the socket listens on all interfaces.

    :type privileged: bool, optional
    :param privileged: When this option is enabled, the socket fully
        manages the exchanges and the structure of the ICMP packets.
        Disable this option if you want to instantiate and use the
        socket without root privileges and let the kernel handle ICMP
        headers. Default to True.
        Only available on Unix systems. Ignored on Windows.

    :raises SocketPermissionError: If the privileges are insufficient
        to create the socket.
    :raises SocketAddressError: If the requested address cannot be
        assigned to the socket.
    :raises ICMPSocketError: If another error occurs while creating the
        socket.

    '''
    _ICMP_HEADER_OFFSET   = 0
    _ICMP_CODE_OFFSET     = _ICMP_HEADER_OFFSET + 1
    _ICMP_CHECKSUM_OFFSET = _ICMP_HEADER_OFFSET + 2
    _ICMP_ID_OFFSET       = _ICMP_HEADER_OFFSET + 4
    _ICMP_SEQUENCE_OFFSET = _ICMP_HEADER_OFFSET + 6
    _ICMP_PAYLOAD_OFFSET  = _ICMP_HEADER_OFFSET + 8

    _ICMP_ECHO_REQUEST    = 128
    _ICMP_ECHO_REPLY      = 129

    def _create_socket(self, type):
        '''
        Create and return a new socket.

        '''
        return socket.socket(
            family=socket.AF_INET6,
            type=type,
            proto=socket.IPPROTO_ICMPV6)

    def _set_ttl(self, ttl):
        '''
        Set the time to live of every IP packet originating from this
        socket.

        '''
        self._sock.setsockopt(
            socket.IPPROTO_IPV6,
            socket.IPV6_MULTICAST_HOPS,
            ttl)

    def _set_traffic_class(self, traffic_class):
        '''
        Set the Traffic Class field of every IP packet originating from
        this socket.

        Only available on Unix systems. Ignored on Windows.

        '''
        if PLATFORM_WINDOWS:
            return

        self._sock.setsockopt(
            socket.IPPROTO_IPV6,
            socket.IPV6_TCLASS,
            traffic_class)


class BufferedSocket:
    '''
    A wrapper for ICMP sockets that reads and classifies incoming ICMP
    packets into a buffer, in real time.

    Useful if you want to send several ICMP packets consecutively
    without waiting for a response between each sending. For this, an
    internal thread is used. It stops automatically when you call the
    `detach` or `close` method.

    This feature is experimental. There is no guarantee that it will be
    retained in future versions.

    :type sock: ICMPSocket
    :param sock: An ICMP socket. Once the wrapper instantiated, this
        socket should no longer be used directly.

    '''
    def __init__(self, sock):
        self._sock = sock
        self._buffer = {}

        self._buffer_event = Event()
        self._buffer_lock = Lock()

        self._thread = Thread(target=self._read_from_socket)
        self._thread.start()

    def __enter__(self):
        '''
        Return this object.

        '''
        return self

    def __exit__(self, type, value, traceback):
        '''
        Call the `close` method.

        '''
        self.close()

    def __del__(self):
        '''
        Call the `close` method.

        '''
        self.close()

    def _read_from_socket(self):
        '''
        Internal thread which retrieves incoming ICMP packets from the
        socket and adds them to a buffer.

        '''
        while self._sock:
            try:
                reply = self._sock.receive(timeout=1)

                with self._buffer_lock:
                    buffer_id = reply.id, reply.sequence

                    if buffer_id not in self._buffer:
                        self._buffer[buffer_id] = []

                    self._buffer[buffer_id].append(reply)
                    self._buffer_event.set()

            except ICMPSocketError:
                pass

    def send(self, request):
        '''
        Send an ICMP request message over the network to a remote host.

        This operation is non-blocking. Use the `receive` method to get
        the reply.

        :type request: ICMPRequest
        :param request: The ICMP request you have created. If the
            underlying socket is used in non-privileged mode on a Linux
            system, the identifier defined in the request will be
            replaced by the kernel.

        :raises SocketBroadcastError: If a broadcast address is used
            and the corresponding option is not enabled on the
            underlying socket (ICMPv4 only).
        :raises SocketUnavailableError: If the socket is closed.
        :raises ICMPSocketError: If another error occurs while sending.

        '''
        if not self._sock:
            raise SocketUnavailableError

        self._sock.send(request)

    def receive(self, request, timeout=2):
        '''
        Retrieve an ICMP reply message from the buffer.

        This method can be called multiple times if you expect several
        responses as with a broadcast address.

        :type request: ICMPRequest
        :param request: The ICMP request to use to match the response.

        :type timeout: int or float, optional
        :param timeout: The maximum waiting time for receiving the
            response in seconds. This parameter takes into account the
            timestamp of the request. Default to 2.

        :rtype: ICMPReply
        :returns: An `ICMPReply` object representing the response of
            the desired destination or an upstream gateway. See the
            `ICMPReply` class for details.

        :raises TimeoutExceeded: If no response is received before the
            timeout specified in parameters.

        '''
        buffer_id = request.id, request.sequence

        while True:
            with self._buffer_lock:
                self._buffer_event.clear()

                if buffer_id in self._buffer:
                    reply = self._buffer[buffer_id].pop(0)

                    if not self._buffer[buffer_id]:
                        del self._buffer[buffer_id]

                    return reply

            remaining_time = request.time + timeout - time()

            if not self._buffer_event.wait(remaining_time):
                raise TimeoutExceeded(timeout)

    def detach(self):
        '''
        Detach the socket from the wrapper and return it. The wrapper
        cannot be used after this call but the socket can be reused for
        other purposes.

        '''
        sock = self._sock

        if self._sock:
            self._sock = None
            self._thread.join()

        return sock

    def close(self):
        '''
        Close this object and the underlying socket. Both cannot be
        used after this call.

        '''
        if self._sock:
            self.detach().close()

    @property
    def is_closed(self):
        '''
        Indicate whether the wrapper is still operational or not.
        Return a `boolean`.

        '''
        return self._sock is None
