# icmplib — Ping example & tests


## Simple use-case

One may ping IPv4 addresses:

    >>> from icmplib import ping
    >>> # Warning: this test uses internet connexion, and exact timing values
    ... # may differ from this example.  Some too random lines are skipped while
    ... # running doctest with "doctest: +SKIP".  However, the remote machine
    ... # (one.one.one.one) is still expected to be reachable.
    ...
    ... host = ping('1.1.1.1', count=5, interval=0.5, timeout=1,
    ...             privileged=False)

Then, in the reply, we may get multiple information:

- The IP address of the host that responded to the request

      >>> host.address
      '1.1.1.1'

- The minimum round-trip time in milliseconds

      >>> host.min_rtt  # doctest: +SKIP
      5.761

- The average round-trip time in milliseconds

      >>> host.avg_rtt  # doctest: +SKIP
      12.036

- The maximum round-trip time in milliseconds

      >>> host.max_rtt  # doctest: +SKIP
      16.207

- The list of round-trip times expressed in milliseconds

      >>> len(host.rtts)
      5
      >>> host.rtts  # doctest: +SKIP, +ELLIPSIS
      [11.595010757446289, 13.135194778442383, ..., 11.2398945671505]

- The number of requests transmitted to the remote host

      >>> host.packets_sent
      5

- The number of ICMP responses received from the remote host

      >>> host.packets_received
      5

- Packet loss occurs when packets fail to reach their destination.  Returns a
  float between 0 and 1 (all packets are lost)

      >>> host.packet_loss
      0.0

- The jitter in milliseconds, defined as the variance of the latency of packets
  flowing through the network.  At least two ICMP responses are required to
  calculate the jitter

      >>> host.jitter  # doctest: +SKIP
      4.575

- Indicates whether the host is reachable

      >>> host.is_alive
      True



## Ping IPv6

One may ping IPv6 addresses.  For most of the cases, this is as simple as IPv4
addresses:

    >>> IPv6_ADDRESS = "2606:4700:4700::1111"
    >>> host = ping(IPv6_ADDRESS, privileged=False)

(The address used is the IPv6 equivalent of 1.1.1.1 IPv4 address.  They are both
the address of the domain "one.one.one.one".)

    >>> host.is_alive
    True
    >>> host.address
    '2606:4700:4700::1111'
    >>> host.packets_sent
    4



## Ping localhost

This is exactly as one other IP address.  Works for IPv4 or IPv6.

    >>> host = ping("127.0.0.1", privileged=False)
    >>> host.is_alive
    True
    >>> host.address
    '127.0.0.1'
    >>> host.packets_sent
    4

    >>> host = ping("::1", privileged=False)
    >>> host.is_alive
    True
    >>> host.address
    '::1'
    >>> host.packets_sent
    4



## Ping link-local IPv6 addresses

With link-local addresses, you need to specify the name of the interface,
this way:

    >>> # Here is a too specific link-local address, so test is deactivated.
    ... # This may be improved with finding the current link-local address on
    ... # any interface of the current machine—but this requires `getifaddrs`,
    ... # available in C, not available in Python.  Waiting for it.  In the
    ... # meantime, you may change the address below with its own and activate
    ... # the test.
    ...
    ... host = ping("fe80::510a:de0e:26e0:def3%eth0", privileged=False)
    ...                # doctest: +SKIP
    >>> host.is_alive  # doctest: +SKIP
    True
    >>> host.address   # doctest: +SKIP
    'fe80::510a:de0e:26e0:def3%eth0'
    >>> host.packets_sent  # doctest: +SKIP
    4
