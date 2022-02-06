# Changelog

All notable changes to this project will be documented in this file.

## [v3.0.3](https://github.com/ValentinBELYN/icmplib/releases/tag/v3.0.3) - 2022-02-06
- Add the `sock` property to the `ICMPSocket` class.

## [v3.0.2](https://github.com/ValentinBELYN/icmplib/releases/tag/v3.0.2) - 2021-10-31
- Add support for IPv6 addresses with zone index.
- The `payload` property of an `ICMPRequest` now returns a random value if the payload is not defined instead of `None`.
- Optimize imports.

## [v3.0.1](https://github.com/ValentinBELYN/icmplib/releases/tag/v3.0.1) - 2021-08-14
- Make the `SocketPermissionError` more explicit when the OS does not allow instantiation of unprivileged sockets.
- Delete unnecessary properties from exceptions.
- Improve SEO on GitHub.

## [v3.0.0](https://github.com/ValentinBELYN/icmplib/releases/tag/v3.0.0) - 2021-06-01
**icmplib 3.0 is here! :rocket:**

- The library is now asynchronous!
  - Introduce new functions: `async_ping`, `async_multiping` and `async_resolve`.
  - Add a new `AsyncSocket` class to make an ICMP socket asynchronous.
- Rewrite models:
  - All the properties of `Host` and `Hop` classes are now lazy.
  - Add new properties to the `Host` and `Hop` classes: you can retrieve the list of round-trip times and calculate the jitter.
  - Add the metaclass `__str__` to visualize the results more easily.
- Rewrite the `ping`, `multiping` and `traceroute` functions:
  - The identifier of ICMP requests is now handled automatically by the library.
  - Add the ability to set the address family if a hostname or an FQDN is specified.
  - A new implementation is used for the `multiping` function. It should be more reliable.
  - The `multiping` function is now in a dedicated module.
- Rewrite the documentation to help you get started with icmplib.
- Improve the `resolve` function to return all IP addresses found.
- Add the `is_hostname` function to check if a string is a hostname or an FQDN.
- Delete the experimental class `BufferedSocket`, replaced by `AsyncSocket`.
- Performance and compatibility improvement.
- Many other small changes and fixes.

Special thanks to [@JonasKs](https://github.com/JonasKs) and [@bdraco](https://github.com/bdraco) for their suggestions, advice and feedback!

> Python 3.7 or later is now required.

## [v2.1.1](https://github.com/ValentinBELYN/icmplib/releases/tag/v2.1.1) - 2021-03-21
- :bug: Revert changes made to the `traceroute` function due to a bug.

> This version is the last of the 2.x branch. See you soon for the release of icmplib 3.0!

## [v2.1.0](https://github.com/ValentinBELYN/icmplib/releases/tag/v2.1.0) - 2021-03-20
- Add a `family` parameter to the `resolve` function to define the address family.
- Improve the reliability of the results of the `traceroute` function.

## [v2.0.2](https://github.com/ValentinBELYN/icmplib/releases/tag/v2.0.2) - 2021-02-07
- Rename the default branch from `master` to `main`.
- Add more details about the `privileged` parameter in the `README` file (part 2).
- :bug: Fix a bug preventing the `traceroute` function to work with IPv6 addresses (part 2).

## [v2.0.1](https://github.com/ValentinBELYN/icmplib/releases/tag/v2.0.1) - 2020-12-12
- Handle `EACCES` errors at sockets level.
- Add some details about the `privileged` parameter in the `README` file.
- :bug: Fix a bug preventing the `traceroute` function to work with IPv6 addresses.

## [v2.0.0](https://github.com/ValentinBELYN/icmplib/releases/tag/v2.0.0) - 2020-11-15
**icmplib 2.0 is here! :rocket:**

- New library architecture.
- Add a new `multiping` function. This function will be faster and more memory efficient.
- Add the ability to use the library without root privileges.
- Add the ability to set a source IP address for sending your ICMP packets.
- Add a `first_hop` parameter to the `traceroute` function to set the initial time to live value ([@scoulondre](https://github.com/scoulondre)).
- Add two new exceptions:
  - `NameLookupError`: raised when the requested name does not exist or cannot be resolved.
  - `SocketAddressError`: raised when the requested address cannot be assigned to the socket.
- Add a new `BufferedSocket` class (experimental) to send several packets simultaneously without waiting for a response.
- The `receive` method of sockets can receive all incoming packets.
- Throw new exceptions when instantiating sockets, sending and receiving packets.
- Improve the `resolve` function:
  - A `NameLookupError` is now raised if the requested name does not exist or cannot be resolved.
- Improve compatibility with Linux, macOS and Windows.
- Delete deprecated properties.
- Update docstrings, examples and documentation.

> Compatibility with existing programs is maintained.

## [v1.2.2](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.2.2) - 2020-10-10
- Add support for hostnames and FQDN resolution to IPv6 addresses.
- Performance improvement.

## [v1.2.1](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.2.1) - 2020-09-26
- :bug: Fix an issue in the `traceroute` function which gave the wrong value for the `avg_rtt` property ([@patrickfnielsen](https://github.com/patrickfnielsen)).

## [v1.2.0](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.2.0) - 2020-09-12
- Add the ability to modify the traffic class of ICMP packets.
- Add new optional parameters to the `traceroute` function.
- Add a new exception `SocketUnavailableError` when an action is performed while a socket is closed.
- Add a warning message on deprecated properties.
- Explicit closure of sockets on built-in functions.
- :bug: Fix a bug when ICMP responses are not correctly formatted (part 2).

## [v1.1.3](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.1.3) - 2020-09-03
- :bug: Fix a bug when ICMP responses are not correctly formatted.

## [v1.1.2](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.1.2) - 2020-08-29
- :bug: Fix a compatibility issue.

## [v1.1.1](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.1.1) - 2020-07-10
- :bug: Fix a bug when the source host does not have an IP address.

## [v1.1.0](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.1.0) - 2020-06-25
- Add support for odd size payloads.
- Normalize the names of variables and properties:
  - `ICMPReply` class: the `received_bytes` property is deprecated. Use `bytes_received` instead.
  - `Host` and `Hop` classes: the `transmitted_packets` property is deprecated. Use `packets_sent` instead.
  - `Host` and `Hop` classes: the `received_packets` property is deprecated. Use `packets_received` instead.
- Normalize docstrings.
- Optimizations.

## [v1.0.4](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.0.4) - 2020-06-14
- Add the `is_closed` property to the `ICMPSocket` class.
- Round round-trip time values by default.
- Add an index for examples.
- :bug: Fix a bug in the `multiping` function where the `id` parameter was ignored.
- :bug: Fix a bug in the `ICMPSocket` class when instantiated without root privileges.

## [v1.0.3](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.0.3) - 2020-05-09
- Add the ability to customize the payload.
- Improve the `ping` and `multiping` functions:
  - You can pass arguments to the `ICMPRequest` object using keywords arguments `**kwargs`.
- Update some docstrings.
- Add new examples.

## [v1.0.2](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.0.2) - 2019-10-20
- Change the license. This project now uses the more permissive license LGPLv3.

## [v1.0.1](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.0.1) - 2019-10-07
- Add some examples.
- Rename `model.py` to `models.py`.
- Update setup keywords.

## [v1.0.0](https://github.com/ValentinBELYN/icmplib/releases/tag/v1.0.0) - 2019-09-29
- :tada: Initial release.
