# UniFi Protect
UniFi Protect is Ubiquiti's camera and recording application. It runs on a UniFi OS console such as a UNVR or a Cloud Gateway with storage. Much of what follows came from search summaries and third-party pages and is marked unverified. Check Ubiquiti's own articles before relying on it.

Documentation: [UniFi Help Center](https://help.ui.com/) · [Home Assistant UniFi Protect](https://www.home-assistant.io/integrations/unifiprotect/)

## Recording Modes
Per camera: Always, Detection Only, or Never. Retention and the purge order (oldest first is commonly reported) were **not verified**.

## Streams
- Enable RTSPS in the camera's settings, Advanced, then pick Low, Medium or High.
- RTSPS is reported on port 7441, and plain RTSP on 7447 by removing the `s` from the URL. These ports come from community and Home Assistant sources only.
- ONVIF support for third-party cameras arrived in Protect 5.0. Feature depth varies by camera.

```bash
ffplay "rtsps://<CONSOLE_IP>:7441/<STREAM_ALIAS>?enableSrtp"
```

The URL form above comes from the stream settings page, not from Ubiquiti documentation, so copy the exact URL the UI shows.

## Backups
Settings, Control Plane, Backups, then Restore. Backups cover configuration and **not recordings**. This path moves settings between a UDM Pro and a UNVR. See [UniFi Backups and Migration](unifi-backups.md).

## Home Assistant
The Home Assistant integration needs Protect 7.2.105 or newer on a UniFi OS console, and an API key. A local user is optional and unlocks more entities. Live feeds use RTSPS, and camera speaker audio needs UDP 7004. See [Home Assistant](../apps/home-assistant.md) and [UniFi API and Automation](unifi-api-automation.md).

## Network Tips
- Put cameras on their own VLAN with no internet access, and allow only the console to reach them ([UniFi Firewall and VPN](unifi-firewall-vpn.md)).
- Use PoE switches with enough budget for cameras.
- Camera disconnects are most often cabling, PoE power or VLAN issues, but no official fixes were verified.

## Related Applications
- **Access:** door access control (readers and intercoms).
- **Talk:** a VoIP phone system.
Both run on UniFi OS. They are described here only by name.

## Not Verified
Hardware specs, storage and retention behaviour, adopting cameras from another Protect, user permissions, ONVIF compatibility list, RTSP ports.

## See Also
- [UniFi](unifi.md)
- [UniFi Backups and Migration](unifi-backups.md)
- [UniFi API and Automation](unifi-api-automation.md)
- [Home Assistant](../apps/home-assistant.md)
