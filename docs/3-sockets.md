# Sockets and classes

If you want to create your own functions and classes using the ICMP protocol, you can use the [`ICMPv4Socket`] (for IPv4 only) and the [`ICMPv6Socket`] (for IPv6 only). These classes have many methods and properties in common. They manipulate [`ICMPRequest`] and [`ICMPReply`] objects.

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

  The traffic class of the ICMP packet. Provides a defined level of service to the packet by setting the DS Field (formerly TOS) or the Traffic Class field of the IP header. Packets are delivered with the minimum priority by default (Best-effort delivery). Intermediate routers must be able to support this feature.

  *Only available on Unix systems. Ignored on Windows.*

  - Type: `int`
  - Default: `0`

#### Properties only

- `time`

  The timestamp of the ICMP request. Initialized to zero when creating the request and replaced by the `send` method of an ICMP socket with the time of sending.

  - Type: `float`

<br>

### ICMPReply

A class that represents an ICMP reply. Generated from an ICMP socket.

```python
ICMPReply(source, family, id, sequence, type, code, bytes_received, time)
```

#### Parameters and properties

- `source`

  The IP address of the host that composes the ICMP message.

  - Type: `str`

- `family`

  The address family. Can be set to `4` for IPv4 or `6` for IPv6 addresses.

  - Type: `int`

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

  - Raises [`DestinationUnreachable`]: If the destination is unreachable for some reason.
  - Raises [`TimeExceeded`]: If the time to live field of the ICMP request has reached zero.
  - Raises [`ICMPError`]: Raised for any other type and ICMP error code, except ICMP Echo Reply messages.

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

  - Raises [`SocketPermissionError`]: If the privileges are insufficient to create the socket.
  - Raises [`SocketAddressError`]: If the requested address cannot be assigned to the socket.
  - Raises [`ICMPSocketError`]: If another error occurs while creating the socket.

- `__enter__()`

  Return this object.

- `__exit__(type, value, traceback)`

  Call the `close` method.

- `__del__()`

  *Destructor. Automatically called: do not call it directly.*

  Call the `close` method.

- `send(request)`

  Send an ICMP request message over the network to a remote host.

  This operation is non-blocking. Use the `receive` method to get the reply.

  - Parameter `request` ([`ICMPRequest`]): The ICMP request you have created. If the socket is used in non-privileged mode on a Linux system, the identifier defined in the request will be replaced by the kernel.
  - Raises [`SocketBroadcastError`]: If a broadcast address is used and the corresponding option is not enabled on the socket (ICMPv4 only).
  - Raises [`SocketUnavailableError`]: If the socket is closed.
  - Raises [`ICMPSocketError`]: If another error occurs while sending.

- `receive(request=None, timeout=2)`

  Receive an ICMP reply message from the socket.

  This method can be called multiple times if you expect several responses as with a broadcast address.

  - Parameter `request` ([`ICMPRequest`]): The ICMP request to use to match the response. By default, all ICMP packets arriving on the socket are returned.
  - Parameter `timeout` (`int` or `float`): The maximum waiting time for receiving the response in seconds. Default to `2`.
  - Raises [`TimeoutExceeded`]: If no response is received before the timeout specified in parameters.
  - Raises [`SocketUnavailableError`]: If the socket is closed.
  - Raises [`ICMPSocketError`]: If another error occurs while receiving.

  Returns an [`ICMPReply`] object representing the response of the desired destination or an upstream gateway.

- `close()`

  Close the socket. It cannot be used after this call.

#### Properties only

- `sock`

  Return the underlying socket or `None` if the socket is closed.

  This property should only be used if the feature you want is not yet implemented. Some changes made to this socket may cause unexpected behavior or be incompatible with later versions of the library.

  Prefer to use the other methods and properties defined within this class if possible.

  - Type: `socket.socket` or `None`

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

- `blocking`

  Set the blocking or non-blocking mode of the socket.

  - Type: `bool`
  - Default: `False`

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

The same methods and properties as for the [`ICMPv4Socket`] class, except the `broadcast` property.

<br>

### AsyncSocket

A wrapper for ICMP sockets which makes them asynchronous.

```python
AsyncSocket(icmp_sock)
```

#### Parameters

- `icmp_sock`

  An ICMP socket. Once the wrapper is instantiated, this socket should no longer be used directly.

  - Type: [`ICMPv4Socket`] or [`ICMPv6Socket`]

#### Methods

The same methods as for the underlying ICMP socket, except:

- `receive(request=None, timeout=2)`

  This function is now non-blocking. It must be awaited.

- `detach()`

  Detach the socket from the wrapper and return it. The wrapper cannot be used after this call but the socket can be reused for other purposes.

- `close()`

  Detach the underlying socket from the wrapper and close it. Both cannot be used after this call.

#### Properties

The same properties as for the underlying ICMP socket, except:

- `is_closed`

  Indicate whether the underlying socket is closed or detached from this wrapper.

  - Type: `bool`

<br>

### Examples

#### Sockets in action

```python
from icmplib import *


def one_ping(address, timeout=2, id=PID):
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

    except TimeExceeded as err:
        # The reply indicates that the time to live exceeded in transit
        print(err)

    except ICMPLibError as err:
        # All other errors
        print(err)

    # Automatic socket closure (garbage collector)
```

#### Verbose ping

```python
from icmplib import *
from time import sleep


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
            print(f'  {reply.bytes_received} bytes from '
                  f'{reply.source}: ', end='')

            # We throw an exception if it is an ICMP error message
            reply.raise_for_status()

            # We calculate the round-trip time and we display it
            round_trip_time = (reply.time - request.time) * 1000

            print(f'icmp_seq={sequence} '
                  f'time={round(round_trip_time, 3)} ms')

            # We wait before continuing
            if sequence < count - 1:
                sleep(interval)

        except TimeoutExceeded:
            # The timeout has been reached
            print(f'  Request timeout for icmp_seq {sequence}')

        except ICMPError as err:
            # An ICMP error message has been received
            print(err)

        except ICMPLibError:
            # All other errors
            print('  An error has occurred.')

    print('\nCompleted.')


verbose_ping('1.1.1.1')

# PING 1.1.1.1: 56 data bytes
#
#   64 bytes from 1.1.1.1: icmp_seq=0 time=12.061 ms
#   64 bytes from 1.1.1.1: icmp_seq=1 time=12.597 ms
#   64 bytes from 1.1.1.1: icmp_seq=2 time=12.475 ms
#   64 bytes from 1.1.1.1: icmp_seq=3 time=10.822 ms
#
# Completed.
```

[`ICMPRequest`]: #ICMPRequest
[`ICMPReply`]: #ICMPReply
[`ICMPv4Socket`]: #ICMPv4Socket
[`ICMPv6Socket`]: #ICMPv6Socket
[`ICMPSocketError`]: 4-exceptions.md#ICMPSocketError
[`SocketAddressError`]: 4-exceptions.md#SocketAddressError
[`SocketPermissionError`]: 4-exceptions.md#SocketPermissionError
[`SocketUnavailableError`]: 4-exceptions.md#SocketUnavailableError
[`SocketBroadcastError`]: 4-exceptions.md#SocketBroadcastError
[`TimeoutExceeded`]: 4-exceptions.md#TimeoutExceeded
[`ICMPError`]: 4-exceptions.md#ICMPError
[`DestinationUnreachable`]: 4-exceptions.md#DestinationUnreachable
[`TimeExceeded`]: 4-exceptions.md#TimeExceeded
