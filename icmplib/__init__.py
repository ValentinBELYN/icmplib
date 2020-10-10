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

from .sockets import ICMPv4Socket, ICMPv6Socket
from .models import ICMPRequest, ICMPReply, Host, Hop
from .ping import ping, multiping
from .traceroute import traceroute
from .exceptions import *
from .utils import PID, is_ipv4_address, is_ipv6_address


__author__    = 'Valentin BELYN'
__copyright__ = 'Copyright 2017-2020 Valentin BELYN'
__license__   = 'GNU Lesser General Public License v3.0'

__version__   = '1.2.2'
__build__     = '201010'
