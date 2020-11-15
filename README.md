<div align="center">
  <br>
  <img src="media/icmplib-logo-2.0.png" height="190" width="100" alt="icmplib">
  <br>
  <br>

  <br>
  <div>
    <a href="#features">Features</a>&nbsp;&nbsp;&nbsp;
    <a href="#installation">Installation</a>&nbsp;&nbsp;&nbsp;
    <a href="#built-in-functions">Built-in functions</a>&nbsp;&nbsp;&nbsp;
    <a href="#icmp-sockets">ICMP sockets</a>&nbsp;&nbsp;&nbsp;
    <a href="#faq">FAQ</a>&nbsp;&nbsp;&nbsp;
    <a href="#contributing">Contributing</a>&nbsp;&nbsp;&nbsp;
    <a href="#donate">Donate</a>&nbsp;&nbsp;&nbsp;
    <a href="#license">License</a>
  </div>
  <br>

  <pre><strong>icmplib 2.0 is here! 🎉</strong>

To celebrate its first year and its integration into popular projects,
icmplib has been completely revised! Thanks to its advanced features,
including the ability to use the library without root privileges, QoS and
increased compatibility with all modern operating systems, it becomes the
most advanced library in its category. Many things are yet to come!

Star this project if you like it 😍</pre>

  <pre>icmplib is a brand new and modern implementation of the ICMP protocol in Python.
Use the built-in functions or build your own, you have the choice!</pre>
</div>

<br>

## Features

- :deciduous_tree: **Ready-to-use:** icmplib offers ready-to-use functions such as the most popular ones: `ping`, `multiping` and `traceroute`.
- :gem: **Modern:** This library uses the latest technologies offered by Python 3.6+ and is fully object-oriented.
- :rocket: **Fast:** Each class and function has been designed and optimized to deliver the best performance. Some functions are also multithreaded like the `multiping` function. You can ping the world in seconds!
- :zap: **Powerful:** Use the library without root privileges, set the traffic class of ICMP packets, customize their payload and more!
- :nut_and_bolt: **Evolutive:** Easily build your own classes and functions with `ICMPv4` and `ICMPv6` sockets.
- :fire: **Seamless integration of IPv6:** Use IPv6 the same way you use IPv4. Automatic detection is done without impacting performance.
- :rainbow: **Broadcast support** (you must use the `ICMPv4Socket` class to enable it).
- :beer: **Support of all operating systems.** Tested on Linux, macOS and Windows.
- :metal: **No dependency:** icmplib is a pure Python implementation of the ICMP protocol. It does not use any external dependencies.

<br>

## Installation

The recommended way to install or upgrade icmplib is to use `pip3`:

```shell
$ pip3 install icmplib
$ pip3 install --upgrade icmplib
```

*icmplib requires Python 3.6 or later.*

To import icmplib into your project (only import what you need):

```python
# For simple use
from icmplib import ping, multiping, traceroute, resolve, Host, Hop

# For advanced use (sockets)
from icmplib import ICMPv4Socket, ICMPv6Socket, ICMPRequest, ICMPReply

# Exceptions
from icmplib import ICMPLibError, NameLookupError, ICMPSocketError
from icmplib import SocketAddressError, SocketPermissionError
from icmplib import SocketUnavailableError, SocketBroadcastError, TimeoutExceeded
from icmplib import ICMPError, DestinationUnreachable, TimeExceeded
```

<br>

## Built-in functions

### Ping
Send ICMP Echo Request packets to a network host.

```python
ping(address, count=4, interval=1, timeout=2, id=PID, source=None, privileged=True, **kwargs)
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

  The identifier of ICMP requests. Used to match the responses with requests. In practice, a unique identifier should be used for every ping process. On Linux, this identifier is ignored when the `privileged` parameter is disabled.

  - Type: `int`
  - Default: `PID`

- `source`

  The IP address from which you want to send packets. By default, the interface is automatically chosen according to the specified destination.

  - Type: `str`
  - Default: `None`

- `privileged`

  When this option is enabled, this library fully manages the exchanges and the structure of ICMP packets. Disable this option if you want to use this function without root privileges and let the kernel handle ICMP headers.

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
  `address`, `min_rtt`, `avg_rtt`, `max_rtt`, `packets_sent`, `packets_received`, `packet_loss`, `is_alive`

#### Exceptions
- `NameLookupError`

  If you pass a hostname or FQDN in parameters and it does not exist or cannot be resolved.

- `SocketPermissionError`

  If the privileges are insufficient to create the socket.

- `SocketAddressError`

  If the source address cannot be assigned to the socket.

- `ICMPSocketError`

  If another error occurs. See the `ICMPv4Socket` or `ICMPv6Socket` class for details.

#### Example
```python
>>> host = ping('1.1.1.1', count=10, interval=0.2)

