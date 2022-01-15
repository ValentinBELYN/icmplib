'''
    icmplib
    ~~~~~~~

    The power to forge ICMP packets and do ping and traceroute.

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2022 Valentin BELYN.
    :license: GNU LGPLv3, see the LICENSE for details.

    ~~~~~~~

    Example: ping
'''

from icmplib import ping


host = ping('1.1.1.1', count=10, interval=0.5, timeout=1)

# The IP address of the host that responded to the request
print(host.address)
# '1.1.1.1'

# The minimum round-trip time in milliseconds
print(host.min_rtt)
# 5.761

# The average round-trip time in milliseconds
print(host.avg_rtt)
# 12.036

# The maximum round-trip time in milliseconds
print(host.max_rtt)
# 16.207

# The list of round-trip times expressed in milliseconds
print(host.rtts)
# [ 11.595010757446289, 13.135194778442383, 9.614229202270508,
#   16.018152236938477, 11.960029602050781, 5.761146545410156,
#   16.207218170166016, 11.937141418457031, 12.098073959350586 ]

# The number of requests transmitted to the remote host
print(host.packets_sent)
# 10

# The number of ICMP responses received from the remote host
print(host.packets_received)
# 9

# Packet loss occurs when packets fail to reach their destination
# Returns a float between 0 and 1 (all packets are lost)
print(host.packet_loss)
# 0.1

# The jitter in milliseconds, defined as the variance of the latency of
# packets flowing through the network
# At least two ICMP responses are required to calculate the jitter
print(host.jitter)
# 4.575

# Indicates whether the host is reachable
print(host.is_alive)
# True
