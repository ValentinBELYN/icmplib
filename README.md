<div align="center">
  <br>
  <br>
  <img src="media/icmplib-logo.png" height="125" width="100" alt="icmplib">
  <br>

  <br>
  <div>
    <a href="#features">Features</a>&nbsp;&nbsp;&nbsp;
    <a href="#installation">Installation</a>&nbsp;&nbsp;&nbsp;
    <a href="#getting-started">Getting started</a>&nbsp;&nbsp;&nbsp;
    <a href="#documentation">Documentation</a>&nbsp;&nbsp;&nbsp;
    <a href="#contributing">Contributing</a>&nbsp;&nbsp;&nbsp;
    <a href="#donate">Donate</a>&nbsp;&nbsp;&nbsp;
    <a href="#license">License</a>
  </div>
  <br>

  <pre>icmplib is a brand new and modern implementation of the ICMP protocol in Python.
Use the built-in functions or build your own, you have the choice!

<a href="CHANGELOG.md">icmplib 3.0 has been released! See what's new 🎉</a></pre>

  <a href="https://pypi.org/project/icmplib">
    <img src="https://img.shields.io/pypi/dm/icmplib.svg?style=flat-square&labelColor=0366d6&color=005cc5" alt="statistics">
  </a>
</div>

<br>

## Features

- :deciduous_tree: **Ready-to-use:** icmplib offers ready-to-use functions such as the most popular ones: `ping`, `multiping` and `traceroute`. An extensive documentation also helps you get started.
- :gem: **Modern:** This library uses the latest mechanisms offered by Python 3.6/3.7+ and is fully object-oriented.
- :rocket: **Fast:** Each class and function has been designed and optimized to deliver the best performance. Some functions are also asynchronous like the `async_ping` and `async_multiping` functions. You can ping the world in seconds!
- :zap: **Powerful:** Use the library without root privileges, set the traffic class of ICMP packets, customize their payload, send broadcast requests and more!
- :nut_and_bolt: **Evolutive:** Easily build your own classes and functions with `ICMPv4` and `ICMPv6` sockets.
- :fire: **Seamless integration of IPv6:** Use IPv6 the same way you use IPv4.
- :beer: **Cross-platform:** Optimized for Linux, macOS and Windows. The library automatically manages the specificities of each system.
- :metal: **No dependency:** icmplib is a pure Python implementation of the ICMP protocol. It does not rely on any external dependency.

<br>

## Installation

- **Install icmplib**

  The recommended way to install icmplib is to use `pip3`:

  ```shell
  $ pip3 install icmplib
  ```

  *Since icmplib 3, Python 3.7 or later is required to use the library.*<br>
  *If you are using Python 3.6 and you cannot update it, you can still install icmplib 2.*

- **Import basic functions**

  ```python
  from icmplib import ping, multiping, traceroute, resolve
  ```

- **Import asynchronous functions**

  ```python
  from icmplib import async_ping, async_multiping, async_resolve
  ```

- **Import sockets (advanced)**

  ```python
  from icmplib import ICMPv4Socket, ICMPv6Socket, AsyncSocket, ICMPRequest, ICMPReply
  ```

- **Import exceptions**

  ```python
  from icmplib import ICMPLibError, NameLookupError, ICMPSocketError
  from icmplib import SocketAddressError, SocketPermissionError
  from icmplib import SocketUnavailableError, SocketBroadcastError, TimeoutExceeded
  from icmplib import ICMPError, DestinationUnreachable, TimeExceeded
  ```

  *Import only what you need.*

<br>

## Getting started

### ping

Send ICMP Echo Request packets to a network host.

```python
ping(address, count=4, interval=1, timeout=2, id=None, source=None, family=None, privileged=True, **kwargs)
```

#### Parameters

- `address`

  The IP address, hostname or FQDN of the host to which messages should be sent. For deterministic behavior, prefer to use an IP address.

  - Type: `str`

- `count`

  The number of ping to perform.

  - Type: `int`
  - Default: `4`

- `interval`

  The interval in seconds between sending each packet.

  - Type: `int` or `float`
  - Default: `1`

- `timeout`

  The maximum waiting time for receiving a reply in seconds.

  - Type: `int` or `float`
  - Default: `2`

- `id`

  The identifier of ICMP requests. Used to match the responses with requests. In practice, a unique identifier should be used for every ping process. On Linux, this identifier is ignored when the `privileged` parameter is disabled. The library handles this identifier itself by default.

  - Type: `int`
  - Default: `None`

- `source`

  The IP address from which you want to send packets. By default, the interface is automatically chosen according to the specified destination.

  - Type: `str`
  - Default: `None`