>>> host.address            # The IP address of the host that responded
'1.1.1.1'                   # to the request

>>> host.min_rtt            # The minimum round-trip time
12.2

>>> host.avg_rtt            # The average round-trip time
13.2

>>> host.max_rtt            # The maximum round-trip time
17.6

>>> host.packets_sent       # The number of packets transmitted to the
10                          # destination host

>>> host.packets_received   # The number of packets sent by the remote
9                           # host and received by the current host

>>> host.packet_loss        # Packet loss occurs when packets fail to
0.1                         # reach their destination. Returns a float
                            # between 0 and 1 (all packets are lost)
>>> host.is_alive           # Indicates whether the host is reachable
True
```

<br>

### Multiping
Send ICMP Echo Request packets to several network hosts.

This function relies on a single thread to send multiple packets simultaneously. If you mix IPv4 and IPv6 addresses, up to two threads are used.

```python
multiping(addresses, count=2, interval=0.01, timeout=2, id=PID, source=None, privileged=True, **kwargs)
```

#### Parameters
- `addresses`

  The IP addresses of the hosts to which messages should be sent. Hostnames and FQDNs are not allowed. You can easily retrieve their IP address by calling the built-in `resolve` function.

  - Type: `list of str`

- `count`

  The number of ping to perform per address.

  - Type: `int`
  - Default: `2`

- `interval`

  The interval in seconds between sending each packet.

  - Type: `int` or `float`
  - Default: `0.01`

- `timeout`

  The maximum waiting time for receiving all responses in seconds.

  - Type: `int` or `float`
  - Default: `2`

- `id`

  The identifier of ICMP requests. Used to match the responses with requests. This identifier will be incremented by one for each destination. On Linux, this identifier is ignored when the `privileged` parameter is disabled.

  - Type: `int`
  - Default: `PID`

- `source`

  The IP address from which you want to send packets. By default, the interface is automatically chosen according to the specified destination. This parameter should not be used if you are passing both IPv4 and IPv6 addresses to this function.

  - Type: `str`
  - Default: `None`

- `privileged`

  When this option is enabled, this library fully manages the exchanges and the structure of ICMP packets. Disable this option if you want to use this function without root privileges and let the kernel handle ICMP headers.

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
- A `list of Host` objects containing statistics about the desired destinations:<br>
  `address`, `min_rtt`, `avg_rtt`, `max_rtt`, `packets_sent`, `packets_received`, `packet_loss`, `is_alive`

  The list is sorted in the same order as the addresses passed in parameters.

#### Exceptions
- `SocketPermissionError`

  If the privileges are insufficient to create the socket.

- `SocketAddressError`

  If the source address cannot be assigned to the socket.

- `ICMPSocketError`

  If another error occurs. See the `ICMPv4Socket` or `ICMPv6Socket` class for details.

#### Example
```python
>>> hosts = multiping(['10.0.0.5', '127.0.0.1', '::1'])

>>> for host in hosts:
...     if host.is_alive:
...         # See the Host class for details
...         print(f'{host.address} is alive!')
...
...     else:
...         print(f'{host.address} is dead!')
...

# 10.0.0.5 is dead!
# 127.0.0.1 is alive!
# ::1 is alive!
```

<br>

### Traceroute
Determine the route to a destination host.

The Internet is a large and complex aggregation of network hardware, connected together by gateways. Tracking the route one's packets follow can be difficult. This function uses the IP protocol time to live field and attempts to elicit an ICMP Time Exceeded response from each gateway along the path to some host.

*This function requires root privileges to run.*

```python
traceroute(address, count=2, interval=0.05, timeout=2, id=PID, first_hop=1, max_hops=30, source=None, fast=False, **kwargs)
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

- `id`

  The identifier of ICMP requests. Used to match the responses with requests. In practice, a unique identifier should be used for every traceroute process.

  - Type: `int`
  - Default: `PID`

- `first_hop`

  The initial time to live value used in outgoing probe packets.

  - Type: `int`
  - Default: `1`

- `max_hops`

  The maximum time to live (max number of hops) used in outgoing probe packets.

  - Type: `int`
  - Default: `30`

- `source`

  The IP address from which you want to send packets. By default, the interface is automatically chosen according to the specified destination.

  - Type: `str`
  - Default: `None`

