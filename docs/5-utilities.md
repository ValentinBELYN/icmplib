# Utilities

### resolve

Resolve a hostname or FQDN to an IP address. Depending on the name specified in parameters, several IP addresses may be returned.

This function relies on the DNS name server configured on your operating system.

```python
resolve(name, family=None)
```

#### Parameters

- `name`

  A hostname or a Fully Qualified Domain Name (FQDN).

  - Type: `str`

- `family`

  The address family. Can be set to `4` for IPv4 or `6` for IPv6 addresses. By default, this function searches for IPv4 addresses first for compatibility reasons (A DNS lookup) before searching for IPv6 addresses (AAAA DNS lookup).

  - Type: `int`
  - Default: `None`

#### Return value

- A list of IP addresses corresponding to the name passed as a parameter.

#### Exceptions

- [`NameLookupError`]

  If you pass a hostname or FQDN in parameters and it does not exist or cannot be resolved.

#### Example

```python
>>> from icmplib import resolve

>>> resolve('one.one.one.one')
['1.0.0.1', '1.1.1.1']

>>> resolve('localhost')
['127.0.0.1']

>>> resolve('ipv6.google.com')
['2a00:1450:4007:813::200e']
```

<br>

### async_resolve

Resolve a hostname or FQDN to an IP address. Depending on the name specified in parameters, several IP addresses may be returned.

This function relies on the DNS name server configured on your operating system.

*This function is non-blocking.*

```python
async_resolve(name, family=None)
```

#### Parameters, return value and exceptions

The same parameters, return values and exceptions as for the [`resolve`](#resolve) function.

#### Example

```python
>>> import asyncio
>>> from icmplib import async_resolve

>>> asyncio.run(async_resolve('one.one.one.one'))
['1.0.0.1', '1.1.1.1']

>>> asyncio.run(async_resolve('localhost'))
['127.0.0.1']

>>> asyncio.run(async_resolve('ipv6.google.com'))
['2a00:1450:4007:813::200e']
```

<br>

### is_hostname

Indicate whether the specified name is a hostname or an FQDN.

```python
is_hostname(address)
```

#### Example

```python
>>> from icmplib import is_hostname

>>> is_hostname('one.one.one.one')
True

>>> is_hostname('localhost')
True

>>> is_hostname('127.0.0.1')
False

>>> is_hostname('2a00:1450:4007:813::200e')
False
```

<br>

### is_ipv4_address

Indicate whether the specified address is an IPv4 address.

This function does not perform a strict checking. Its does not check if each byte of the IP address is within the allowed range.

This function has been designed to be fast.

```python
is_ipv4_address(address)
```

#### Example

```python
>>> from icmplib import is_ipv4_address

>>> is_ipv4_address('one.one.one.one')
False

>>> is_ipv4_address('localhost')
False

>>> is_ipv4_address('127.0.0.1')
True

>>> is_ipv4_address('2a00:1450:4007:813::200e')
False
```

<br>

### is_ipv6_address

Indicate whether the specified address is an IPv4 address.

This function does not perform a strict checking. Its does not check if each byte of the IP address is within the allowed range.

This function has been designed to be fast.

```python
is_ipv6_address(address)
```

#### Example

```python
>>> from icmplib import is_ipv6_address

>>> is_ipv6_address('one.one.one.one')
False

>>> is_ipv6_address('localhost')
False

>>> is_ipv6_address('127.0.0.1')
False

>>> is_ipv6_address('2a00:1450:4007:813::200e')
True
```

[`NameLookupError`]: 4-exceptions.md#NameLookupError
