# Examples

## Built-in functions

- [ping](ping.py)
- [multiping](multiping.py)
- [traceroute](traceroute.py)

## Sockets (advanced)

- [verbose-ping](verbose_ping.py)

  This example shows how to reproduce the ping command using sockets of `icmplib`.

  *Output:*

  ```console
  PING 1.1.1.1: 56 data bytes

    64 bytes from 1.1.1.1: icmp_seq=0 time=12.061 ms
    64 bytes from 1.1.1.1: icmp_seq=1 time=12.597 ms
    64 bytes from 1.1.1.1: icmp_seq=2 time=12.475 ms
    64 bytes from 1.1.1.1: icmp_seq=3 time=10.822 ms

  Completed.
  ```

- [verbose-traceroute](verbose_traceroute.py)

  This example shows how to reproduce the traceroute command.

  *Output:*

  ```console
  Traceroute to ovh.com (198.27.92.1): 56 data bytes, 30 hops max

    1    192.168.0.254      192.168.0.254                9.86 ms
    2    194.149.164.56     194.149.164.56               4.61 ms
    3    213.186.32.181     be100-159.th2-1-a9.fr.eu     11.97 ms
    4    94.23.122.146      be102.rbx-g1-nc5.fr.eu       15.81 ms
    5    * * *
    6    37.187.231.75      be5.rbx-iplb1-a70.fr.eu      17.12 ms
    7    198.27.92.1        www.ovh.com                  10.87 ms

  Completed.
  ```

- [broadcast-ping](broadcast_ping.py)

  This example shows how to enable the broadcast support on a socket.

  *Output:*

  ```console
  PING 255.255.255.255: 56 data bytes

    64 bytes from 10.0.0.17: icmp_seq=0 time=1.065 ms
    64 bytes from 10.0.0.40: icmp_seq=0 time=1.595 ms
    64 bytes from 10.0.0.41: icmp_seq=0 time=9.471 ms

    64 bytes from 10.0.0.17: icmp_seq=1 time=0.983 ms
    64 bytes from 10.0.0.40: icmp_seq=1 time=1.579 ms
    64 bytes from 10.0.0.41: icmp_seq=1 time=9.345 ms

    64 bytes from 10.0.0.17: icmp_seq=2 time=0.916 ms
    64 bytes from 10.0.0.40: icmp_seq=2 time=2.031 ms
    64 bytes from 10.0.0.41: icmp_seq=2 time=9.554 ms

    64 bytes from 10.0.0.17: icmp_seq=3 time=1.112 ms
    64 bytes from 10.0.0.40: icmp_seq=3 time=1.384 ms
    64 bytes from 10.0.0.41: icmp_seq=3 time=9.565 ms

  Completed.
  ```