- `fast`

  When this option is enabled and an intermediate router has been reached, skip to the next hop rather than perform additional requests. The `count` parameter then becomes the maximum number of requests in the event of no response.

  - Type: `bool`
  - Default: `False`

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
- A `list of Hop` objects representing the route to the desired destination. A `Hop` has the same properties as a `Host` object but it also has a `distance`.

  The list is sorted in ascending order according to the distance, in terms of hops, that separates the remote host from the current machine. Gateways that do not respond to requests are not added to this list.

#### Exceptions
- `NameLookupError`

  If you pass a hostname or FQDN in parameters and it does not exist or cannot be resolved.

- `SocketPermissionError`

  If the privileges are insufficient to create the socket.

- `SocketAddressError`

  If the source address cannot be assigned to the socket.

- `ICMPSocketError`

  If another error occurs. See the `ICMPv4Socket` or `ICMPv6Socket` class for details.

#### Example
```python
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
...

# Distance/TTL    Address                 Average round-trip time
# 1               10.0.0.1                5.196 ms
# 2               194.149.169.49          7.552 ms
# 3               194.149.166.54          12.21 ms
# *               Some gateways are not responding
# 5               212.73.205.22           22.15 ms
# 6               1.1.1.1                 13.59 ms
```

<br>

## ICMP sockets

If you want to create your own functions and classes using the ICMP protocol, you can use the `ICMPv4Socket` (for IPv4 only) and the `ICMPv6Socket` (for IPv6 only). These classes have many methods and properties in common. They manipulate `ICMPRequest` and `ICMPReply` objects.

```
                                    ┌──────────────────┐
  ┌─────────────────┐   send(...)   │   ICMPv4Socket   │   receive()   ┌─────────────────┐
  │   ICMPRequest   │ ────────────> │        or        │ ────────────> │    ICMPReply    │
  └─────────────────┘               │   ICMPv6Socket   │               └─────────────────┘
                                    └──────────────────┘
```

### ICMPRequest
A user-created object that represents an ICMP Echo Request.

```python
ICMPRequest(destination, id, sequence, payload=None, payload_size=56, ttl=64, traffic_class=0)
```

#### Parameters and properties
- `destination`

  The IP address of the host to which the message should be sent.

  - Type: `str`

- `id`

  The identifier of the request. Used to match the reply with the request. In practice, a unique identifier is used for every ping process. On Linux, this identifier is automatically replaced if the request is sent from an unprivileged socket.

  - Type: `int`

- `sequence`

  The sequence number. Used to match the reply with the request. Typically, the sequence number is incremented for each packet sent during the process.

  - Type: `int`

- `payload`

  The payload content in bytes. A random payload is used by default.

  - Type: `bytes`
  - Default: `None`

- `payload_size`

  The payload size. Ignored when the `payload` parameter is set.

  - Type: `int`
  - Default: `56`

- `ttl`

  The time to live of the packet in terms of hops.

  - Type: `int`
  - Default: `64`

- `traffic_class`

  The traffic class of the packet. Provides a defined level of service to the packet by setting the DS Field (formerly TOS) or the Traffic Class field of the IP header. Packets are delivered with the minimum priority by default (Best-effort delivery). Intermediate routers must be able to support this feature.

  *Only available on Unix systems. Ignored on Windows.*

  - Type: `int`
  - Default: `0`

#### Properties only
- `time`

  The timestamp of the ICMP request. Initialized to zero when creating the request and replaced by the `send` method of `ICMPv4Socket` or `ICMPv6Socket` with the time of sending.

  - Type: `float`

<br>

### ICMPReply
A class that represents an ICMP reply. Generated from an ICMP socket (`ICMPv4Socket` or `ICMPv6Socket`).

```python
ICMPReply(source, id, sequence, type, code, bytes_received, time)
```

#### Parameters and properties
- `source`

  The IP address of the gateway or host that composes the ICMP message.

  - Type: `str`

- `id`

  The identifier of the reply. Used to match the reply with the request.

  - Type: `int`

- `sequence`

  The sequence number. Used to match the reply with the request.

  - Type: `int`

- `type`

  The type of ICMP message.

  - Type: `int`

- `code`

  The ICMP error code.

  - Type: `int`

- `bytes_received`

  The number of bytes received.

  - Type: `int`

- `time`

  The timestamp of the ICMP reply.

  - Type: `float`

