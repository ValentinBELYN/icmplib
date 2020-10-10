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

import socket
from .utils import PLATFORM_WINDOWS


# Fix for Windows
if PLATFORM_WINDOWS:
    socket.IPPROTO_IPV6 = 41


class IPSocket:
    def __init__(self, family, protocol):
        self._socket = socket.socket(
            family=family,
            type=socket.SOCK_RAW,
            proto=protocol)

        self.timeout = 5
        self.ttl = 64
        self.traffic_class = 0

    def send(self, payload, address, port):
        return self._socket.sendto(payload, (address, port))

    def receive(self, buffer_size=1024):
        packet = self._socket.recvfrom(buffer_size)

        payload = packet[0]
        address = packet[1][0]
        port = packet[1][1]

        return payload, address, port

    def close(self):
        self._socket.close()

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._socket.settimeout(timeout)
        self._timeout = timeout

    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    def ttl(self, ttl):
        self._ttl = ttl

    @property
    def traffic_class(self):
        return self._traffic_class

    @traffic_class.setter
    def traffic_class(self, traffic_class):
        self._traffic_class = traffic_class


class IPv4Socket(IPSocket):
    def __init__(self, protocol):
        super().__init__(
            family=socket.AF_INET,
            protocol=protocol)

        self._broadcast = False

    @IPSocket.ttl.setter
    def ttl(self, ttl):
        self._ttl = ttl

        self._socket.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_TTL,
            ttl)

    @IPSocket.traffic_class.setter
    def traffic_class(self, traffic_class):
        self._traffic_class = traffic_class

        if not PLATFORM_WINDOWS:
            self._socket.setsockopt(
                socket.IPPROTO_IP,
                socket.IP_TOS,
                traffic_class)

    @property
    def broadcast(self):
        return self._broadcast

    @broadcast.setter
    def broadcast(self, allow):
        self._broadcast = allow

        self._socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_BROADCAST,
            allow)


class IPv6Socket(IPSocket):
    def __init__(self, protocol):
        super().__init__(
            family=socket.AF_INET6,
            protocol=protocol)

    @IPSocket.ttl.setter
    def ttl(self, ttl):
        self._ttl = ttl

        self._socket.setsockopt(
            socket.IPPROTO_IPV6,
            socket.IPV6_MULTICAST_HOPS,
            ttl)

    @IPSocket.traffic_class.setter
    def traffic_class(self, traffic_class):
        self._traffic_class = traffic_class

        if not PLATFORM_WINDOWS:
            self._socket.setsockopt(
                socket.IPPROTO_IPV6,
                socket.IPV6_TCLASS,
                traffic_class)
