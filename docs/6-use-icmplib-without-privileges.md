# Use icmplib without root privileges

- **Step 1: adapt your code**

  To use icmplib without root privileges, you must set the `privileged` parameter to `False` on the [`ping`] and [`multiping`] functions, as well as their asynchronous variants and the low level classes.

  By disabling this parameter, icmplib let the kernel handle some parts of the ICMP headers.

  The [`traceroute`] function does not have this parameter. It should always be run as root to receive ICMP Time Exceeded messages from gateways.

- **Step 2: allow this feature on your operating system**

  On some Linux systems, you must allow this feature:

  ```shell
  $ echo 'net.ipv4.ping_group_range = 0 2147483647' | sudo tee -a /etc/sysctl.conf
  $ sudo sysctl -p
  ```

  You can check the current value with the following command:

  ```shell
  $ sysctl net.ipv4.ping_group_range
  net.ipv4.ping_group_range = 0 2147483647
  ```

  *Since Ubuntu 20.04 LTS, this manipulation is no longer necessary.*

  [Read more about `ping_group_range` on www.kernel.org]

[`ping`]: 2-functions.md#ping
[`multiping`]: 2-functions.md#multiping
[`traceroute`]: 2-functions.md#traceroute
[Read more about `ping_group_range` on www.kernel.org]: https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt
