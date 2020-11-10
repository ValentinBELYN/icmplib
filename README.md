<div align="center">
  <br>
  <img src="media/icmplib-logo.png" height="125" width="100" alt="icmplib">
  <br>
  <br>

  <p><strong>Easily forge ICMP packets and make your own ping and traceroute.</strong></p>
  <a href="https://pypi.org/project/icmplib">
    <img src="https://img.shields.io/pypi/dm/icmplib.svg?style=flat-square&labelColor=0366d6&color=005cc5" alt="statistics">
  </a>
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
  <br>

  <pre>icmplib is a brand new and modern implementation of the ICMP protocol in Python.
Use the built-in functions or build your own, you have the choice!

<strong>Root privileges are required to use this library (raw sockets).</strong></pre>
</div>

<br>

## Features

- :deciduous_tree: **Ready-to-use:** icmplib offers ready-to-use functions such as the most popular ones: `ping`, `multiping` and `traceroute`.
- :gem: **Modern:** This library uses the latest technologies offered by Python 3.6+ and is fully object-oriented.
- :rocket: **Fast:** Each class and function has been designed and optimized to deliver the best performance. Some functions are also multithreaded (like the `multiping` function). You can ping the world in seconds!
- :nut_and_bolt: **Powerful and evolutive:** Easily build your own classes and functions with `ICMPv4` and `ICMPv6` sockets.
- :fire: **Seamless integration of IPv6:** Use IPv6 the same way you use IPv4. Automatic detection is done without impacting performance.
- :rainbow: **Broadcast support** (you must use the `ICMPv4Socket` class to enable it).
- :beer: **Support of all operating systems.** Tested on Linux, macOS and Windows.
- :metal: **No dependency:** icmplib is a pure Python implementation of the ICMP protocol. It does not use any external dependencies.

<br>

## Installation

Install, upgrade and uninstall icmplib with these commands:

```shell
$ pip3 install icmplib
$ pip3 install --upgrade icmplib
$ pip3 uninstall icmplib
```

icmplib requires Python 3.6 or later.

Import icmplib into your project (only import what you need):

```python
# For simple use
from icmplib import ping, multiping, traceroute, Host, Hop

# For advanced use (sockets)
from icmplib import ICMPv4Socket, ICMPv6Socket, ICMPRequest, ICMPReply

# Exceptions
from icmplib import ICMPLibError, ICMPSocketError, SocketPermissionError
from icmplib import SocketUnavailableError, SocketBroadcastError, TimeoutExceeded
from icmplib import ICMPError, DestinationUnreachable, TimeExceeded
```

<br>

## Built-in functions

### Ping
Send *ICMP ECHO_REQUEST* packets to a network host.

#### Definition
```python
ping(address, count=4, interval=1, timeout=2, id=PID, **kwargs)
```

#### Parameters
- `address`

  The IP address of the gateway or host to which the message should be sent.

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

  The identifier of the request. Used to match the reply with the request.<br>
  In practice, a unique identifier is used for every ping process.

  - Type: `int`
  - Default: `PID`

- `**kwargs`

  `Optional` Advanced use: arguments passed to `ICMPRequest` objects.

#### Return value
- `Host` object

  A `Host` object containing statistics about the desired destination:<br>
  `address`, `min_rtt`, `avg_rtt`, `max_rtt`, `packets_sent`,<br>
  `packets_received`, `packet_loss`, `is_alive`.

#### Exceptions
- `SocketPermissionError`

  If the permissions are insufficient to create a socket.

