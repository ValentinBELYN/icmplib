'''
    icmplib
    ~~~~~~~

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2020 Valentin BELYN.
    :license: GNU LGPLv3, see the LICENSE for details.

    ~~~~~~~

    Example: broadcast ping (advanced)

    PING 255.255.255.255: 56 data bytes

        64 bytes from 10.0.0.17: icmp_seq=0 time=1.06 ms
        64 bytes from 10.0.0.40: icmp_seq=0 time=1.59 ms
        64 bytes from 10.0.0.41: icmp_seq=0 time=9.47 ms

        64 bytes from 10.0.0.17: icmp_seq=1 time=0.98 ms
        64 bytes from 10.0.0.40: icmp_seq=1 time=1.57 ms
        64 bytes from 10.0.0.41: icmp_seq=1 time=9.34 ms

        64 bytes from 10.0.0.17: icmp_seq=2 time=0.91 ms
        64 bytes from 10.0.0.40: icmp_seq=2 time=2.03 ms
        64 bytes from 10.0.0.41: icmp_seq=2 time=9.55 ms

        64 bytes from 10.0.0.17: icmp_seq=3 time=1.11 ms
        64 bytes from 10.0.0.40: icmp_seq=3 time=1.38 ms
        64 bytes from 10.0.0.41: icmp_seq=3 time=9.56 ms
'''

from icmplib import (
    ICMPv4Socket,
    ICMPRequest,
    TimeoutExceeded,
    ICMPLibError,
    PID)


def broadcast_ping(address, count=4, timeout=1, id=PID):
    # ICMPRequest uses a payload of 56 bytes by default
    # You can modify it using the payload_size parameter
    print(f'PING {address}: 56 data bytes')

    # Broadcast is only possible in IPv4
    socket = ICMPv4Socket()

    # We allow the socket to send broadcast packets
    socket.broadcast = True

    for sequence in range(count):
        # We create an ICMP request
        request = ICMPRequest(
            destination=address,
            id=id,
            sequence=sequence,
            timeout=timeout)

        print()

        try:
            # We send the request
            socket.send(request)

            while 'we receive replies':
                # We are awaiting receipt of an ICMP reply
                # If there is no more responses, the TimeoutExceeded
                # exception is thrown and the loop is stopped
                reply = socket.receive()

                # We calculate the round-trip time of the reply
                round_trip_time = (reply.time - request.time) * 1000

                # We display some information
                print(f'  {reply.received_bytes} bytes from '
                      f'{reply.source}: icmp_seq={sequence} '
                      f'time={round(round_trip_time, 2)} ms')

        except TimeoutExceeded:
            # The timeout has been reached
            # We use this exception to break the while loop
            pass

        except ICMPLibError:
            # All other errors
            print('An error has occurred.')


# Limited broadcast
broadcast_ping('255.255.255.255')

# Directed broadcast
# broadcast_ping('192.168.0.255')
