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

from sys import platform
from os import getpid
from re import match
from random import choices

from .exceptions import NameLookupError


PID = getpid()
PLATFORM_LINUX   = platform == 'linux'
PLATFORM_MACOS   = platform == 'darwin'
PLATFORM_WINDOWS = platform == 'win32'


def random_byte_message(size):
    '''
    Generate a random byte sequence of the specified size.

    '''
    sequence = choices(
        b'abcdefghijklmnopqrstuvwxyz'
        b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        b'1234567890', k=size)

    return bytes(sequence)


def resolve(name):
    '''
    Resolve a hostname or FQDN into an IP address. If several IP
    addresses are available, only the first one is returned.

    This function searches for IPv4 addresses first for compatibility
    reasons before searching for IPv6 addresses.

    If you pass an IP address, no lookup is done. The same address is
    returned.

    Raises a `NameLookupError` exception if the requested name does
    not exist or cannot be resolved.

    '''
    if is_ipv4_address(name) or is_ipv6_address(name):
        return name

    try:
        return socket.getaddrinfo(
            host=name,
            port=None,
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM
        )[0][4][0]

    except OSError:
        pass

    try:
        return socket.getaddrinfo(
            host=name,
            port=None,
            family=socket.AF_INET6,
            type=socket.SOCK_DGRAM
        )[0][4][0]

    except OSError:
        raise NameLookupError(name)


def is_ipv4_address(address):
    '''
    Indicate whether the specified address is an IPv4 address.
    Return a `boolean`.

    '''
    pattern = r'^([0-9]{1,3}[.]){3}[0-9]{1,3}$'
    return match(pattern, address) is not None


def is_ipv6_address(address):
    '''
    Indicate whether the specified address is an IPv6 address.
    Return a `boolean`.

    '''
    return ':' in address
