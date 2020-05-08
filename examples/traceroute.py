'''
    icmplib
    ~~~~~~~

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2020 Valentin BELYN.
    :license: GNU LGPLv3, see the LICENSE for details.

    ~~~~~~~

    Example: traceroute
'''

from icmplib import traceroute


hops = traceroute('1.1.1.1', timeout=1, fast_mode=True)

print(hops)
# [<Hop 1 [192.168.0.254]>, <Hop 2 [194.149.169.81]>,
#  <Hop 4 [149.11.115.13]>, <Hop 5 [154.54.61.21]>,
#  <Hop 6 [154.54.60.126]>, <Hop 7 [149.11.0.126]>,
#  <Hop 8 [1.1.1.1]>]


last_distance = 0

for hop in hops:
    if last_distance + 1 != hop.distance:
        print('   *    Some routers are not responding')

    print(f'{hop.distance:4}    {hop.address:15}    '
          f'{round(hop.avg_rtt, 2)} ms')

    last_distance = hop.distance

#   1    192.168.0.254      8.88 ms
#   2    194.149.169.81     11.95 ms
#   *    Some routers are not responding
#   4    149.11.115.13      16.66 ms
#   5    154.54.61.21       4.67 ms
#   6    154.54.60.126      4.38 ms
#   7    149.11.0.126       5.38 ms
#   8    1.1.1.1            4.24 ms