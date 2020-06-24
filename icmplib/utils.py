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

from os import getpid
from random import choice


PID = getpid()


def random_byte_message(size):
    '''
    Generate a random byte sequence of the specified size.

    '''
    bytes_available = (
        b'abcdefghijklmnopqrstuvwxyz'
        b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        b'1234567890'
    )

    sequence = [
        choice(bytes_available)
        for _ in range(size)
    ]

    return bytes(sequence)


def is_ipv6_address(address):
    '''
    Take an IP address and indicate whether it is an IPv6 address or
    not. Return a `boolean`.

    '''
    return ':' in address