- `family`

  The address family if a hostname or FQDN is specified. Can be set to `4` for IPv4 or `6` for IPv6 addresses. By default, this function searches for IPv4 addresses first before searching for IPv6 addresses.

  - Type: `int`
  - Default: `None`

- `privileged`

  When this option is enabled, this library fully manages the exchanges and the structure of ICMP packets. Disable this option if you want to use this function without root privileges and let the kernel handle ICMP headers.

  [Learn more about the `privileged` parameter.]

  *Only available on Unix systems. Ignored on Windows.*

  - Type: `bool`
  - Default: `True`

- `payload`

  The payload content in bytes. A random payload is used by default.

  - Type: `bytes`
  - Default: `None`

- `payload_size`

  The payload size. Ignored when the `payload` parameter is set.

  - Type: `int`
  - Default: `56`

- `traffic_class`

  The traffic class of ICMP packets. Provides a defined level of service to packets by setting the DS Field (formerly TOS) or the Traffic Class field of IP headers. Packets are delivered with the minimum priority by default (Best-effort delivery). Intermediate routers must be able to support this feature.

  *Only available on Unix systems. Ignored on Windows.*

  - Type: `int`
  - Default: `0`

#### Return value

- A `Host` object containing statistics about the desired destination:<br>
  `address`, `min_rtt`, `avg_rtt`, `max_rtt`, `rtts`, `packets_sent`, `packets_received`, `packet_loss`, `jitter`, `is_alive`

#### Exceptions

- [`NameLookupError`]

  If you pass a hostname or FQDN in parameters and it does not exist or cannot be resolved.

- [`SocketPermissionError`]

  If the privileges are insufficient to create the socket.

- [`SocketAddressError`]

  If the source address cannot be assigned to the socket.

- [`ICMPSocketError`]

  If another error occurs. See the [`ICMPv4Socket`] or [`ICMPv6Socket`] class for details.

#### Example

```python
>>> from icmplib import ping

>>> host = ping('1.1.1.1', count=10, interval=0.2)

>>> host.address              # The IP address of the host that responded
'1.1.1.1'                     # to the request

>>> host.min_rtt              # The minimum round-trip time in milliseconds
5.761

>>> host.avg_rtt              # The average round-trip time in milliseconds
12.036

>>> host.max_rtt              # The maximum round-trip time in milliseconds
16.207

>>> host.rtts                 # The list of round-trip times expressed in
[ 11.595, 13.135, 9.614,      # milliseconds
  16.018, 11.960, 5.761,      # The results are not rounded unlike other
  16.207, 11.937, 12.098 ]    # properties

>>> host.packets_sent         # The number of requests transmitted to the
10                            # remote host

>>> host.packets_received     # The number of ICMP responses received from
9                             # the remote host

>>> host.packet_loss          # Packet loss occurs when packets fail to
0.1                           # reach their destination. Returns a float
                              # between 0 and 1 (all packets are lost)

>>> host.jitter               # The jitter in milliseconds, defined as the
4.575                         # variance of the latency of packets flowing
                              # through the network

>>> host.is_alive             # Indicates whether the host is reachable
True
```

<br>

### multiping

Send ICMP Echo Request packets to several network hosts.

```python
multiping(addresses, count=2, interval=0.5, timeout=2, concurrent_tasks=50, source=None, family=None, privileged=True, **kwargs)
```

#### Parameters

- `addresses`

  The IP addresses of the hosts to which messages should be sent. Hostnames and FQDNs are allowed but not recommended. You can easily retrieve their IP address by calling the built-in [`resolve`] function.

  - Type: `list[str]`

- `count`

  The number of ping to perform per address.

  - Type: `int`
  - Default: `2`

- `interval`

  The interval in seconds between sending each packet.

  - Type: `int` or `float`
  - Default: `0.5`

- `timeout`

  The maximum waiting time for receiving a reply in seconds.

  - Type: `int` or `float`
  - Default: `2`

- `concurrent_tasks`

  The maximum number of concurrent tasks to speed up processing. This value cannot exceed the maximum number of file descriptors configured on the operating system.

  - Type: `int`
  - Default: `50`

- `source`

  The IP address from which you want to send packets. By default, the interface is automatically chosen according to the specified destinations. This parameter should not be used if you are passing both IPv4 and IPv6 addresses to this function.

  - Type: `str`
  - Default: `None`

- `family`

  The address family if a hostname or FQDN is specified. Can be set to `4` for IPv4 or `6` for IPv6 addresses. By default, this function searches for IPv4 addresses first before searching for IPv6 addresses.

  - Type: `int`
  - Default: `None`

