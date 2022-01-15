'''
    icmplib
    ~~~~~~~

    The power to forge ICMP packets and do ping and traceroute.

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2022 Valentin BELYN.
    :license: GNU LGPLv3, see the LICENSE for details.

    ~~~~~~~

    Example: traceroute
'''

from icmplib import traceroute


hops = traceroute('1.1.1.1', timeout=1, fast=True)

print(hops)
# [ <Hop 1 [10.0.0.1]>, <Hop 2 [194.149.169.49]>,
#   <Hop 3 [194.149.166.54]>, <Hop 5 [212.73.205.22]>,
#   <Hop 6 [1.1.1.1]> ]

last_distance = 0

for hop in hops:
    if last_distance + 1 != hop.distance:
        print('  *     Some gateways are not responding')

    print(f'  {hop.distance:<2}    {hop.address:15}    '
          f'{hop.avg_rtt} ms')

    last_distance = hop.distance

#   1       10.0.0.1            5.196 ms
#   2       194.149.169.49      7.552 ms
#   3       194.149.166.54      12.21 ms
#   *       Some gateways are not responding
#   5       212.73.205.22       22.15 ms
#   6       1.1.1.1             13.59 ms
