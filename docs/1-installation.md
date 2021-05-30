# Installation

## Requirements

- Since icmplib 3, Python 3.7 or later is required to use the library.
- If you are using Python 3.6 and you cannot update it, you can still install icmplib 2.
- icmplib has been optimized to run on the most popular operating systems such as Linux, macOS and Windows.

## Installation and update

- **Install**

  The recommended way to install icmplib is to use `pip3`:

  ```shell
  $ pip3 install icmplib
  ```

- **Update**

  Before updating icmplib, take care to read the release notes carefully to avoid any incompatibilities with your applications.

  ```shell
  $ pip3 install --upgrade icmplib
  ```

## Imports

Add the following instructions into your project to import icmplib (only import what you need):

- **Basic functions**

  ```python
  from icmplib import ping, multiping, traceroute, resolve
  ```

- **Asynchronous functions**

  ```python
  from icmplib import async_ping, async_multiping, async_resolve
  ```

- **Sockets (advanced)**

  ```python
  from icmplib import ICMPv4Socket, ICMPv6Socket, AsyncSocket, ICMPRequest, ICMPReply
  ```

- **Exceptions**

  ```python
  from icmplib import ICMPLibError, NameLookupError, ICMPSocketError
  from icmplib import SocketAddressError, SocketPermissionError
  from icmplib import SocketUnavailableError, SocketBroadcastError, TimeoutExceeded
  from icmplib import ICMPError, DestinationUnreachable, TimeExceeded
  ```
