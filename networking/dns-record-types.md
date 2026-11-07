# DNS Record Types
## Most common types of DNS Records
Type | Description
---|---
A|The record that holds the IP address of a domain.
AAAA|The record that contains the IPv6 address for a domain (as opposed to A records, which list the IPv4 address).
CNAME|Forwards one domain or subdomain to another domain, does NOT provide an IP address.
MX|Directs mail to an email server.
TXT|Lets an admin store text notes in the record. These records are often used for email security.
NS|Stores the name server for a DNS entry.
SOA|Stores admin information about a domain.
SRV|Specifies a port for specific services.
PTR|Provides a domain name in reverse-lookups.

## Newer and Security-Related Records
Type | Description
---|---
DS|‘Delegation signer’ record held at the parent zone. It links a child zone's DNSKEY to the chain of trust for DNSSEC.
TLSA|Publishes a certificate or key fingerprint so clients can verify TLS via DNSSEC (DANE), commonly used for SMTP.
HTTPS / SVCB|Service binding records that advertise HTTP/2, HTTP/3, ALPN and alternative endpoints for a name.
SOA fields|Serial, refresh, retry, expire and negative-cache TTL. Increase the serial on every zone change.

## Query Records with dig
COMMAND | DESCRIPTION
---|---
`dig example.com A +short` | IPv4 address
`dig example.com AAAA +short` | IPv6 address
`dig example.com MX +short` | Mail servers
`dig example.com TXT +short` | SPF, verification and other text
`dig example.com NS +short` | Authoritative name servers
`dig example.com SOA +short` | Zone start of authority
`dig example.com CAA +short` | Certificate authority restrictions
`dig -x 192.0.2.10 +short` | Reverse (PTR) lookup
`dig @1.1.1.1 example.com A` | Ask a specific resolver
`dig example.com ANY` | Usually refused or minimal today, ask for specific types instead
`dig +trace example.com` | Follow delegation from the root
`dig example.com DNSKEY +dnssec` | DNSSEC records

DNSSEC signing and validation: [DNSSEC](dnssec.md). On Windows use `Resolve-DnsName example.com -Type MX` (see [Windows DNS Server](../windows/windows-dns-server.md)). Encrypted lookups are covered in [DNS Encryption](dns-encryption.md). Mail records: [Mail Server DNS Records Cheat-Sheet](dns-record-mailserver.md).

## Less commonly used DNS Records
Type | Description
---|---
AFSDB|This record is used for clients of the Andrew File System (AFS) developed by Carnegie Mellon. The AFSDB record functions to find other AFS cells.
APL|The ‘address prefix list’ is an experimental record that specifies lists of address ranges.
CAA|This is the ‘certification authority authorization’ record, it allows domain owners state which certificate authorities can issue certificates for that domain. If no CAA record exists, then anyone can issue a certificate for the domain. These records are also inherited by subdomains.
DNSKEY|The ‘DNS Key Record’ contains a public key used to verify Domain Name System Security Extension (DNSSEC) signatures.
CDNSKEY|This is a child copy of the DNSKEY record, meant to be transferred to a parent.
CERT|The ‘certificate record’ stores public key certificates.
DHCID|The ‘DHCP Identifier’ stores info for the Dynamic Host Configuration Protocol (DHCP), a standardized network protocol used on IP networks.
DNAME|The ‘delegation name’ record creates a domain alias, just like CNAME, but this alias will redirect all subdomains as well. For instance if the owner of ‘example.com’ bought the domain ‘website.net’ and gave it a DNAME record that points to ‘example.com’, then that pointer would also extend to ‘blog.website.net’ and any other subdomains.
HIP|This record uses ‘Host identity protocol’, a way to separate the roles of an IP address; this record is used most often in mobile computing.
IPSECKEY|The ‘IPSEC key’ record works with the Internet Protocol Security (IPSEC), an end-to-end security protocol framework and part of the Internet Protocol Suite (TCP/IP).
LOC|The ‘location’ record contains geographical information for a domain in the form of longitude and latitude coordinates.
NAPTR|The ‘name authority pointer’ record can be combined with an SRV record to dynamically create URI’s to point to based on a regular expression.
NSEC|The ‘next secure record’ is part of DNSSEC, and it’s used to prove that a requested DNS resource record does not exist.
RRSIG|The ‘resource record signature’ is a record to store digital signatures used to authenticate records in accordance with DNSSEC.
RP|This is the ‘responsible person’ record and it stores the email address of the person responsible for the domain.
SSHFP|This record stores the ‘SSH public key fingerprints’; SSH stands for Secure Shell and it’s a cryptographic networking protocol for secure communication over an unsecure network.
