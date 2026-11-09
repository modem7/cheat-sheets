# UniFi WiFi
SSID and access point settings that matter in a homelab: bands, 6 GHz, IoT networks, multicast and roaming. Settings move between releases, so confirm names in your version.

Documentation: [SSID and AP Settings Overview](https://help.ui.com/hc/en-us/articles/32065480092951) · [Getting Started with 6 GHz](https://help.ui.com/hc/en-us/articles/20407971377815) · [Unable to Connect to WiFi](https://help.ui.com/hc/en-us/articles/23283660456599)

## SSIDs
- One SSID on several bands is preferred over a 6 GHz-only SSID.
- Tie each SSID to a network, see [UniFi Networks and VLANs](unifi-networks-vlans.md).
- Use a separate SSID for IoT and another for guests.

## Bands and Security
SETTING | NOTES
---|---
6 GHz | Needs WPA3 or OWE. Turning it on defaults to WPA2/3 with PMF optional
PMF | Optional (default), Required (WPA3 and OWE), or Disabled. It cannot be disabled on WPA2/3 or WPA3
Band steering | Now uses BSS transition frames. The old AP-level method is deprecated
Multicast Enhancement | Converts multicast to unicast
DTIM | Defaults 1 on 2.4 GHz and 3 on 5 and 6 GHz
MLO | Multi-link operation, a WiFi 7 option

## IoT SSID
Ubiquiti's advice for devices that will not connect:
- Create a separate SSID with 6 GHz off and WPA2.
- WPA3 is not recommended on 2.4 GHz.
- Disabling PMF is suggested only for troubleshooting.
- Keep the SSID on an IoT network with a firewall zone, see [UniFi Firewall and VPN](unifi-firewall-vpn.md).

## Roaming
Fast roaming (802.11r) and minimum RSSI are described only by third-party guides and were **not verified** officially. Change one setting at a time and test with the devices you care about, because some IoT clients dislike 802.11r.

## Not Covered or Unverified
Radio AI, WiFi Experience, Zero-Wait DFS, hotspot portals, PPSK, WiFi scheduler, mesh uplinks and channel width guidance were not researched.

## See Also
- [UniFi](unifi.md)
- [UniFi Networks and VLANs](unifi-networks-vlans.md)
- [UniFi Firewall and VPN](unifi-firewall-vpn.md)
- [Home Assistant](../apps/home-assistant.md)
