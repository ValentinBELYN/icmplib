'''
    icmplib
    ~~~~~~~

    A powerful library for forging ICMP packets and performing ping
    and traceroute.

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2020 Valentin BELYN.
    :license: GNU LGPLv3, see the LICENSE for details.

    ~~~~~~~

    Example: multiping
'''

from icmplib import resolve, multiping


addresses = [
    # IPv4 addresses
    '1.1.1.1',
    '8.8.8.8',
    '10.0.0.100',
    '10.0.0.200',

    # IPv6 addresses
    '::1',

    # Hostnames and Fully Qualified Domain Names (FQDNs) are not
    # allowed. You can easily retrieve their IP address by calling the
    # built-in 'resolve' function. The first address returned from the
    # DNS resolution will be used. For deterministic behavior, prefer
    # to use an IP address.
    resolve('github.com')
]

hosts = multiping(addresses, count=2, timeout=1)

hosts_alive = []
hosts_dead = []

for host in hosts:
    if host.is_alive:
        hosts_alive.append(host.address)

    else:
        hosts_dead.append(host.address)

print(hosts_alive)
# ['1.1.1.1', '8.8.8.8', '::1', '140.82.121.4']

print(hosts_dead)
# ['10.0.0.100', '10.0.0.200']