#### Example
```python
>>> host = ping('1.1.1.1', count=10, interval=0.2)

>>> host.address            # The IP address of the gateway or host
'1.1.1.1'                   # that responded to the request

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
Send *ICMP ECHO_REQUEST* packets to multiple network hosts.

#### Definition
```python
multiping(addresses, count=2, interval=1, timeout=2, id=PID, max_threads=10, **kwargs)
```

#### Parameters
- `addresses`

  The IP addresses of the gateways or hosts to which messages should be sent.

  - Type: `list of str`

- `count`

  The number of ping to perform per address.

  - Type: `int`
  - Default: `2`

- `interval`

  The interval in seconds between sending each packet.

  - Type: `int` or `float`
  - Default: `1`

- `timeout`

  The maximum waiting time for receiving a reply in seconds.

  - Type: `int` or `float`
  - Default: `2`

- `id`

  The identifier of the requests. This identifier will be incremented by one for each destination.

  - Type: `int`
  - Default: `PID`

- `max_threads`

  The number of threads allowed to speed up processing.

  - Type: `int`
  - Default: `10`

- `**kwargs`

  `Optional` Advanced use: arguments passed to `ICMPRequest` objects.

#### Return value
- `List of Host`

  A `list of Host` objects containing statistics about the desired destinations:<br>
  `address`, `min_rtt`, `avg_rtt`, `max_rtt`, `packets_sent`,<br>
  `packets_received`, `packet_loss`, `is_alive`.<br>
  The list is sorted in the same order as the addresses passed in parameters.

#### Exceptions
- `SocketPermissionError`

  If the permissions are insufficient to create a socket.

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

The Internet is a large and complex aggregation of network hardware, connected together by gateways. Tracking the route one's packets follow can be difficult. This function utilizes the IP protocol time to live field and attempts to elicit an *ICMP TIME_EXCEEDED* response from each gateway along the path to some host.

#### Definition
```python
traceroute(address, count=3, interval=0.05, timeout=2, id=PID, traffic_class=0, min_hops=1, max_hops=30, fast_mode=False, **kwargs)
```

#### Parameters
- `address`

  The destination IP address.

  - Type: `str`

- `count`

  The number of ping to perform per hop.

  - Type: `int`
  - Default: `3`

- `interval`

  The interval in seconds between sending each packet.

  - Type: `int` or `float`
  - Default: `0.05`

- `timeout`

  The maximum waiting time for receiving a reply in seconds.

  - Type: `int` or `float`
  - Default: `2`

- `id`

  The identifier of the request. Used to match the reply with the request.<br>
  In practice, a unique identifier is used for every ping process.

  - Type: `int`
  - Default: `PID`

- `traffic_class`

  The traffic class of packets. Provides a defined level of service to packets by setting the DS Field (formerly TOS) or the Traffic Class field of IP headers. Packets are delivered with the minimum priority by default (Best-effort delivery).

  Intermediate routers must be able to support this feature.<br>
  *Only available on Unix systems. Ignored on Windows.*

  - Type: `int`
  - Default: `0`

- `min_hops`

  The minimum time to live (max number of hops) used in outgoing probe packets.

  - Type: `int`
  - Default: `1`

- `max_hops`

  The maximum time to live (max number of hops) used in outgoing probe packets.

  - Type: `int`
  - Default: `30`

- `fast_mode`

  When this option is enabled and an intermediate router has been reached, skip to the next hop rather than perform additional requests. The `count` parameter then becomes the maximum number of requests in case of no responses.

  - Type: `bool`
  - Default: `False`

- `**kwargs`

  `Optional` Advanced use: arguments passed to `ICMPRequest` objects.

#### Return value
- `List of Hop`

  A `list of Hop` objects representing the route to the desired host. A `Hop` is a `Host` object with an additional attribute: a `distance`. The list is sorted in ascending order according to the distance (in terms of hops) that separates the remote host from the current machine.

#### Exceptions
- `SocketPermissionError`

  If the permissions are insufficient to create a socket.

#### Example
```python
>>> hops = traceroute('1.1.1.1')

>>> print('Distance (ttl)    Address    Average round-trip time')
>>> last_distance = 0

>>> for hop in hops:
...     if last_distance + 1 != hop.distance:
...         print('Some routers are not responding')
...
...     # See the Hop class for details
...     print(f'{hop.distance}    {hop.address}    {hop.avg_rtt} ms')
...
...     last_distance = hop.distance
...

# Distance (ttl)    Address                 Average round-trip time
# 1                 10.0.0.1                5.196 ms
# 2                 194.149.169.49          7.552 ms
# 3                 194.149.166.54          12.21 ms
# *                 Some routers are not responding
# 5                 212.73.205.22           22.15 ms
# 6                 1.1.1.1                 13.59 ms
```

<br>

## ICMP sockets

If you want to create your own functions and classes using the ICMP protocol, you can use the `ICMPv4Socket` (for IPv4) and the `ICMPv6Socket` (for IPv6 only). These classes have many methods and attributes in common. They manipulate `ICMPRequest` and `ICMPReply` objects.

```
                                      ┌─────────────────┐
    ┌─────────────────┐   send(...)   │ ICMPSocket:     │   receive()   ┌─────────────────┐
    │   ICMPRequest   │ ────────────> │ ICMPv4Socket or │ ────────────> │    ICMPReply    │
    └─────────────────┘               │ ICMPv6Socket    │               └─────────────────┘
                                      └─────────────────┘