- `privileged`

  When this option is enabled, this library fully manages the exchanges and the structure of ICMP packets. Disable this option if you want to use this function without root privileges and let the kernel handle ICMP headers.

  [Learn more about the `privileged` parameter.]

  *Only available on Unix systems. Ignored on Windows.*

  - Type: `bool`
  - Default: `True`

- `payload`

  The payload content in bytes. A random payload is used by default.

  - Type: `bytes`
  - Default: `None`

- `payload_size`

  The payload size. Ignored when the `payload` parameter is set.

  - Type: `int`
  - Default: `56`

- `traffic_class`

  The traffic class of ICMP packets. Provides a defined level of service to packets by setting the DS Field (formerly TOS) or the Traffic Class field of IP headers. Packets are delivered with the minimum priority by default (Best-effort delivery). Intermediate routers must be able to support this feature.

  *Only available on Unix systems. Ignored on Windows.*

  - Type: `int`
  - Default: `0`

#### Return value

- A list of `Host` objects containing statistics about the desired destinations:<br>
  `address`, `min_rtt`, `avg_rtt`, `max_rtt`, `rtts`, `packets_sent`, `packets_received`, `packet_loss`, `jitter`, `is_alive`

  The list is sorted in the same order as the addresses passed in parameters.

#### Exceptions

- [`NameLookupError`]

  If you pass a hostname or FQDN in parameters and it does not exist or cannot be resolved.

- [`SocketPermissionError`]

  If the privileges are insufficient to create the socket.

- [`SocketAddressError`]

  If the source address cannot be assigned to the socket.

- [`ICMPSocketError`]

  If another error occurs. See the [`ICMPv4Socket`] or [`ICMPv6Socket`] class for details.

#### Example

```python
>>> from icmplib import multiping

>>> hosts = multiping(['10.0.0.5', '127.0.0.1', '::1'])

>>> for host in hosts:
...     if host.is_alive:
...         # See the Host class for details
...         print(f'{host.address} is up!')
...     else:
...         print(f'{host.address} is down!')

# 10.0.0.5 is down!
# 127.0.0.1 is up!
# ::1 is up!
```

<br>

### traceroute

Determine the route to a destination host.

The Internet is a large and complex aggregation of network hardware, connected together by gateways. Tracking the route one's packets follow can be difficult. This function uses the IP protocol time to live field and attempts to elicit an ICMP Time Exceeded response from each gateway along the path to some host.

*This function requires root privileges to run.*

```python
traceroute(address, count=2, interval=0.05, timeout=2, first_hop=1, max_hops=30, fast=False, id=None, source=None, family=None, **kwargs)
```

#### Parameters

- `address`

  The IP address, hostname or FQDN of the host to reach. For deterministic behavior, prefer to use an IP address.

  - Type: `str`

- `count`

  The number of ping to perform per hop.

  - Type: `int`
  - Default: `2`

- `interval`

  The interval in seconds between sending each packet.

  - Type: `int` or `float`
  - Default: `0.05`

- `timeout`

  The maximum waiting time for receiving a reply in seconds.

  - Type: `int` or `float`
  - Default: `2`

- `first_hop`

  The initial time to live value used in outgoing probe packets.

  - Type: `int`
  - Default: `1`

- `max_hops`

  The maximum time to live (max number of hops) used in outgoing probe packets.

  - Type: `int`
  - Default: `30`

- `fast`

  When this option is enabled and an intermediate router has been reached, skip to the next hop rather than perform additional requests. The `count` parameter then becomes the maximum number of requests in the event of no response.

  - Type: `bool`
  - Default: `False`

- `id`

  The identifier of ICMP requests. Used to match the responses with requests. In practice, a unique identifier should be used for every traceroute process. The library handles this identifier itself by default.

  - Type: `int`
  - Default: `None`

- `source`

  The IP address from which you want to send packets. By default, the interface is automatically chosen according to the specified destination.

  - Type: `str`
  - Default: `None`

- `family`

  The address family if a hostname or FQDN is specified. Can be set to `4` for IPv4 or `6` for IPv6 addresses. By default, this function searches for IPv4 addresses first before searching for IPv6 addresses.

  - Type: `int`
  - Default: `None`

- `payload`

  The payload content in bytes. A random payload is used by default.

  - Type: `bytes`
  - Default: `None`

- `payload_size`

  The payload size. Ignored when the `payload` parameter is set.

  - Type: `int`
  - Default: `56`

- `traffic_class`

  The traffic class of ICMP packets. Provides a defined level of service to packets by setting the DS Field (formerly TOS) or the Traffic Class field of IP headers. Packets are delivered with the minimum priority by default (Best-effort delivery). Intermediate routers must be able to support this feature.

  *Only available on Unix systems. Ignored on Windows.*

  - Type: `int`
  - Default: `0`

#### Return value

