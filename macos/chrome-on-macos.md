# Google Chrome

## Advanced

### No "Proceed Anyway" Option

Chrome won't show a "Proceed Anyway" button on some invalid certificate errors (`NET::ERR_CERT_INVALID`, HSTS sites). Use the hidden bypass as a workaround, **only for sites you trust** such as your own lab hosts.

1. Click on the error page so it has focus
2. Type `thisisunsafe` (nothing appears on screen, the page reloads)

The keyword has changed in the past, so if it stops working search for the current phrase. The proper fix is a trusted certificate: see [SSL Certificates Cheat-Sheet](../misc/ssl-certs.md) to trust your own CA, or use Let's Encrypt via [Cert-Manager](../apps/cert-manager.md) or [Traefik](../apps/traefik.md).

### Useful Internal Pages
URL | DESCRIPTION
---|---
`chrome://flags` | Experimental features
`chrome://net-internals/#hsts` | Delete a domain's HSTS entry (search for the domain, then delete)
`chrome://net-internals/#dns` | DNS cache (or `chrome://net-internals/#dns` clear host cache)
`chrome://settings/certificates` | Certificate manager
`chrome://version` | Version and profile path
`chrome://inspect` | Debug remote targets
`chrome://gpu` | GPU status

`chrome://flags/#allow-insecure-localhost` allows invalid certificates on `localhost` only.

### Keyboard Shortcuts (macOS)
SHORTCUT | DESCRIPTION
---|---
`Cmd`+`L` | Focus the address bar
`Cmd`+`T` / `Cmd`+`W` | New / close tab
`Cmd`+`Shift`+`T` | Reopen closed tab
`Cmd`+`Option`+`Left` / `Right` | Previous / next tab
`Cmd`+`Option`+`I` | Developer tools
`Cmd`+`Shift`+`R` | Hard reload (bypass cache)
`Cmd`+`Shift`+`N` | Incognito window
`Cmd`+`Shift`+`Delete` | Clear browsing data
`Cmd`+`Option`+`J` | Open the console

See [MacOS keyboard shortcuts](macos-shortcuts.md) for general macOS keys.
