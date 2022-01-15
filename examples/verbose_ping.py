'''
    icmplib
    ~~~~~~~

    The power to forge ICMP packets and do ping and traceroute.

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2022 Valentin BELYN.
    :license: GNU LGPLv3, see the LICENSE for details.

    ~~~~~~~

    Example: verbose ping (advanced)

    PING 1.1.1.1: 56 data bytes

        64 bytes from 1.1.1.1: icmp_seq=0 time=12.061 ms
        64 bytes from 1.1.1.1: icmp_seq=1 time=12.597 ms
        64 bytes from 1.1.1.1: icmp_seq=2 time=12.475 ms
        64 bytes from 1.1.1.1: icmp_seq=3 time=10.822 ms

    Completed.
'''

from time import sleep

from icmplib import ICMPv4Socket, ICMPv6Socket, ICMPRequest
from icmplib import ICMPLibError, ICMPError, TimeoutExceeded
from icmplib import PID, is_ipv6_address


def verbose_ping(address, count=4, interval=1, timeout=2, id=PID):
    # A payload of 56 bytes is used by default. You can modify it using
    # the 'payload_size' parameter of your ICMP request.
    print(f'PING {address}: 56 data bytes\n')

    # We detect the socket to use from the specified IP address
    if is_ipv6_address(address):
        sock = ICMPv6Socket()
    else:
        sock = ICMPv4Socket()

    for sequence in range(count):
        # We create an ICMP request
        request = ICMPRequest(
            destination=address,
            id=id,
            sequence=sequence)

        try:
            # We send the request
            sock.send(request)

            # We are awaiting receipt of an ICMP reply
            reply = sock.receive(request, timeout)

            # We received a reply
            # We display some information
            print(f'  {reply.bytes_received} bytes from '
                  f'{reply.source}: ', end='')

            # We throw an exception if it is an ICMP error message
            reply.raise_for_status()

            # We calculate the round-trip time and we display it
            round_trip_time = (reply.time - request.time) * 1000

            print(f'icmp_seq={sequence} '
                  f'time={round(round_trip_time, 3)} ms')

            # We wait before continuing
            if sequence < count - 1:
                sleep(interval)

        except TimeoutExceeded:
            # The timeout has been reached
            print(f'  Request timeout for icmp_seq {sequence}')

        except ICMPError as err:
            # An ICMP error message has been received
            print(err)

        except ICMPLibError:
            # All other errors
            print('  An error has occurred.')

    print('\nCompleted.')


verbose_ping('1.1.1.1')