- A list of `Hop` objects representing the route to the desired destination. A `Hop` has the same properties as a `Host` object but it also has a `distance`:<br>
  `address`, `min_rtt`, `avg_rtt`, `max_rtt`, `rtts`, `packets_sent`, `packets_received`, `packet_loss`, `jitter`, `is_alive`, `distance`

  The list is sorted in ascending order according to the distance, in terms of hops, that separates the remote host from the current machine. Gateways that do not respond to requests are not added to this list.

#### Exceptions

- [`NameLookupError`]

  If you pass a hostname or FQDN in parameters and it does not exist or cannot be resolved.

- [`SocketPermissionError`]

  If the privileges are insufficient to create the socket.

- [`SocketAddressError`]

  If the source address cannot be assigned to the socket.

- [`ICMPSocketError`]

  If another error occurs. See the [`ICMPv4Socket`] or [`ICMPv6Socket`] class for details.

#### Example

```python
>>> from icmplib import traceroute

>>> hops = traceroute('1.1.1.1')

>>> print('Distance/TTL    Address    Average round-trip time')
>>> last_distance = 0

>>> for hop in hops:
...     if last_distance + 1 != hop.distance:
...         print('Some gateways are not responding')
...
...     # See the Hop class for details
...     print(f'{hop.distance}    {hop.address}    {hop.avg_rtt} ms')
...
...     last_distance = hop.distance

# Distance/TTL    Address                 Average round-trip time
# 1               10.0.0.1                5.196 ms
# 2               194.149.169.49          7.552 ms
# 3               194.149.166.54          12.21 ms
# *               Some gateways are not responding
# 5               212.73.205.22           22.15 ms
# 6               1.1.1.1                 13.59 ms
```

<br>

### async_ping

Send ICMP Echo Request packets to a network host.

*This function is non-blocking.*

```python
async_ping(address, count=4, interval=1, timeout=2, id=None, source=None, family=None, privileged=True, **kwargs)
```

#### Parameters, return value and exceptions

The same parameters, return value and exceptions as for the [`ping`] function.

#### Example

```python
>>> import asyncio
>>> from icmplib import async_ping

>>> async def is_alive(address):
...     host = await async_ping(address, count=10, interval=0.2)
...     return host.is_alive

>>> asyncio.run(is_alive('1.1.1.1'))
True
```

<br>

### async_multiping

Send ICMP Echo Request packets to several network hosts.

*This function is non-blocking.*

```python
async_multiping(addresses, count=2, interval=0.5, timeout=2, concurrent_tasks=50, source=None, family=None, privileged=True, **kwargs)
```

#### Parameters, return value and exceptions

The same parameters, return values and exceptions as for the [`multiping`] function.

#### Example

```python
>>> import asyncio
>>> from icmplib import async_multiping

>>> async def are_alive(*addresses):
...     hosts = await async_multiping(addresses)
...     
...     for host in hosts:
...         if not host.is_alive:
...             return False
...
...     return True

>>> asyncio.run(are_alive('10.0.0.5', '127.0.0.1', '::1'))
False
```

<br>

## Documentation

This page only gives an overview of the features of icmplib.

To learn more about the built-in functions, on how to create your own and handle exceptions, you can click on the following link:

- :rocket: [Documentation]

## Contributing

Comments and enhancements are welcome.

All development is done on [GitHub]. Use [Issues] to report problems and submit feature requests. Please include a minimal example that reproduces the bug.

## Donate

icmplib is completely free and open source. It has been fully developed on my free time. If you enjoy it, please consider donating to support the development.

- :tada: [Donate via PayPal]

## License

Copyright 2017-2022 Valentin BELYN.

Code released under the GNU LGPLv3 license. See the [LICENSE] for details.

[Learn more about the `privileged` parameter.]: docs/6-use-icmplib-without-privileges.md
[Documentation]: docs
[GitHub]: https://github.com/ValentinBELYN/icmplib
[Issues]: https://github.com/ValentinBELYN/icmplib/issues
[Donate via PayPal]: https://paypal.me/ValentinBELYN
[LICENSE]: LICENSE
[`ping`]: #ping
[`multiping`]: #multiping
[`ICMPv4Socket`]: docs/3-sockets.md#ICMPv4Socket
[`ICMPv6Socket`]: docs/3-sockets.md#ICMPv6Socket
[`NameLookupError`]: docs/4-exceptions.md#NameLookupError
[`ICMPSocketError`]: docs/4-exceptions.md#ICMPSocketError
[`SocketAddressError`]: docs/4-exceptions.md#SocketAddressError
[`SocketPermissionError`]: docs/4-exceptions.md#SocketPermissionError
[`resolve`]: docs/5-utilities.md#resolve