```

### ICMPRequest
A user-created object that represents an *ICMP ECHO_REQUEST*.

#### Definition
```python
ICMPRequest(destination, id, sequence, payload=None, payload_size=56, timeout=2, ttl=64, traffic_class=0)
```

#### Parameters / Getters
- `destination`

  The IP address of the gateway or host to which the message should be sent.

  - Type: `str`

- `id`

  The identifier of the request. Used to match the reply with the request.<br>
  In practice, a unique identifier is used for every ping process.

  - Type: `int`

- `sequence`

  The sequence number. Used to match the reply with the request.<br>
  Typically, the sequence number is incremented for each packet sent during the process.

  - Type: `int`

- `payload`

  The payload content in bytes. A random payload is used by default.

  - Type: `bytes`
  - Default: `None`

- `payload_size`

  The payload size. Ignored when the `payload` parameter is set.

  - Type: `int`
  - Default: `56`

- `timeout`

  The maximum waiting time for receiving a reply in seconds.

  - Type: `int` or `float`
  - Default: `2`

- `ttl`

  The time to live of the packet in seconds.

  - Type: `int`
  - Default: `64`

- `traffic_class`

  The traffic class of the packet. Provides a defined level of service to the packet by setting the DS Field (formerly TOS) or the Traffic Class field of the IP header. Packets are delivered with the minimum priority by default (Best-effort delivery).

  Intermediate routers must be able to support this feature.<br>
  *Only available on Unix systems. Ignored on Windows.*

  - Type: `int`
  - Default: `0`

#### Getters only
- `time`

  The timestamp of the ICMP request. Initialized to zero when creating the request and replaced by `ICMPv4Socket` or `ICMPv6Socket` with the time of sending.

  - Type: `float`

<br>

### ICMPReply
A class that represents an ICMP reply. Generated from an `ICMPSocket` object (`ICMPv4Socket` or `ICMPv6Socket`).

#### Definition
```python
ICMPReply(source, id, sequence, type, code, bytes_received, time)
```

#### Parameters / Getters
- `source`

  The IP address of the gateway or host that composes the ICMP message.

  - Type: `str`

- `id`

  The identifier of the request. Used to match the reply with the request.

  - Type: `int`

- `sequence`

  The sequence number. Used to match the reply with the request.

  - Type: `int`

- `type`

  The type of message.

  - Type: `int`

- `code`

  The error code.

  - Type: `int`

- `bytes_received`

  The number of bytes received.

  - Type: `int`

- `time`

  The timestamp of the ICMP reply.

  - Type: `float`

#### Methods
- `raise_for_status()`

  Throw an exception if the reply is not an *ICMP ECHO_REPLY*.<br>
  Otherwise, do nothing.

  - Raises `ICMPv4DestinationUnreachable`: If the ICMPv4 reply is type 3.
  - Raises `ICMPv4TimeExceeded`: If the ICMPv4 reply is type 11.
  - Raises `ICMPv6DestinationUnreachable`: If the ICMPv6 reply is type 1.
  - Raises `ICMPv6TimeExceeded`: If the ICMPv6 reply is type 3.
  - Raises `ICMPError`: If the reply is of another type and is not an *ICMP ECHO_REPLY*.

<br>

### ICMPv4Socket
Socket for sending and receiving ICMPv4 packets.

#### Definition
```python
ICMPv4Socket()
```

#### Methods
- `__init__()`

  *Constructor. Automatically called: do not call it directly.*

  - Raises `SocketPermissionError`: If the permissions are insufficient to create the socket.

- `__del__()`

  *Destructor. Automatically called: do not call it directly.*

  - Call the `close` method.

- `send(request)`

  Send a request to a host.

  This operation is non-blocking. Use the `receive` method to get the reply.

  - Parameter `ICMPRequest`: The ICMP request you have created.
  - Raises `SocketBroadcastError`: If a broadcast address is used and the corresponding option is not enabled on the socket (ICMPv4 only).
  - Raises `SocketUnavailableError`: If the socket is closed.
  - Raises `ICMPSocketError`: If another error occurs while sending.

- `receive()`

  Receive a reply from a host.

  This method can be called multiple times if you expect several responses (as with a broadcast address).

  - Raises `TimeoutExceeded`: If no response is received before the timeout defined in the request. This exception is also useful for stopping a possible loop in case of multiple responses.
  - Raises `SocketUnavailableError`: If the socket is closed.
  - Raises `ICMPSocketError`: If another error occurs while receiving.
  - Returns `ICMPReply`: An `ICMPReply` object containing the reply of the desired destination. See the `ICMPReply` class for details.

- `close()`

  Close the socket. It cannot be used after this call.

#### Getters only
- `is_closed`

  Indicate whether the socket is closed.

  - Type: `bool`

#### Getters / Setters
- `broadcast`

  Enable or disable the broadcast support on the socket.

  - Type: `bool`
  - Default: `False`

<br>

### ICMPv6Socket
Socket for sending and receiving ICMPv6 packets.

#### Definition
```python
ICMPv6Socket()
```

#### Methods
The same methods as for the `ICMPv4Socket` class.

<br>

### Exceptions
The library contains many exceptions to adapt to your needs:

```
ICMPLibError
 ├─ ICMPSocketError
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
- `ICMPSocketError`: Base class for ICMP sockets exceptions.
- `SocketPermissionError`: Raised when the permissions are insufficient to create a socket.
- `SocketUnavailableError`: Raised when an action is performed while the socket is closed.
- `SocketBroadcastError`: Raised when a broadcast address is used and the corresponding option is not enabled on the socket.
- `TimeoutExceeded`: Raised when a timeout occurs on a socket.
- `ICMPError`: Base class for ICMP error messages.
- `DestinationUnreachable`: Destination Unreachable message is generated by the host or its inbound gateway to inform the client that the destination is unreachable for some reason.
- `TimeExceeded`: Time Exceeded message is generated by a gateway to inform the source of a discarded datagram due to the time to live field reaching zero. A Time Exceeded message may also be sent by a host if it fails to reassemble a fragmented datagram within its time limit.

