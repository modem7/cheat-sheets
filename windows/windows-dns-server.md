# Windows DNS Server

In Windows Server, DNS is a server role that you can install by using Server Manager or Windows PowerShell commands. If you are installing a new Active Directory forest and domain, DNS is automatically installed with Active Directory as the Global Catalogue server for the forest and domain. For record types see [DNS Record Types](../networking/dns-record-types.md), and for PowerShell basics see [PowerShell Cheat-Sheet](powershell.md).

---
## Install Windows DNS Server role
```powershell
Install-WindowsFeature -Name DNS -IncludeManagementTools
```
On a workstation, install only the PowerShell module with `Add-WindowsCapability -Online -Name Rsat.Dns.Tools~~~~0.0.1.0`.

---
## Manage DNS Server via PowerShell
Most cmdlets accept `-ComputerName <dns-server>` to manage a remote server.

**Check the DNS Server module is available**
```powershell
Get-Module DnsServer -ListAvailable
```

**List zones**
```powershell
Get-DnsServerZone
```

**Show current DNS Records in Zone**
```powershell
Get-DnsServerResourceRecord -ZoneName <your-dns-zone>
```

### Zones
```powershell
Add-DnsServerPrimaryZone -Name <your-dns-zone> -ReplicationScope Domain
Add-DnsServerPrimaryZone -NetworkId "192.168.1.0/24" -ReplicationScope Domain   # reverse zone
Remove-DnsServerZone -Name <your-dns-zone> -Force
```
`-ReplicationScope` applies to Active Directory-integrated zones. For a standalone server use `-ZoneFile "<zone>.dns"` instead.

### Get/Create/Modify DNS Record

**Show DNS Record**
```powershell
Get-DnsServerResourceRecord -ZoneName <your-dns-zone> -Name <dns-name>
```

**Delete DNS Record**
```powershell
Get-DnsServerResourceRecord -ZoneName <your-dns-zone> -Name <dns-name> | Remove-DnsServerResourceRecord -ZoneName <your-dns-zone> -Force
```
Add `-WhatIf` to check what would be deleted first.

**Add DNS Records**
```powershell
Add-DnsServerResourceRecordA -Name <dns-name> -ZoneName <your-dns-zone> -AllowUpdateAny -IPv4Address <ip-address> -TimeToLive 01:00:00
Add-DnsServerResourceRecordCName -Name <alias> -ZoneName <your-dns-zone> -HostNameAlias <target.your-dns-zone>
Add-DnsServerResourceRecordPtr -Name <last-octet> -ZoneName 1.168.192.in-addr.arpa -PtrDomainName <host.your-dns-zone>
Add-DnsServerResourceRecordMX -Name "." -ZoneName <your-dns-zone> -MailExchange <mail.your-dns-zone> -Preference 10
Add-DnsServerResourceRecord -Txt -Name "." -ZoneName <your-dns-zone> -DescriptiveText "v=spf1 mx -all"
```
`-TimeToLive` takes a time span (`hh:mm:ss`), not seconds. See [Mail Server DNS Records Cheat-Sheet](../networking/dns-record-mailserver.md) for mail records.

### Forwarders, Cache and Testing
COMMAND | DESCRIPTION
---|---
`Get-DnsServerForwarder` | Show forwarders
`Set-DnsServerForwarder -IPAddress 1.1.1.1,9.9.9.9` | Set forwarders
`Clear-DnsServerCache -Force` | Clear the server cache
`Clear-DnsClientCache` | Clear the local client cache
`Resolve-DnsName <name> -Server <dns-server> -Type A` | Query a specific server
`Restart-Service DNS` | Restart the DNS service
`dnscmd /info` | Legacy command line tool
`Get-DnsServerStatistics` | Query counters

See [DNS over TLS (DoT)](../networking/dns-over-tls.md) and [DNS over HTTPS (DoH)](../networking/dns-over-https.md) for encrypted DNS in general. Whether the Windows Server DNS role itself supports it depends on the Windows Server version, which was not checked here.
