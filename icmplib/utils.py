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
from sys import platform
from os import getpid
from re import match
from random import choices


PID = getpid()
PLATFORM_WINDOWS = platform == 'win32'


def random_byte_message(size):
    '''
    Generate a random byte sequence of the specified size.

    '''
    bytes_available = (
        b'abcdefghijklmnopqrstuvwxyz'
        b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        b'1234567890'
    )

    return bytes(
        choices(bytes_available, k=size)
    )


def resolve(name):
    '''
    Resolve a hostname or FQDN into an IP address. If several IP
    addresses are available, only the first one is returned.

    This function searches for IPv4 addresses first for compatibility
    reasons before searching for IPv6 addresses.

    If no address is found, the name specified in parameter is
    returned so as not to impact the operation of other functions. This
    behavior may change in future versions of icmplib.

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
        return name


def is_ipv4_address(address):
    '''
    Indicate whether the specified address is an IPv4 address.
    Return a `boolean`.

    '''
    return match(
        r'^([0-9]{1,3}[.]){3}[0-9]{1,3}$',
        address
    ) is not None


def is_ipv6_address(address):
    '''
    Indicate whether the specified address is an IPv6 address.
    Return a `boolean`.

    '''
    return ':' in address
