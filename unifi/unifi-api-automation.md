# UniFi API and Automation
The official local Integration API, Terraform, the Home Assistant integrations and Unpoller for monitoring. API keys need a UniFi OS console or UniFi OS Server. The legacy self-hosted Network app does not support them.

Documentation: [UniFi developer docs](https://developer.ui.com/) · [Unpoller](https://unpoller.com/docs/install/configuration) · [Home Assistant UniFi](https://www.home-assistant.io/integrations/unifi/)

## API Keys
Network application, Integrations, Create New API Key. The key is shown **once**, so store it in a secrets manager. Use an environment variable in scripts.

## Integration API
From the official OpenAPI spec for Network 10.0.162:

BASE URL | USE
---|---
`https://<CONSOLE_IP>/proxy/network/integration` | Local, on the console
`https://api.ui.com/v1/connector/consoles/<CONSOLE_ID>/proxy/network/integration` | Via the cloud connector

```bash
curl -k -H "X-API-KEY: ${UNIFI_API_KEY}" \
  "https://<CONSOLE_IP>/proxy/network/integration/v1/sites"
```

PATH | RETURNS
---|---
`/v1/info` | Application info
`/v1/sites` | Sites
`/v1/sites/{siteId}/devices` | Devices
`/v1/sites/{siteId}/clients` | Clients

The `curl` example uses the header name from the Site Manager spec and a third-party local example. No official local `curl` was read. Use `-k` only for a self-signed console certificate, and prefer installing a proper certificate.

The cloud Site Manager API uses the `X-API-Key` header and is limited to 100 requests per minute per console.

Older scripts use `/api/login` and `/proxy/network/api/s/default/...`. These are the unofficial controller paths and can change without notice. Prefer the Integration API.

## Terraform
`paultyng/unifi` is archived. Active forks on the registry include `filipowm/unifi`, `ubiquiti-community/unifi` and `akerl/unifi`. The `filipowm` provider:

```hcl
terraform {
  required_providers {
    unifi = {
      source = "filipowm/unifi"
    }
  }
}

provider "unifi" {
  api_url        = "https://<CONSOLE_IP>"
  api_key        = var.unifi_api_key
  allow_insecure = false
}
```

- API key auth needs controller 9.0.108 or newer. Username and password also work.
- Environment variables: `UNIFI_API_KEY`, `UNIFI_USERNAME`, `UNIFI_PASSWORD`, `UNIFI_API`, `UNIFI_INSECURE`.
- Resources include `unifi_network` and `unifi_wlan`. Apply from a wired connection so a WiFi change cannot lock you out.
- `filipowm` v1.0.0 may need state edits when migrating from the original provider.

See [Terraform](../tools/terraform.md).

## Home Assistant
INTEGRATION | NOTES
---|---
UniFi Network | Needs a local user, not an SSO cloud user. Fields: host, username, password, port (default 443), Verify SSL, Site ID. Early Access and Release Candidate builds are not supported. Presence timeout defaults to 300 seconds
UniFi Protect | Needs Protect 7.2.105 or newer and an API key. Live feeds use RTSPS

See [Home Assistant](../apps/home-assistant.md).

## Unpoller
Exports UniFi metrics to Prometheus or InfluxDB ([Prometheus](../apps/prometheus.md), [Grafana](../apps/grafana.md)). Image: `ghcr.io/unpoller/unpoller`, config file at `/etc/unpoller/up.conf`.

VARIABLE | DEFAULT OR NOTE
---|---
`UP_UNIFI_DEFAULT_URL` | `https://127.0.0.1:8443`
`UP_UNIFI_DEFAULT_USER` | `unifipoller`
`UP_UNIFI_DEFAULT_PASS` | Empty
`UP_UNIFI_DEFAULT_API_KEY` | Used instead of user and password
`UP_PROMETHEUS_HTTP_LISTEN` | `0.0.0.0:9130`
`UP_PROMETHEUS_DISABLE` | `false`
`UP_INFLUXDB_DISABLE` | `false`
`UP_INFLUXDB_URL` | `http://127.0.0.1:8086`

- UniFi OS consoles use port 443, so do not append `:8443` to the URL.
- Remote mode uses `UP_UNIFI_REMOTE=true` and `UP_UNIFI_REMOTE_API_KEY`.
- Unpoller can also ship to Loki ([Loki and Alloy](../apps/loki-alloy.md)). Its variables were **not verified**.
- Create a read-only local user for it.

## Not Verified
Official local `curl` example, the Loki settings, and full Integration API endpoint coverage.

## See Also
- [UniFi](unifi.md)
- [Terraform](../tools/terraform.md)
- [Home Assistant](../apps/home-assistant.md)
- [Prometheus](../apps/prometheus.md)
