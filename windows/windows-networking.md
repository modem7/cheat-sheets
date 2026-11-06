# Windows Networking
Inspecting and configuring networking on Windows from the command line: classic tools (`ipconfig`, `netsh`, `route`, `netstat`) and the newer PowerShell cmdlets (`Get-NetIPConfiguration`, `Test-NetConnection`, `Resolve-DnsName`, `New-NetFirewallRule`). Run elevated for changes. Commands run in PowerShell ([[powershell]]) unless noted. See also [[windows-dns-server]], [[windows-troubleshooting]], [[wsl]] and Linux equivalents in [[linuxbasics]].

Documentation: [NetTCPIP module](https://learn.microsoft.com/en-us/powershell/module/nettcpip/), [NetSecurity module](https://learn.microsoft.com/en-us/powershell/module/netsecurity/)

## IP Configuration
COMMAND | DESCRIPTION
---|---
`ipconfig` | IP, mask and gateway of each adapter
`ipconfig /all` | Full detail: MAC, DHCP server, DNS servers, lease times
`ipconfig /release` / `ipconfig /renew` | Drop and request a DHCP lease
`ipconfig /flushdns` | Clear the DNS resolver cache
`ipconfig /displaydns` | Show the DNS resolver cache
`ipconfig /registerdns` | Re-register this host's records in DNS
`Get-NetIPConfiguration` | Summary per interface (IP, gateway, DNS)
`Get-NetIPAddress -AddressFamily IPv4` | All IPv4 addresses
`Get-NetAdapter` | Adapters with status, speed and MAC
`Get-NetAdapter \| Where Status -eq Up` | Active adapters
`Get-NetIPInterface` | Interface metrics and DHCP state
`New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress <IP> -PrefixLength 24 -DefaultGateway <GW>` | Set a static IP
`Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses <DNS1>,<DNS2>` | Set DNS servers
`Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ResetServerAddresses` | Back to DHCP-provided DNS
`Set-NetIPInterface -InterfaceAlias "Ethernet" -Dhcp Enabled` | Switch to DHCP (remove the static address and gateway first)
`Rename-NetAdapter -Name "Ethernet" -NewName "LAN"` | Rename an adapter
`Disable-NetAdapter -Name "Wi-Fi" -Confirm:$false` / `Enable-NetAdapter -Name "Wi-Fi"` | Disable or enable an adapter
`Get-NetConnectionProfile` | Network category: Public, Private or DomainAuthenticated
`Set-NetConnectionProfile -InterfaceAlias "Ethernet" -NetworkCategory Private` | Change the category (affects firewall profile)

## Test Connectivity
COMMAND | DESCRIPTION
---|---
`ping <HOST>` | ICMP echo (`-t` continuous, `-n 10` count, `-l 1400` size)
`Test-Connection <HOST> -Count 4` | PowerShell ping, returns objects
`Test-NetConnection <HOST>` | Ping plus resolved address and interface
`Test-NetConnection <HOST> -Port 443` | TCP port check (replaces telnet)
`Test-NetConnection <HOST> -Port 3389 -InformationLevel Quiet` | Just `True` or `False`
`Test-NetConnection <HOST> -TraceRoute` | Traceroute
`Test-NetConnection -ComputerName <HOST> -CommonTCPPort SMB` | Check a common service (`HTTP`, `RDP`, `WINRM`, `SMB`)
`1..1024 \| ForEach-Object { if ((Test-NetConnection <HOST> -Port $_ -WarningAction SilentlyContinue).TcpTestSucceeded) { $_ } }` | Slow port scan (use [[nmap]] for real scans)
`tracert <HOST>` | Classic traceroute (`-d` skips name lookups)
`pathping <HOST>` | Traceroute with per-hop loss statistics (takes about 5 minutes)
`curl.exe -I https://<HOST>` | HTTP header check with the bundled curl ([[curl]])
`Test-WSMan <HOST>` | Check WinRM ([[powershell-remote]])

Add `-WarningAction SilentlyContinue` to `Test-NetConnection` to hide warnings when ICMP is blocked.

## DNS
COMMAND | DESCRIPTION
---|---
`Resolve-DnsName <HOST>` | Lookup (A and AAAA)
`Resolve-DnsName <HOST> -Type MX` | Record type (`A`, `AAAA`, `CNAME`, `TXT`, `NS`, `SRV`, `PTR`)
`Resolve-DnsName <HOST> -Server <DNS-IP>` | Ask a specific DNS server
`Resolve-DnsName <HOST> -DnsOnly` | Skip hosts file, LLMNR and NetBIOS
`Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.<DOMAIN>` | Find domain controllers via DNS ([[active-directory]])
`Resolve-DnsName <IP>` | Reverse lookup (PTR)
`nslookup <HOST> <DNS-IP>` | Classic lookup (`set type=MX` interactive)
`Get-DnsClientServerAddress` | DNS servers per interface
`Get-DnsClientCache` | Resolver cache as objects
`Clear-DnsClientCache` | Flush the cache (same as `ipconfig /flushdns`)
`Get-DnsClientNrptPolicy` | Name Resolution Policy Table (DirectAccess, VPN)
`Add-DnsClientNrptRule -Namespace ".lab.local" -NameServers <DNS-IP>` | Send one domain to a specific DNS server
`Get-Content C:\Windows\System32\drivers\etc\hosts` | Hosts file (edit as admin)

A short checklist for "can't resolve a name": `ipconfig /all` (which DNS server), `Resolve-DnsName <HOST> -Server <DNS-IP>`, `Clear-DnsClientCache`, hosts file, VPN/NRPT rules. See [[dns-record-types]] for record types.

## Ports and Connections
COMMAND | DESCRIPTION
---|---
`netstat -ano` | All connections and listeners with owning PID
`netstat -ano \| findstr :443` | Filter by port
`netstat -abno` | Include the executable name (needs admin)
`Get-NetTCPConnection -State Listen` | Listening TCP ports as objects
`Get-NetTCPConnection -LocalPort 443` | Connections on a port
`Get-NetTCPConnection -State Established \| Group-Object RemoteAddress \| Sort Count -Desc` | Top remote peers
`Get-Process -Id <PID>` | Which process owns a PID
`Get-NetUDPEndpoint` | UDP listeners
`(Get-NetTCPConnection -LocalPort 8080).OwningProcess \| ForEach-Object { Get-Process -Id $_ }` | Process behind a port

## Routing
COMMAND | DESCRIPTION
---|---
`route print` | Routing table (IPv4 and IPv6)
`Get-NetRoute` | Routes as objects (`-AddressFamily IPv4`)
`Get-NetRoute -DestinationPrefix 0.0.0.0/0` | Default gateway route
`route add 10.10.0.0 mask 255.255.0.0 <GW>` | Add a temporary route (lost on reboot)
`route -p add 10.10.0.0 mask 255.255.0.0 <GW>` | Add a persistent route
`New-NetRoute -DestinationPrefix 10.10.0.0/16 -InterfaceAlias "Ethernet" -NextHop <GW>` | Add a route in PowerShell (persistent by default)
`Remove-NetRoute -DestinationPrefix 10.10.0.0/16 -Confirm:$false` | Remove a route
`route delete 10.10.0.0` | Remove a route (classic)
`Find-NetRoute -RemoteIPAddress <IP>` | Which route and source address would be used

## ARP and Neighbours
COMMAND | DESCRIPTION
---|---
`arp -a` | ARP table
`Get-NetNeighbor` | ARP/ND cache as objects (`-State Reachable`)
`Remove-NetNeighbor -IPAddress <IP> -Confirm:$false` | Drop one entry
`netsh interface ip delete arpcache` | Clear the ARP cache
`Get-NetAdapter \| Select Name,MacAddress` | Local MAC addresses

## Firewall (Windows Defender Firewall)
COMMAND | DESCRIPTION
---|---
`Get-NetFirewallProfile` | State of the Domain, Private and Public profiles
`Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled True` | Turn the firewall on (avoid disabling it)
`Get-NetFirewallRule -Enabled True -Direction Inbound` | Active inbound rules
`Get-NetFirewallRule -DisplayName "*Remote Desktop*"` | Search rules by name
`Get-NetFirewallRule -DisplayName "Allow HTTPS" \| Get-NetFirewallPortFilter` | Ports in a rule
`New-NetFirewallRule -DisplayName "Allow HTTPS In" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow` | Open an inbound port
`New-NetFirewallRule -DisplayName "Allow SSH from LAN" -Direction Inbound -Protocol TCP -LocalPort 22 -RemoteAddress 192.168.1.0/24 -Action Allow -Profile Private` | Restrict by source and profile
`New-NetFirewallRule -DisplayName "Allow MyApp" -Direction Inbound -Program "C:\Apps\myapp.exe" -Action Allow` | Allow a program
`New-NetFirewallRule -DisplayName "Block Outbound 25" -Direction Outbound -Protocol TCP -RemotePort 25 -Action Block` | Block outbound traffic
`Set-NetFirewallRule -DisplayName "Allow HTTPS In" -RemoteAddress 10.0.0.0/8` | Edit a rule
`Disable-NetFirewallRule -DisplayName "<NAME>"` / `Enable-NetFirewallRule -DisplayName "<NAME>"` | Toggle a rule
`Enable-NetFirewallRule -DisplayGroup "Remote Desktop"` | Enable a built-in group
`Remove-NetFirewallRule -DisplayName "<NAME>"` | Delete a rule
`Get-NetFirewallRule \| Where Direction -eq Inbound \| Where Action -eq Block` | Block rules
`netsh advfirewall show allprofiles` | Classic profile summary
`netsh advfirewall export C:\fw.wfw` / `netsh advfirewall import C:\fw.wfw` | Back up and restore firewall policy
`netsh advfirewall reset` | Reset to defaults (**removes custom rules**)
`netsh advfirewall set allprofiles logging droppedconnections enable` | Log dropped packets (default log `%systemroot%\system32\LogFiles\Firewall\pfirewall.log`)

Rule priority: explicit **Block** rules override **Allow** rules. The active profile follows the network category (see `Get-NetConnectionProfile`). Domain GPOs ([[group-policy]]) can override local rules. For `ufw` on Linux see [[ufw]].

## netsh
COMMAND | DESCRIPTION
---|---
`netsh interface ip show config` | IP settings per interface
`netsh interface ip set address "Ethernet" static <IP> <MASK> <GW>` | Set static IP
`netsh interface ip set address "Ethernet" dhcp` | Use DHCP
`netsh interface ip set dns "Ethernet" static <DNS>` | Set DNS
`netsh interface portproxy add v4tov4 listenport=<PORT> connectport=<PORT> connectaddress=<IP>` | Port forward (see [[wsl]])
`netsh interface portproxy show all` | List port proxies
`netsh winsock reset` | Reset Winsock (reboot after)
`netsh int ip reset` | Reset the TCP/IP stack (reboot after)
`netsh wlan show profiles` | Saved Wi-Fi networks
`netsh wlan show profile name="<SSID>" key=clear` | Show a saved Wi-Fi key (admin; it prints a secret)
`netsh wlan show interfaces` | Current Wi-Fi connection and signal
`netsh trace start capture=yes tracefile=C:\trace.etl` / `netsh trace stop` | Packet capture without extra software (convert the `.etl` for Wireshark with the `etl2pcapng` tool)
`netsh http show urlacl` | HTTP URL reservations

## Shares and Sessions
COMMAND | DESCRIPTION
---|---
`net use` | Mapped drives and sessions
`net use Z: \\<SERVER>\<SHARE> /persistent:yes` | Map a drive (prompts for credentials if needed)
`net use Z: /delete` | Remove the mapping
`New-SmbMapping -LocalPath Z: -RemotePath \\<SERVER>\<SHARE>` | PowerShell mapping
`Get-SmbShare` | Shares on this machine
`Get-SmbConnection` | Outgoing SMB connections
`Get-SmbSession` | Clients connected to this server
`Get-SmbOpenFile` | Files opened over SMB (`Close-SmbOpenFile` to close)
`net view \\<SERVER>` | Shares on a server

## Reset Network Stack
For when networking is broken beyond DNS (run elevated, then reboot):
```powershell
netsh winsock reset
netsh int ip reset
ipconfig /release
ipconfig /renew
ipconfig /flushdns
```
Also try `Restart-NetAdapter -Name "Ethernet"` and checking for stale VPN adapters with `Get-NetAdapter -IncludeHidden`.

## Not Verified
Commands were written from the Microsoft documentation and not executed. Cmdlet availability differs on Windows Server Core and in PowerShell 7 (some NetTCPIP cmdlets load through Windows PowerShell compatibility).