Use the `message` property to retrieve the error message.

`ICMPError` subclasses have properties to retrieve the response (`reply` property) and the specific message of the error (`message` property).

<br>

### Examples
#### Sockets in action
```python
def single_ping(address, timeout=2, id=PID):
    # Create an ICMP socket
    socket = ICMPv4Socket()

    # Create a request
    # See the ICMPRequest class for details
    request = ICMPRequest(
        destination=address,
        id=id,
        sequence=1,
        timeout=timeout)

    try:
        socket.send(request)

        # If the program arrives in this section,
        # it means that the packet has been transmitted

        reply = socket.receive()

        # If the program arrives in this section,
        # it means that a packet has been received
        # The reply has the same identifier and sequence number that
        # the request but it can come from an intermediate gateway

        reply.raise_for_status()

        # If the program arrives in this section,
        # it means that the destination host has responded to
        # the request

    except TimeoutExceeded as err:
        # The timeout has been reached
        # Equivalent to print(err.message)
        print(err)

    except DestinationUnreachable as err:
        # The reply indicates that the destination host is
        # unreachable
        print(err)

        # Retrieve the response
        reply = err.reply

    except TimeExceeded as err:
        # The reply indicates that the time to live exceeded
        # in transit
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

### How to resolve a FQDN / domain name?
Python has a method to do this in its libraries:
```python
>>> import socket
>>> socket.gethostbyname('github.com')
'140.82.118.4'
```

## Contributing

Comments and enhancements are welcome.

All development is done on [GitHub](https://github.com/ValentinBELYN/icmplib). Use [Issues](https://github.com/ValentinBELYN/icmplib/issues) to report problems and submit feature requests. Please include a minimal example that reproduces the bug.

## Donate

icmplib is completely free and open source. It has been fully developed on my free time. If you enjoy it, please consider donating to support the development.

- [:tada: Donate via PayPal](https://paypal.me/ValentinBELYN)

## License

Copyright 2017-2020 Valentin BELYN.

Code released under the GNU LGPLv3 license. See the [LICENSE](LICENSE) for details.
