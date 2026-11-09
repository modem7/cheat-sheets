# ESPHome
ESPHome turns ESP32 and ESP8266 boards into smart home devices from a YAML file. It compiles and flashes firmware that talks to [Home Assistant](home-assistant.md) over an encrypted native API. These notes follow the 2026.10 documentation.

Documentation: [esphome.io](https://esphome.io/)

## Install
COMMAND | DESCRIPTION
---|---
`pip install esphome` | CLI only (Python 3.12 or newer, use a virtual environment)
`pip install "esphome-device-builder[esphome]"` then `esphome-device-builder config` | Web UI plus CLI, UI on `http://localhost:6052` (`config` is your config directory)
`docker run --rm --net=host -v "${PWD}":/config -it ghcr.io/esphome/esphome` | Docker. On Docker Desktop use `-p 6052:6052` instead of `--net=host`

In Home Assistant, install the "ESPHome Device Builder" app from Settings, Apps. If it is missing, add `https://github.com/esphome/home-assistant-addon` as a repository. `esphome dashboard` was removed in favour of Device Builder. `uv tool install esphome` was not on the install page, so it is unverified.

## CLI
Format: `esphome [OPTIONS] <COMMAND> <CONFIG...>`

COMMAND | DESCRIPTION
---|---
`esphome wizard <NAME>.yaml` | Interactive new device
`esphome config <NAME>.yaml` | Validate and print the resolved config (`--show-secrets`, `--no-defaults`)
`esphome compile <NAME>.yaml` | Build (`--only-generate` writes code only)
`esphome run <NAME>.yaml` | Compile, upload and show logs
`esphome run <NAME>.yaml --device <PORT_OR_IP>` | Choose serial port or network target (repeatable, `OTA` also accepted)
`esphome upload <NAME>.yaml` | Flash without compiling again (`--device`, `--file`)
`esphome logs <NAME>.yaml` | Stream logs (`--device`, `--reset`)
`esphome clean <NAME>.yaml` | Delete build files
`esphome clean-mqtt <NAME>.yaml` | Clear retained MQTT messages (`--topic`)
`esphome version` | Show version
`esphome -s name my_device01 config <NAME>.yaml` | Override a substitution from the command line

Global options include `-v`, `-q`, `-s KEY VALUE` and `--toolchain`. Other commands exist (`config-hash`, `clean-all`, `analyze-memory`, `bundle`, `update-all`) but were only listed. `esphome vscode` and `esphome rename` were not confirmed.

## First Flash
The very first install has to be over USB. After that updates are wireless.

```bash
esphome run livingroom.yaml
```

With the device plugged in, pick the serial port when asked. Home Assistant usually discovers it through mDNS. Otherwise use Add Integration, ESPHome and enter `<NAME>.local` or the IP.

## Minimal Config
```yaml
esphome:
  name: livingroom

esp32:
  variant: esp32s3
  framework:
    type: esp-idf

logger:

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "Livingroom Fallback Hotspot"
    password: !secret wifi_ap_password

captive_portal:
```

- Names use lowercase letters, digits and hyphens only.
- The API key is a 32-byte base64 string. Without a key, encryption is not used.
- `esp-idf` is the default framework. Arduino works only on ESP32, C3, S2 and S3, and newer chips (C2, C5, C6, H2, P4) need ESP-IDF.
- ESP8266 uses `esp8266: board: nodemcuv2` with `framework: version: recommended`. `esp01_1m` is the generic fallback.
- Since 2024.6.0 `ota:` must name a platform, so `- platform: esphome` is required.

## Secrets
Put values in `secrets.yaml` next to the config and use `!secret wifi_ssid`. Use hyphens, not underscores, in names where the docs say so. To share Home Assistant's file, add `<<: !include ../secrets.yaml` inside ESPHome's `secrets.yaml`. Keep `secrets.yaml` out of Git.

## Behaviour to Know
SETTING | DEFAULT OR EFFECT
---|---
`api` `reboot_timeout` | 15 minutes without a client, then reboot (`0s` disables). Remove `api:` or set `0s` when using MQTT only
`wifi` `ap_timeout` | 90 seconds. The captive portal starts after 1 minute of failed WiFi
`ota` esphome | Port 3232 (ESP32) or 8266 (ESP8266)
`safe_mode` | Own component. After repeated failed boots only logging, network and OTA run
`web_server` | `version: 2` is the default. Add `auth:` for a login. Basic auth changes to digest in 2027.1.0
`mdns` | Do not disable it unless you use fixed addresses, or auto-discovery breaks
`prometheus` | Needs `web_server:`, metrics at `<IP>/metrics`

## Components
```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

sensor:
  - platform: bme280_i2c
    address: 0x76
    temperature:
      name: "Temperature"
    update_interval: 60s
  - platform: dht
    pin: GPIO4
    model: DHT22
    temperature:
      name: "DHT Temperature"
  - platform: adc
    pin: GPIO34
    name: "Battery"
    attenuation: auto

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode:
        input: true
        pullup: true
      inverted: true
    name: "Door"

switch:
  - platform: gpio
    pin: GPIO16
    name: "Relay"

time:
  - platform: sntp
```

- `bme280_i2c` defaults to address `0x77` and needs `i2c`.
- `i2c` scans on start by default and uses a 50 kHz frequency unless set.
- `spi` takes `clk_pin`, `mosi_pin` and `miso_pin`, and each device takes `cs_pin`.
- `deep_sleep` takes `run_duration` and `sleep_duration`. ESP8266 needs GPIO16 wired to RST.
- `status_led` takes a `pin`.
- The pin numbers above are examples. Check your board's pinout.

## Reuse
FEATURE | EXAMPLE
---|---
Substitutions | `${name}`, set in a `substitutions:` block
Include | `!include common/wifi.yaml` (with `file:` and `vars:`)
Packages | `packages: wifi: !include common/wifi.yaml`, or `github://user/repo/file.yml@main`
External components | `external_components: - source: github://esphome/esphome@dev` with `components: [<NAME>]`

Remote packages cannot use `!secret`.

## Chip and Pin Notes
- ESP8266 strapping pins: GPIO0, GPIO2 and GPIO15 set the boot mode. GPIO16 is the deep sleep wake pin.
- ESP32: do not hold strapping pins low at boot, GPIO34 to 39 are input only, and GPIO0 sets the boot mode.
- ESP32-C3 and S3: the logger defaults to the USB serial JTAG port.

## Breaking Changes
- 2024.6.0: `ota` became a platform component, and safe mode is separate.
- 2026.10.0: `light` `restore_mode` was replaced by `restore_state`, and the native Arduino toolchain is the default for ESP8266.

Read the changelog before updating many devices. Earlier releases were not read.

## Not Verified
Lambdas, the web flasher, ESP32-C3 and S3 pin lists, and the full ESP32 options page (the fetch was truncated).

## See Also
- [Home Assistant](home-assistant.md)
- [Notification Services](../homelab/notification-services.md)
- [Cron](../misc/cron.md)
