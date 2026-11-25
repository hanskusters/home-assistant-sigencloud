# home-assistant-sigencloud

A custom [Home Assistant](https://www.home-assistant.io/) integration for the
**SigenCloud** platform, exposing your Sigenergy solar / battery / energy system
as sensors and devices in Home Assistant.

## Installation

1. Copy the `custom_components/sigencloud` folder into your Home Assistant
   `config/custom_components/` directory (or install via HACS as a custom
   repository).
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for
   **SigenCloud**.

## Entities

| Entity | Type | Description |
| --- | --- | --- |
| Spike loads | sensor | Number of scheduled spike loads (list in attributes) |
| Manual control | select | `Off`, `Charge`, `Discharge`, `Hold`, `Self-consumption` |
| Manual control end time | sensor | When the active manual control ends |
| Manual control duration | number (config) | Minutes used when a manual control mode is selected |
| Manual control power limit | number (config) | kW used when a mode is selected; `0` = no limitation |
| Battery max charging power | number | kW; `unknown` means "depends on system" |
| Battery max discharging power | number | kW; `unknown` means "depends on system" |
| Reset charging limit | button | Set charging limit back to "depends on system" |
| Reset discharging limit | button | Set discharging limit back to "depends on system" |
| Clear spike loads | button | Remove all scheduled spike loads |

The services (`sigencloud.manual_control`, `sigencloud.set_battery_power_limit`, …)
remain available for automations.

## Disclaimer

This is an **unofficial** integration. It is not affiliated with, authorized,
maintained, sponsored, or endorsed by Sigenergy or any of its affiliates.
"SigenCloud" and "Sigenergy" are trademarks of their respective owners. The
integration relies on Sigenergy's cloud API, which may change or break at any
time. Use at your own risk.

## License

Released under the [MIT License](LICENSE). Copyright (c) 2026 Hans Kusters.
