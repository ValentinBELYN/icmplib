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

    while upper - lower > 1:
        test_size = lower + int((upper - lower) / 2)
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
            interval=0.5,
            timeout=1,
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

    return MTU


hosts = ["10.0.0.1", "fc00::1", "10.1.0.0", "fc00:1::2", "10.1.0.1", "fc00:1::1"]

for host in hosts:
    mtu = findmtu(host, verbose=False, debug=False)
    print(f"host: {host} MTU: {mtu}")