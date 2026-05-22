# ha-thiink

Unofficial Home Assistant integration for the [Thiink](https://thiink.io) Control Unit (CU) — a local energy management device that controls battery inverters based on spot prices.

> **Disclaimer:** This project is not affiliated with, endorsed by, or connected to Thiink in any way. It is an independent, community-built integration that uses the device's undocumented local HTTP API.

## Features

- Polls the CU's local HTTP API — no cloud dependency
- 22 sensors covering grid, battery, PV, load, and cabinet environment
- Per-phase grid measurements (voltage, current, power) for three-phase installations
- Grid energy import/export counters compatible with the HA Energy Dashboard
- Two polling intervals: EMS data every 10 s, device status every 60 s

## Installation

1. Copy `custom_components/thiink/` into your Home Assistant config's `custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Integrations → Add Integration** and search for **Thiink**.
4. Enter the hostname or IP address of your Thiink Control Unit.

## Sensors

| Entity | Unit | Notes |
|--------|------|-------|
| Grid Power | W | Negative = export |
| Grid L1/L2/L3 Power | W | |
| Grid L1/L2/L3 Voltage | V | |
| Grid L1/L2/L3 Current | A | |
| Grid Energy Import | Wh | Cumulative |
| Grid Energy Export | Wh | Cumulative |
| PV Power | W | From inverter via Modbus |
| Battery Power | W | |
| Battery State of Charge | % | |
| Battery Voltage | V | |
| Battery Capacity | kWh | |
| Load Power | W | |
| Inverter Temperature | °C | |
| Battery Temperature | °C | |
| Cabinet Temperature | °C | Internal CU sensor |
| Cabinet Humidity | % | Internal CU sensor |

## Requirements

- Home Assistant 2024.1 or later
- Thiink Control Unit on your local network (reachable by HTTP)
- No cloud account or internet access required for the integration

## Structure

```
custom_components/thiink/
├── pythiink/       # Pure Python API client (no HA dependency)
└── ...             # HA integration code
```

`pythiink/` is kept as a self-contained library with no Home Assistant dependencies so it can be published separately in the future.

## License

MIT License — see [LICENSE](LICENSE).