#### Methods
- `raise_for_status()`

  Throw an exception if the reply is not an ICMP Echo Reply. Otherwise, do nothing.

  - Raises `DestinationUnreachable`: If the destination is unreachable for some reason.
  - Raises `TimeExceeded`: If the time to live field of the ICMP request has reached zero.
  - Raises `ICMPError`: Raised for any other type and ICMP error code, except ICMP Echo Reply messages.

<br>

### ICMPv4Socket
Class for sending and receiving ICMPv4 packets.

```python
ICMPv4Socket(address=None, privileged=True)
```

#### Parameters
- `source`

  The IP address from which you want to listen and send packets. By default, the socket listens on all interfaces.

  - Type: `str`
  - Default: `None`

- `privileged`

  When this option is enabled, the socket fully manages the exchanges and the structure of the ICMP packets. Disable this option if you want to instantiate and use the socket without root privileges and let the kernel handle ICMP headers.

  *Only available on Unix systems. Ignored on Windows.*

  - Type: `bool`
  - Default: `True`

#### Methods
- `__init__(address=None, privileged=True)`

  *Constructor. Automatically called: do not call it directly.*

  - Raises `SocketPermissionError`: If the privileges are insufficient to create the socket.
  - Raises `SocketAddressError`: If the requested address cannot be assigned to the socket.
  - Raises `ICMPSocketError`: If another error occurs while creating the socket.

- `__del__()`

  *Destructor. Automatically called: do not call it directly.*

  Call the `close` method.

- `send(request)`

  Send an ICMP request message over the network to a remote host.<br>
  This operation is non-blocking. Use the `receive` method to get the reply.

  - Parameter `request` *(ICMPRequest)*: The ICMP request you have created. If the socket is used in non-privileged mode on a Linux system, the identifier defined in the request will be replaced by the kernel.
  - Raises `SocketBroadcastError`: If a broadcast address is used and the corresponding option is not enabled on the socket (ICMPv4 only).
  - Raises `SocketUnavailableError`: If the socket is closed.
  - Raises `ICMPSocketError`: If another error occurs while sending.

- `receive(request=None, timeout=2)`

  Receive an ICMP reply message from the socket.<br>
  This method can be called multiple times if you expect several responses as with a broadcast address.

  - Parameter `request` *(ICMPRequest)*: The ICMP request to use to match the response. By default, all ICMP packets arriving on the socket are returned.
  - Parameter `timeout` *(int or float)*: The maximum waiting time for receiving the response in seconds. Default to `2`.
  - Raises `TimeoutExceeded`: If no response is received before the timeout specified in parameters.
  - Raises `SocketUnavailableError`: If the socket is closed.
  - Raises `ICMPSocketError`: If another error occurs while receiving.

  Returns an `ICMPReply` object representing the response of the desired destination or an upstream gateway.

- `close()`

  Close the socket. It cannot be used after this call.

#### Properties
- `address`

  The IP address from which the socket listens and sends packets. Return `None` if the socket listens on all interfaces.

  - Type: `str`

- `is_privileged`

  Indicate whether the socket is running in privileged mode.

  - Type: `bool`

- `is_closed`

  Indicate whether the socket is closed.

  - Type: `bool`

#### Properties and setters
- `broadcast`

  Enable or disable the broadcast support on the socket.

  - Type: `bool`
  - Default: `False`

<br>

### ICMPv6Socket
Class for sending and receiving ICMPv6 packets.

```python
ICMPv6Socket(address=None, privileged=True)
```

#### Methods and properties
The same methods and properties as for the `ICMPv4Socket` class, except the `broadcast` property.

<br>

### Exceptions
The library contains many exceptions to adapt to your needs:

```
ICMPLibError
 ├─ NameLookupError
 ├─ ICMPSocketError
 │  ├─ SocketAddressError
 │  ├─ SocketPermissionError
 │  ├─ SocketUnavailableError
 │  ├─ SocketBroadcastError
 │  └─ TimeoutExceeded
 │
 └─ ICMPError
    ├─ DestinationUnreachable
    │  ├─ ICMPv4DestinationUnreachable
    │  └─ ICMPv6DestinationUnreachable
    │
    └─ TimeExceeded
       ├─ ICMPv4TimeExceeded
       └─ ICMPv6TimeExceeded
```

