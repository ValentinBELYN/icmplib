'''
    icmplib
    ~~~~~~~

        https://github.com/ValentinBELYN/icmplib

    :copyright: Copyright 2017-2020 Valentin BELYN.
    :license: GNU LGPLv3, see the LICENSE for details.

    ~~~~~~~

    Example: multiping
'''

from icmplib import multiping


addresses = [
    # A fully qualified domain name (FQDN) is allowed. The first
    # address returned from the DNS resolution will be used.
    # For deterministic behavior, prefer to use an IP address.
    'github.com',

    # IPv4 addresses
    '1.1.1.1',
    '8.8.8.8',
    '10.0.0.100',
    '10.0.0.200',

    # IPv6 addresses
    '::1',
]

hosts = multiping(addresses, count=2, interval=0.5, timeout=1)

hosts_alive = []
hosts_dead = []

for host in hosts:
    if host.is_alive:
        hosts_alive.append(host.address)

    else:
        hosts_dead.append(host.address)

print(hosts_alive)
# ['github.com', '1.1.1.1', '8.8.8.8', '::1']

print(hosts_dead)
# ['10.0.0.100', '10.0.0.200']
