"""OSift IP validation filter — deployed to /opt/pr0t31n/OSift/ip_filter.py

Rejects bogus IPs that OSift's regex-based extraction mis-captures from
text: version numbers, dates, DNS resolvers, network/broadcast addresses,
and reserved ranges.

Usage:
    from ip_filter import validate_ip, filter_ips
"""

import re

_KNOWN_DNS_RESOLVERS = frozenset({
    "1.1.1.1", "1.0.0.1", "1.0.1.1",
    "8.8.8.8", "8.8.4.4",
    "9.9.9.9", "9.9.9.10",
    "208.67.222.222", "208.67.220.220",
    "64.6.64.6", "64.6.65.6",
    "149.112.112.112",
    "185.228.168.9", "185.228.169.9",
    "77.88.8.8", "77.88.8.1",
    "4.2.2.1", "4.2.2.2", "4.2.2.3", "4.2.2.4", "4.2.2.5", "4.2.2.6",
    "76.76.19.19", "76.223.122.150",
    "94.140.14.14", "94.140.15.15",
    "199.85.126.10", "199.85.127.10",
    "156.154.70.1", "156.154.71.1",
})

_IP_OCTET_RE = re.compile(
    r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
)


def validate_ip(ip_str):
    """Return True if ip_str is a plausible scan-target IPv4 address.

    Rejects leading-zero octets (date/version artifacts like 07.03.16.06),
    known DNS resolvers, network/broadcast addresses, loopback, multicast,
    and reserved ranges.
    """
    if not ip_str:
        return False
    cleaned = re.sub(r'^https?://', '', str(ip_str)).split('/')[0].split(':')[0].strip()
    if not cleaned:
        return False
    m = _IP_OCTET_RE.match(cleaned)
    if not m:
        return True  # not an IP at all (hostname) — let scope checking handle it
    raw_octets = [m.group(i) for i in range(1, 5)]
    # Leading zeros in any octet → date/version artifact (07.03.16.06, 02.06.18.4)
    if any(len(o) > 1 and o[0] == '0' for o in raw_octets):
        return False
    octets = [int(o) for o in raw_octets]
    if any(o > 255 for o in octets):
        return False
    if cleaned in _KNOWN_DNS_RESOLVERS:
        return False
    # Network addresses: x.0.0.0 (/8 base), x.x.0.0 (/16 base)
    if octets[1] == 0 and octets[2] == 0 and octets[3] == 0:
        return False
    if octets[2] == 0 and octets[3] == 0:
        return False
    # Broadcast/network: x.x.x.0
    if octets[3] == 0:
        return False
    # Loopback
    if octets[0] == 127 or octets[0] == 0:
        return False
    # Multicast + reserved (224-255)
    if octets[0] >= 224:
        return False
    # Link-local
    if octets[0] == 169 and octets[1] == 254:
        return False
    return True


def filter_ips(ip_list):
    """Filter a list of IP strings, returning only valid target IPs."""
    return [ip for ip in ip_list if validate_ip(ip)]
