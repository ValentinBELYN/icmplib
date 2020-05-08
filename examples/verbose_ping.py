'''
    icmplib
    ~~~~~~~

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2020 Valentin BELYN.
    :license: GNU LGPLv3, see the LICENSE for details.

    ~~~~~~~

    Example: verbose ping (advanced)

    PING 1.1.1.1: 56 data bytes

        64 bytes from 1.1.1.1: icmp_seq=0 time=12.06 ms
        64 bytes from 1.1.1.1: icmp_seq=1 time=12.59 ms
        64 bytes from 1.1.1.1: icmp_seq=2 time=12.47 ms
        64 bytes from 1.1.1.1: icmp_seq=3 time=10.82 ms
'''

from icmplib import (
    ICMPv4Socket,
    ICMPv6Socket,
    ICMPRequest,
    TimeoutExceeded,
    ICMPError,
    ICMPLibError,
    is_ipv6_address,
    PID)

from time import sleep


def verbose_ping(address, count=4, interval=1, timeout=2, id=PID):
    # ICMPRequest uses a payload of 56 bytes by default
    # You can modify it using the payload_size parameter
    print(f'PING {address}: 56 data bytes')

    # Detection of the socket to use
    if is_ipv6_address(address):
        socket = ICMPv6Socket()

    else:
        socket = ICMPv4Socket()

    for sequence in range(count):
        # We create an ICMP request
        request = ICMPRequest(
            destination=address,
            id=id,
            sequence=sequence,
            timeout=timeout)

        try:
            # We send the request
            socket.send(request)

            # We are awaiting receipt of an ICMP reply
            reply = socket.receive()

            # We received a reply
            # We display some information
            print(f'{reply.received_bytes} bytes from '
                  f'{reply.source}: ', end='')

            # We throw an exception if it is an ICMP error message
            reply.raise_for_status()

            # We calculate the round-trip time and we display it
            round_trip_time = (reply.time - request.time) * 1000

            print(f'icmp_seq={sequence} '
                  f'time={round(round_trip_time, 2)} ms')

            # We pause before continuing
            if sequence < count - 1:
                sleep(interval)

        except TimeoutExceeded:
            # The timeout has been reached
            print(f'Request timeout for icmp_seq {sequence}')

        except ICMPError as err:
            # An ICMP error message has been received
            print(err)

        except ICMPLibError:
            # All other errors
            print('General failure...')


verbose_ping('1.1.1.1')