- `ICMPLibError`: Exception class for the icmplib package.
- `NameLookupError`: Raised when the requested name does not exist or cannot be resolved. This concerns both Fully Qualified Domain Names and hostnames.
- `ICMPSocketError`: Base class for ICMP sockets exceptions.
- `SocketAddressError`: Raised when the requested address cannot be assigned to the socket.
- `SocketPermissionError`: Raised when the privileges are insufficient to create the socket.
- `SocketUnavailableError`: Raised when an action is performed while the socket is closed.
- `SocketBroadcastError`: Raised when a broadcast address is used and the corresponding option is not enabled on the socket.
- `TimeoutExceeded`: Raised when a timeout occurs on a socket.
- `ICMPError`: Base class for ICMP error messages.
- `DestinationUnreachable`: Destination Unreachable message is generated by the host or its inbound gateway to inform the client that the destination is unreachable for some reason.
- `TimeExceeded`: Time Exceeded message is generated by a gateway to inform the source of a discarded datagram due to the time to live field reaching zero. A Time Exceeded message may also be sent by a host if it fails to reassemble a fragmented datagram within its time limit.

Use the `message` property to get the error message. `ICMPError` subclasses have a `reply` property to retrieve the response.

<br>

### Examples
#### Sockets in action
```python
def single_ping(address, timeout=2, id=PID):
    # Create an ICMP socket
    sock = ICMPv4Socket()

    # Create an ICMP request
    # See the 'ICMPRequest' class for details
    request = ICMPRequest(
        destination=address,
        id=id,
        sequence=1)

    try:
        sock.send(request)

        # If the program arrives in this section, it means that the
        # packet has been transmitted.

        reply = sock.receive(request, timeout)

        # If the program arrives in this section, it means that a
        # packet has been received. The reply has the same identifier
        # and sequence number that the request but it can come from
        # an intermediate gateway.

        reply.raise_for_status()

        # If the program arrives in this section, it means that the
        # destination host has responded to the request.

    except TimeoutExceeded as err:
        # The timeout has been reached
        print(err)

    except DestinationUnreachable as err:
        # The reply indicates that the destination host is unreachable
        print(err)

        # Retrieve the response
        reply = err.reply

    except TimeExceeded as err:
        # The reply indicates that the time to live exceeded in transit
        print(err)

        # Retrieve the response
        reply = err.reply

    except ICMPLibError as err:
        # All other errors
        print(err)

    # Automatic socket closure (garbage collector)
```

#### Verbose ping
```python
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
            print(f'{reply.bytes_received} bytes from '
                  f'{reply.source}: ', end='')

            # We throw an exception if it is an ICMP error message
            reply.raise_for_status()

            # We calculate the round-trip time and we display it
            round_trip_time = (reply.time - request.time) * 1000

            print(f'icmp_seq={sequence} '
                  f'time={round(round_trip_time, 3)} ms')

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
            print('An error has occurred.')


verbose_ping('1.1.1.1')

# PING 1.1.1.1: 56 data bytes
# 64 bytes from 1.1.1.1: icmp_seq=0 time=12.061 ms
# 64 bytes from 1.1.1.1: icmp_seq=1 time=12.597 ms
# 64 bytes from 1.1.1.1: icmp_seq=2 time=12.475 ms
# 64 bytes from 1.1.1.1: icmp_seq=3 time=10.822 ms
```

<br>

## FAQ

### How to resolve a FQDN/domain name or a hostname?
The use of the built-in `resolve` function is recommended:

```python
>>> resolve('github.com')
'140.82.118.4'
```

- If several IP addresses are available, only the first one is returned. This function searches for IPv4 addresses first before searching for IPv6 addresses.
- If you pass an IP address, no lookup is done. The same address is returned.
- Raises a `NameLookupError` exception if the requested name does not exist or cannot be resolved.

### Why I have no response from a remote host?
In the event of no response from a remote host, several causes are possible:
- Your computer's firewall may not be properly configured. This impacts in particular the `traceroute` function which can no longer receive ICMP Time Exceeded messages.
- The remote host or an upstream gateway is down.
- The remote host or an upstream gateway drops ICMP messages for security reasons.
- In the case of the `traceroute` function, if the last host in the list is not the one expected, more than 30 hops (default) may be needed to reach it. You can try increasing the value of the `max_hops` parameter.

## Contributing

Comments and enhancements are welcome.

All development is done on [GitHub](https://github.com/ValentinBELYN/icmplib). Use [Issues](https://github.com/ValentinBELYN/icmplib/issues) to report problems and submit feature requests. Please include a minimal example that reproduces the bug.

## Donate

icmplib is completely free and open source. It has been fully developed on my free time. If you enjoy it, please consider donating to support the development.

- [:tada: Donate via PayPal](https://paypal.me/ValentinBELYN)

## License

Copyright 2017-2020 Valentin BELYN.

Code released under the GNU LGPLv3 license. See the [LICENSE](LICENSE) for details.
