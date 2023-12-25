import argparse
import ipaddress
from icmplib import ping


def findmtu(host, verbose=False, debug=False):
    """
    Find the PMTU to the specified host.
    Searches the range
    Host is an IPv4 or IPv6 address.
    """

    # These headers get added to the ping payload to get to MTU
    SIZE_ICMP_HDR = 8
    SIZE_IPV4_HDR = 20
    SIZE_IPV6_HDR = 40

    # These Ethernet headers are not included in the MTU.
    # Subtract them from the size-on-wire to get MTU.
    SIZE_ETH2_HDR = 14

    if isinstance(ipaddress.ip_address(host), ipaddress.IPv6Address):
        size_ip_hdr = SIZE_IPV6_HDR
    else:
        size_ip_hdr = SIZE_IPV4_HDR

    lower = 900
    upper = 10000
    MTU = lower

    if verbose:
        print(f"\nhost: {host}")

    result = ping(host)
    if not result.is_alive:
        return 0

    timeout = 1.5 * result.max_rtt / 1E3
    interval = 0.5 * result.max_rtt / 1E3
    if verbose:
        print(result)
        print(f'PMTU discovery timeout: {timeout}, interval: {interval}')

    test_size = 1700
    while upper - lower > 1:
        test_MTU = test_size + SIZE_ICMP_HDR + size_ip_hdr
        if verbose:
            if debug:
                s = f" - MTU search range: {upper}-{lower} - {test_MTU+SIZE_ETH2_HDR} bytes on wire "
            else:
                s = ""
            print(
                f"checking frame size {test_MTU} {s}",
                end="",
                flush=True,
            )
        result = ping(
            host,
            count=2,
            interval=interval,
            timeout=timeout,
            payload_size=test_size,
            pmtudisc_opt="do",
        )
        if result.is_alive:
            lower = test_size
            MTU = test_MTU
            if verbose:
                print("✅")
        else:
            upper = test_size
            if verbose:
                print("❌")

        test_size = lower + int((upper - lower) / 2)

    return MTU


parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
parser.add_argument("-d", "--debug", help="debug output", action="store_true")
parser.add_argument("hosts", help="one or more hosts to test", nargs='+')
args = parser.parse_args()

for host in args.hosts:
    mtu = findmtu(host, verbose=args.verbose, debug=args.debug)
    if mtu:
        print(f"host: {host} MTU: {mtu}")
    else:
        print("{host} is unreachable")
